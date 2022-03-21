import asyncio
import contextlib
import datetime
import struct

import requests
from aiortsp.rtsp.reader import RTSPReader
from aiortsp.rtcp.parser import SR


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
    gaze_rtsp_url = get_gaze_rtsp_url(status_response)
    print(f"Connecting to {gaze_rtsp_url}...")

    with contextlib.suppress(KeyboardInterrupt):
        asyncio.run(receive_gaze(gaze_rtsp_url))


async def receive_gaze(url):
    async with WallclockRTSPReader(url) as reader:
        async for pkt in reader.iter_packets():
            # Timestamps are not explicitly encoded in the packet payload. Instead, we
            # use the RTSP built-in timestamping
            rtpmap = reader.session.sdp["medias"][0]["attributes"]["rtpmap"]
            if rtpmap["encoding"] != "com.pupillabs.gaze1":
                continue
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

            print(
                f"[{gaze_datetime}] Gaze at [{x:.02f}, {y:.02f}] (worn: {worn == 255})"
            )


def get_gaze_rtsp_url(status_response):
    ip = _get_phone_ip_address(status_response)
    for sensor in status_response.json()["result"]:
        if (
            sensor["model"] == "Sensor"
            and sensor["data"]["conn_type"] == "DIRECT"
            and sensor["data"]["sensor"] == "gaze"
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
