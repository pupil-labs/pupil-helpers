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

addr = "127.0.0.1"

if __name__ == "__main__":
    from time import sleep, time

    # Setup zmq context and remote helper
    ctx = zmq.Context()
    socket = zmq.Socket(ctx, zmq.REQ)
    socket.connect("tcp://{}:50020".format(addr))

    socket.send_string("SUB_PORT")
    sub_port = socket.recv_string()
    sub = ctx.socket(zmq.SUB)
    sub.connect("tcp://{}:{}".format(addr, sub_port))
    sub.setsockopt_string(zmq.SUBSCRIBE, "notify.pupil_detector.properties")
    sleep(0.2)

    def notify(notification):
        """Sends ``notification`` to Pupil Remote"""
        topic = "notify." + notification["subject"]
        payload = serializer.dumps(notification, use_bin_type=True)
        socket.send_string(topic, flags=zmq.SNDMORE)
        socket.send(payload)
        return socket.recv_string()

    def recv_sub():
        """Recv a message with topic, payload."""
        topic = sub.recv_string()
        payload_serialized = sub.recv()
        payload = serializer.loads(payload_serialized, encoding="utf-8")
        return topic, payload

    def test_malformed_notifications():
        notify(
            {  # Test missing detector specification handling
                "subject": "pupil_detector.set_property",
                "name": "coarse_detection",
                "value": False,
            }
        )

        notify(
            {  # Test missing `name` field handling
                "subject": "pupil_detector.set_property.2d",
                "value": False,
                "target": "eye0",
            }
        )
        notify(
            {  # Test missing `value` field handling
                "subject": "pupil_detector.set_property.2d",
                "name": "coarse_detection",
                "target": "eye1",
            }
        )

    def test_invalid_notification_values():
        notify(
            {  # Test missing non-existend property handling
                "subject": "pupil_detector.set_property.2d",
                "name": "non_existend_property",
                "value": False,
                "target": "eye0",
            }
        )
        notify(
            {  # Test wrongly typed property value handling
                "subject": "pupil_detector.set_property.2d",
                "name": "coarse_detection",
                "value": "False",  # should be boolean, not str
                "target": "eye1",
            }
        )

    def test_valid_notification():
        notify(
            {
                "subject": "pupil_detector.set_property.2d",
                "name": "coarse_detection",
                "value": False,
                "target": "eye1",
            }
        )
        notify(
            {
                "subject": "pupil_detector.set_property.3d",
                "name": "model_sensitivity",
                "value": 0.9999,
            }
        )

    def test_current_properties():
        notify({"subject": "pupil_detector.broadcast_properties", "target": "eye0"})
        topic, properties = recv_sub()
        print(topic, properties)

    test_malformed_notifications()
    test_invalid_notification_values()
    test_valid_notification()
    test_current_properties()
