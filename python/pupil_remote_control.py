"""
(*)~----------------------------------------------------------------------------------
 Pupil Helpers
 Copyright (C) 2012-2016  Pupil Labs

 Distributed under the terms of the GNU Lesser General Public License (LGPL v3.0).
 License details are in the file license.txt, distributed as part of this software.
----------------------------------------------------------------------------------~(*)
"""

"""
This example demonstrates how to send simple messages to the Pupil Remote plugin
    'R' start recording with auto generated session name
    'R rec_name' start recording and name new session name: rec_name
    'r' stop recording
    'C' start currently selected calibration
    'c' stop currently selected calibration
    'T 1234.56' Timesync: make timestamps count form 1234.56 from now on.
    't' get pupil timestamp
    '{notification}' send a notification via pupil remote.
"""

import zmq
import msgpack as serializer


if __name__ == "__main__":
    from time import sleep, time

    # Setup zmq context and remote helper
    ctx = zmq.Context()
    socket = zmq.Socket(ctx, zmq.REQ)
    socket.connect("tcp://127.0.0.1:50020")

    # Measure round trip delay
    t = time()
    socket.send_string("t")
    print(socket.recv_string())
    print("Round trip command delay:", time() - t)

    # set current Pupil time to 0.0
    socket.send_string("T 0.0")
    print(socket.recv_string())

    # start recording
    sleep(1)
    socket.send_string("R")
    print(socket.recv_string())

    sleep(5)
    socket.send_string("r")
    print(socket.recv_string())

    # send notification:
    def notify(notification):
        """Sends ``notification`` to Pupil Remote"""
        topic = "notify." + notification["subject"]
        payload = serializer.dumps(notification, use_bin_type=True)
        socket.send_string(topic, flags=zmq.SNDMORE)
        socket.send(payload)
        return socket.recv_string()

    # test notification, note that you need to listen on the IPC to receive notifications!
    notify({"subject": "calibration.should_start"})
    sleep(5)
    notify({"subject": "calibration.should_stop"})
