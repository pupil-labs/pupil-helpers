import os
import cv2
import requests


def main():
    host_name = "pi.local"
    port = 8080
    base_url = f"http://{host_name}:{port}/api"
    api_endpoint_status = "/status"
    try:
        status_response = requests.get(base_url + api_endpoint_status)
    except requests.exceptions.ConnectionError as err:
        print(f"Could not connect to server {base_url} ({err})")
        return
    world_rtsp_url = get_world_rtsp_url(status_response)
    if not world_rtsp_url:
        print(
            "Could not find world stream. "
            "Glasses or scene camera might not be connected."
        )
        return
        return
    first_frame = True
    for frame in yield_frames_from_url(world_rtsp_url):
        if first_frame:
            print("Hit ESC to stop streaming")
            first_frame = False
        cv2.imshow("frame", frame)
        # press esc to exit
        if cv2.waitKey(1) & 0xFF == 27:
            break


def get_world_rtsp_url(status_response):
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


def yield_frames_from_url(url):
    # Pupil Invisible Companion uses udp for streaming. cv2 defaults to tcp.
    os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;udp"

    print(f"Connecting to stream at {url}")
    cap = cv2.VideoCapture(url)
    print("Waiting for frames")
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Stream ended")
            break
        yield frame


def _get_phone_ip_address(status_response):
    for sensor in status_response.json()["result"]:
        if sensor["model"] == "Phone":
            return sensor["data"]["ip"]


if __name__ == "__main__":
    main()
