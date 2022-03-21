import asyncio
import base64
import contextlib
import datetime
import logging
import struct
import typing as T

import av
import cv2
import numpy as np
import requests
from aiortsp.rtcp.parser import SR
from aiortsp.rtsp.reader import RTSPReader

from nal_unit import extract_payload_from_nal_unit

logger = logging.getLogger(__name__)


def main():
    host_name = "pi.local"
    port = 8080
    base_url = f"http://{host_name}:{port}/api"
    api_endpoint_status = "/status"
    logger.info("Getting stream information...")
    try:
        status_response = requests.get(base_url + api_endpoint_status)
    except requests.exceptions.ConnectionError as err:
        logger.error(f"Could not connect to server {base_url} ({err})")
        exit(1)
    rtsp_url_world = get_rtsp_url(status_response, "world")
    rtsp_url_gaze = get_rtsp_url(status_response, "gaze")

    if not rtsp_url_gaze:
        logger.error("PI glasses not connected (or OTG disabled)")
        exit(1)

    if not rtsp_url_world:
        logger.error("World camera not connected (or OTG disabled)")
        exit(1)

    with contextlib.suppress(KeyboardInterrupt):
        asyncio.run(run_overlay(rtsp_url_world, rtsp_url_gaze))


async def run_overlay(rtsp_url_world, rtsp_url_gaze):
    should_terminate = asyncio.Event()
    queue_video = asyncio.Queue()
    queue_gaze = asyncio.Queue()
    await asyncio.gather(
        queue_results_until(
            queue_video,
            receive_scene_camera_video(rtsp_url_world),
            should_terminate,
        ),
        queue_results_until(queue_gaze, receive_gaze(rtsp_url_gaze), should_terminate),
        overlay_video_with_gaze(queue_video, queue_gaze, should_terminate),
    )


async def overlay_video_with_gaze(queue_video, queue_gaze, should_terminate):
    while True:
        video_datetime, video_frame = await get_most_recent_item(queue_video)
        gaze_datetime, gaze_point = await get_closest_item(queue_gaze, video_datetime)

        time_delta = abs(video_datetime - gaze_datetime)

        bgr_buffer = video_frame.to_ndarray(format="bgr24")
        draw_gaze(bgr_buffer, gaze_point)
        _, y = draw_text(bgr_buffer, f"Video: {video_datetime}", loc_y=50)
        _, y = draw_text(bgr_buffer, f"Gaze: {gaze_datetime}", loc_y=y + 10)
        _, y = draw_text(bgr_buffer, f"Delta: {time_delta}", loc_y=y + 10)

        cv2.imshow("Scene Camera", bgr_buffer)
        if cv2.waitKey(1) & 0xFF == 27:
            should_terminate.set()
            return


async def get_most_recent_item(queue):
    item = await queue.get()
    while True:
        try:
            next_item = queue.get_nowait()
        except asyncio.QueueEmpty:
            return item
        else:
            item = next_item


async def get_closest_item(queue, timestamp):
    item_ts, item = await queue.get()
    # assumes monotonically increasing timestamps
    if item_ts > timestamp:
        return item_ts, item
    while True:
        try:
            next_item_ts, next_item = queue.get_nowait()
        except asyncio.QueueEmpty:
            return item_ts, item
        else:
            if next_item_ts > timestamp:
                return next_item_ts, next_item
            item_ts, item = next_item_ts, next_item


def draw_gaze(bgr_buffer, gaze_point):
    x = int(gaze_point.x)
    y = int(gaze_point.y)
    cv2.circle(bgr_buffer, (x, y), radius=80, color=(0, 0, 255), thickness=15)


def draw_text(frame, frame_txt, loc_x=10, loc_y=10):
    frame_txt_font_name = cv2.FONT_HERSHEY_SIMPLEX
    frame_txt_font_scale = 1.0
    frame_txt_thickness = 1

    frame_txt_size = cv2.getTextSize(
        frame_txt, frame_txt_font_name, frame_txt_font_scale, frame_txt_thickness
    )[0]

    frame_txt_loc = loc_x, loc_y

    cv2.putText(
        frame,
        frame_txt,
        frame_txt_loc,
        frame_txt_font_name,
        frame_txt_font_scale,
        (255, 255, 255),
        thickness=frame_txt_thickness,
        lineType=cv2.LINE_8,
    )

    return loc_x + frame_txt_size[0], loc_y + frame_txt_size[1]


async def queue_results_until(
    queue: asyncio.Queue, generator: T.AsyncGenerator, event: asyncio.Event = None
):
    async for result in generator:
        try:
            queue.put_nowait(result)
        except asyncio.QueueFull:
            logger.warning(f"Queue full, dropping results from {generator}")
        if event is not None and event.is_set():
            break


async def receive_scene_camera_video(url):
    codec = None
    key_frame_seen = False
    async with WallclockRTSPReader(url) as reader:
        frame_datetime = None
        async for pkt in reader.iter_packets():
            if not codec:
                attributes = reader.session.sdp["medias"][0]["attributes"]
                rtpmap = attributes["rtpmap"]
                encoding = rtpmap["encoding"].lower()
                codec = av.CodecContext.create(encoding, "r")

                sprop_parameter_sets = attributes["fmtp"]["sprop-parameter-sets"]
                params = [
                    base64.b64decode(param) for param in sprop_parameter_sets.split(",")
                ]
                for param in params:
                    codec.parse(extract_payload_from_nal_unit(param))

            # if pkt is the start of a new fragmented frame, parse will return a packet
            # containing the data from the previous fragments
            for packet in codec.parse(extract_payload_from_nal_unit(pkt.data)):
                # use timestamp of previous packets
                key_frame_seen = key_frame_seen or packet.is_keyframe
                for frame in codec.decode(packet):
                    if frame_datetime:
                        yield frame_datetime, frame

            # Timestamps are not explicitly encoded in the packet payload. Instead, we
            # use the RTSP built-in timestamping
            try:
                timestamp_seconds = reader.absolute_timestamp_from_packet(pkt)
            except UnknownClockoffsetError:
                # The absolute timestamp is not known yet.
                # Waiting for the first RTCP SR packet...
                continue
            # Convert Unix timestamp to datetime
            frame_datetime = datetime.datetime.fromtimestamp(timestamp_seconds)
            # Convert Unix timestamp from seconds to nanoseconds
            # timestamp_nanoseconds = int(timestamp_seconds * 10 ** 9)


async def receive_gaze(url):
    expected_encoding = "com.pupillabs.gaze1"
    async with WallclockRTSPReader(url) as reader:
        async for pkt in reader.iter_packets():
            # Timestamps are not explicitly encoded in the packet payload. Instead, we
            # use the RTSP built-in timestamping
            rtpmap = reader.session.sdp["medias"][0]["attributes"]["rtpmap"]
            if rtpmap["encoding"] != expected_encoding:
                raise ValueError(
                    f"Unexpected gaze encoding '{rtpmap['encoding']}' "
                    f"(expected '{expected_encoding}')"
                )
            try:
                timestamp_seconds = reader.absolute_timestamp_from_packet(pkt)
            except UnknownClockoffsetError:
                # The absolute timestamp is not known yet.
                # Waiting for the first RTCP SR packet...
                continue
            # Convert Unix timestamp to datetime
            gaze_datetime = datetime.datetime.fromtimestamp(timestamp_seconds)
            # Convert Unix timestamp from seconds to nanoseconds
            # timestamp_nanoseconds = int(timestamp_seconds * 10 ** 9)

            # Gaze data contains two big-endian floats for the pixel location and a
            # single byte indicating whether the user is wearing the device.
            x, y, worn = struct.unpack("!ffB", pkt.data)
            yield gaze_datetime, GazePoint(x, y, worn == 255)


def get_rtsp_url(status_response, sensor_name):
    ip = _get_phone_ip_address(status_response)
    for sensor in status_response.json()["result"]:
        if (
            sensor["model"] == "Sensor"
            and sensor["data"]["conn_type"] == "DIRECT"
            and sensor["data"]["sensor"] == sensor_name
            and sensor["data"]["connected"]
        ):
            protocol = sensor["data"]["protocol"]
            port = sensor["data"]["port"]
            params = sensor["data"]["params"]
            return f"{protocol}://{ip}:{port}/?{params}"


def _get_phone_ip_address(status_response):
    for sensor in status_response.json()["result"]:
        if sensor["model"] == "Phone":
            return sensor["data"]["ip"]


class UnknownClockoffsetError(Exception):
    pass


class WallclockRTSPReader(RTSPReader):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._relative_to_ntp_clock_offset = None

    def handle_rtcp(self, rtcp):
        for pkt in rtcp.packets:
            if isinstance(pkt, SR):
                self._calculate_clock_offset(pkt)

    def absolute_timestamp_from_packet(self, packet):
        """Returns the Unix epoch timestamp for the input packet

        Uses the cached clock offset between the NTP and relative timestamp provided
        by the RTCP packets.
        """
        try:
            return (
                self.relative_timestamp_from_packet(packet)
                + self._relative_to_ntp_clock_offset
            )
        except TypeError:
            # self._relative_to_ntp_clock_offset is still None
            raise UnknownClockoffsetError(
                "Clock offset between relative and NTP clock is still unknown. "
                "Waiting for first RTCP SR packet..."
            )

    def relative_timestamp_from_packet(self, packet):
        rtpmap = self.session.sdp["medias"][0]["attributes"]["rtpmap"]
        clock_rate = rtpmap["clockRate"]
        return packet.ts / clock_rate

    def _calculate_clock_offset(self, sr_pkt):
        # Expected input: aiortsp.rtcp.parser.SR packet which converts the raw NTP
        # timestamp [1] from seconds since 1900 to seconds since 1970 (unix epoch)
        # [1] see https://datatracker.ietf.org/doc/html/rfc3550#section-6.4.1

        self._relative_to_ntp_clock_offset = (
            sr_pkt.ntp - self.relative_timestamp_from_packet(sr_pkt)
        )


class GazePoint(T.NamedTuple):
    x: float
    y: float
    worn: bool


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    main()
