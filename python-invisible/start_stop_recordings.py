import time
import requests


def get_ip_address(base_url):
    api_endpoint_status = "/status"
    response = requests.get(base_url + api_endpoint_status)
    if response.status_code == 200:
        for sensor in response.json()["result"]:
            if sensor["model"] == "Phone":
                ip_address = sensor["data"]["ip"]
                break
        else:
            # could not find phone's IP address
            return base_url
        base_url = f"http://{ip_address}:{port}/api"
        return base_url
    else:
        print(response.json())
        exit(1)


if __name__ == "__main__":
    host_name = "pi.local"
    port = 8080
    base_url = f"http://{host_name}:{port}/api"

    # optional: get ip address to avoid DNS resolution
    base_url = get_ip_address(base_url)

    api_endpoint_rec_start = "/recording:start"
    response = requests.post(base_url + api_endpoint_rec_start)
    print(response.json())

    time.sleep(5)

    api_endpoint_rec_stop_and_save = "/recording:stop_and_save"
    # api_endpoint_rec_start_cancel = "/recording:cancel"  # use for canceling
    response = requests.post(base_url + api_endpoint_rec_stop_and_save)
    print(response.json())
