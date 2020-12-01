"""
(*)~----------------------------------------------------------------------------------
 Pupil Helpers
 Copyright (C) 2012-2016  Pupil Labs

 Distributed under the terms of the GNU Lesser General Public License (LGPL v3.0).
 License details are in the file license.txt, distributed as part of this software.
----------------------------------------------------------------------------------~(*)
"""

import zmq
import msgpack as serializer
import typing as T
from pprint import pprint


class PupilDetectorNetworkApi:
    def __init__(self, host="127.0.0.1", port=50020):
        self.ctx = zmq.Context()

        self.req_socket = zmq.Socket(self.ctx, zmq.REQ)
        self.req_socket.connect(f"tcp://{host}:{port}")

        self.req_socket.send_string("SUB_PORT")
        sub_port = self.req_socket.recv_string()

        self.sub_socket = self.ctx.socket(zmq.SUB)
        self.sub_socket.connect(f"tcp://{host}:{sub_port}")
        self.sub_socket.setsockopt_string(
            zmq.SUBSCRIBE, "notify.pupil_detector.properties"
        )

    def send_req(self, payload: dict):
        topic = "notify." + payload["subject"]
        payload = serializer.dumps(payload, use_bin_type=True)

        self.req_socket.send_string(topic, flags=zmq.SNDMORE)
        self.req_socket.send(payload)
        _ = self.req_socket.recv_string()

    def recv_sub(self) -> T.Tuple[str, T.Any]:
        topic = self.sub_socket.recv_string()
        payload = self.sub_socket.recv()
        payload = serializer.loads(payload, encoding="utf-8")
        return topic, payload

    # Pupil Detector Plugin Network API

    def set_enabled(
        self,
        value: bool,
        detector_name: T.Optional[str] = None,
        eye_id: T.Optional[int] = None,
    ):
        # Construct the payload for set_enabled notification
        payload = {
            "subject": "pupil_detector.set_enabled",
            "value": value,
            "eye_id": eye_id,
            "detector_plugin_class_name": detector_name,
        }

        # Remove all values that are None
        payload = {k: v for k, v in payload.items() if v is not None}

        # Send set_enabled notification
        self.send_req(payload)

    def set_roi(
        self,
        value: T.Tuple[int, int, int, int],
        detector_name: T.Optional[str] = None,
        eye_id: T.Optional[int] = None,
    ):
        # Construct the payload for set_roi notification
        payload = {
            "subject": "pupil_detector.set_roi",
            "value": value,
            "eye_id": eye_id,
            "detector_plugin_class_name": detector_name,
        }

        # Remove all values that are None
        payload = {k: v for k, v in payload.items() if v is not None}

        # Send set_roi notification
        self.send_req(payload)

    def set_properties(
        self,
        values: dict,
        detector_name: str,  # NOTE: required, since property names are specific to a given detector
        eye_id: T.Optional[int] = None,
    ):
        # Construct the payload for set_properties notification
        payload = {
            "subject": "pupil_detector.set_properties",
            "values": values,  # NOTE: key is plural, since the value is a dict of property values by name
            "eye_id": eye_id,
            "detector_plugin_class_name": detector_name,
        }

        # Remove all values that are None
        payload = {k: v for k, v in payload.items() if v is not None}

        # Send set_properties notification
        self.send_req(payload)

    def broadcast_properties(
        self,
        detector_name: T.Optional[str] = None,
        eye_id: T.Optional[int] = None,
    ):
        # Construct the payload for broadcast_properties notification
        payload = {
            "subject": "pupil_detector.broadcast_properties",
            "eye_id": eye_id,
            "detector_plugin_class_name": detector_name,
        }

        # Remove all values that are None
        payload = {k: v for k, v in payload.items() if v is not None}

        # Send broadcast_properties notification
        self.send_req(payload)


def pupil_detector_get_properties(
    api: PupilDetectorNetworkApi, detector_name: str, eye_id: int
):
    # Request property broadcast from a single detector running in a single eye process
    api.broadcast_properties(detector_name=detector_name, eye_id=eye_id)

    # Receive the property broadcast notification
    # Since the broadcast request was sent to a single detector running in a specific eye process
    # It is only expected to receive 1 broadcast response
    topic, payload = api.recv_sub()

    # Assert the response matches the requested (detector_name, eye_id) combination
    assert topic == f"notify.pupil_detector.properties.{eye_id}.{detector_name}", topic

    # Assert the received payload type
    assert isinstance(payload, dict), type(payload)

    return payload


if __name__ == "__main__":
    api = PupilDetectorNetworkApi()
    properties = pupil_detector_get_properties(
        api, detector_name="Detector2DPlugin", eye_id=0
    )
    pprint(properties)
