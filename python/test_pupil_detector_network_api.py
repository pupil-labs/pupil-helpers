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


if __name__ == "__main__":
    from time import sleep, time

    # Setup zmq context and remote helper
    ctx = zmq.Context()
    socket = zmq.Socket(ctx, zmq.REQ)
    socket.connect("tcp://127.0.0.1:50020")

    def notify(notification):
        """Sends ``notification`` to Pupil Remote"""
        topic = "notify." + notification["subject"]
        payload = serializer.dumps(notification, use_bin_type=True)
        socket.send_string(topic, flags=zmq.SNDMORE)
        socket.send(payload)
        return socket.recv_string()

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
            {  # Test wrongly typed property value handling
                "subject": "pupil_detector.set_property.2d",
                "name": "coarse_detection",
                "value": False,
                "target": "eye1",
            }
        )
        notify(
            {  # Test wrongly typed property value handling
                "subject": "pupil_detector.set_property.3d",
                "name": "model_sensitivity",
                "value": 0.9999,
            }
        )

    test_malformed_notifications()
    test_invalid_notification_values()
    test_valid_notification()
