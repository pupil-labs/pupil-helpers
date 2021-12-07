import asyncio
import contextlib
import struct

import requests
from aiortsp.rtsp.reader import RTSPReader


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
    async with RTSPReader(url) as reader:
        async for pkt in reader.iter_packets():
            # Timestamps are not explicitly encoded in the packet payload. Instead, we
            # use the RTSP built-in timestamping
            rtpmap = reader.session.sdp["medias"][0]["attributes"]["rtpmap"]
            if rtpmap["encoding"] != "com.pupillabs.gaze1":
                continue
            clock_rate = rtpmap["clockRate"]
            relative_timestamps_seconds = pkt.ts / clock_rate

            # Gaze data contains two big-endian floats for the pixel location and a
            # single byte indicating whether the user is wearing the device.
            x, y, worn = struct.unpack("!ffB", pkt.data)

            print(
                f"[{relative_timestamps_seconds:.4f}] "
                f"Gaze at [{x:.02f}, {y:.02f}] (worn: {worn == 255})"
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


if __name__ == "__main__":
    main()
