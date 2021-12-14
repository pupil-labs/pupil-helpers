import asyncio
import base64
import contextlib
import datetime

import av
import cv2
import requests
from aiortsp.rtcp.parser import SR
from aiortsp.rtsp.reader import RTSPReader

from nal_unit import extract_payload_from_nal_unit


def main():
    host_name = "pi.local"
    port = 8080
    base_url = f"http://{host_name}:{port}/api"
    api_endpoint_status = "/status"
    print("Getting stream information...")
    try:
        status_response = requests.get(base_url + api_endpoint_status)
    except requests.exceptions.ConnectionError as err:
        print(f"Could not connect to server {base_url} ({err})")
        exit(1)
    gaze_rtsp_url = get_scene_camera_rtsp_url(status_response)
    print(f"Connecting to {gaze_rtsp_url}...")

    with contextlib.suppress(KeyboardInterrupt):
        asyncio.run(receive_scene_camera_video(gaze_rtsp_url))


async def receive_scene_camera_video(url):
    codec = None
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
                print("Hit ESC to stop streaming")

            # if pkt is the start of a new fragmented frame, parse will return a packet
            # containing the data from the previous fragments
            for packet in codec.parse(extract_payload_from_nal_unit(pkt.data)):
                # use timestamp of previous packets
                for frame in codec.decode(packet):
                    bgr_buffer = frame.to_ndarray(format="bgr24")
                    draw_time(bgr_buffer, frame_datetime)
                    cv2.imshow("Scene Camera", bgr_buffer)
                    if cv2.waitKey(1) & 0xFF == 27:
                        return

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


def draw_time(frame, time):
    frame_txt_font_name = cv2.FONT_HERSHEY_SIMPLEX
    frame_txt_font_scale = 1.0
    frame_txt_thickness = 1

    # first line: frame index
    frame_txt = str(time)
    frame_txt_size = cv2.getTextSize(
        frame_txt, frame_txt_font_name, frame_txt_font_scale, frame_txt_thickness
    )[0]

    frame_txt_loc = (
        frame.shape[0] // 2 - frame_txt_size[0] // 2,
        frame.shape[1] // 2 - frame_txt_size[1],
    )

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


def get_scene_camera_rtsp_url(status_response):
    ip = _get_phone_ip_address(status_response)
    for sensor in status_response.json()["result"]:
        if (
            sensor["model"] == "Sensor"
            and sensor["data"]["conn_type"] == "DIRECT"
            and sensor["data"]["sensor"] == "world"
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


if __name__ == "__main__":
    main()
