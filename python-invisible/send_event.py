import time
import requests


if __name__ == "__main__":
    host_name = "pi.local"
    port = 8080
    base_url = f"http://{host_name}:{port}/api"

    api_endpoint_event = "/event"

    event_data = {"name": "event without timestamp"}
    print(f"Sending event: {event_data}")
    response = requests.post(base_url + api_endpoint_event, json=event_data)
    print(response.json())

    event_data = {
        "name": "event with nanosecond unix timestamp",
        "timestamp": time.time_ns(),  # optional: Unix timestamp in nanoseconds
    }
    print(f"Sending event: {event_data}")
    response = requests.post(base_url + api_endpoint_event, json=event_data)
    print(response.json())
