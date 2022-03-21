import pprint
import requests

if __name__ == "__main__":
    base_url = "http://pi.local:8080/api"
    api_endpoint_status = "/status"
    response_status = requests.get(base_url + api_endpoint_status)
    # pprint formats output. Use print() for unformatted output
    pprint.pprint(response_status.json())
