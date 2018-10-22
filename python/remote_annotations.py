"""
(*)~----------------------------------------------------------------------------------
 Pupil Helpers
 Copyright (C) 2012-2016  Pupil Labs

 Distributed under the terms of the GNU Lesser General Public License (LGPL v3.0).
 License details are in the file license.txt, distributed as part of this software.
----------------------------------------------------------------------------------~(*)
"""

"""
This example demonstrates how to send annotations via Pupil Remote
"""

import zmq
import msgpack as serializer


if __name__ == "__main__":
    from time import sleep, time

    # Setup zmq context and remote helper
    ctx = zmq.Context()
    socket = zmq.Socket(ctx, zmq.REQ)
    socket.connect("tcp://127.0.0.1:50020")

    # In order for the annotations to be correlated correctly with the rest of
    # the data it is required to change Pupil Capture's time base to this scripts
    # clock. We only set the time base once. Consider using Pupil Time Sync for
    # a more precise and long term time synchronization
    time_fn = time  # Use the appropriate time function here

    # Set Pupil Capture's time base to this scripts time. (Should be done before
    # starting the recording)
    socket.send_string("T {}".format(time_fn()))
    print(socket.recv_string())

    # send notification:
    def notify(notification):
        """Sends ``notification`` to Pupil Remote"""
        topic = "notify." + notification["subject"]
        payload = serializer.dumps(notification, use_bin_type=True)
        socket.send_string(topic, flags=zmq.SNDMORE)
        socket.send(payload)
        return socket.recv_string()

    def send_trigger(label, timestamp, duration=0., **custom_keys):
        minimal_trigger.update(custom_keys)
        return notify(minimal_trigger)

    # Start the annotations plugin
    notify({"subject": "start_plugin", "name": "Annotation_Capture", "args": {}})

    socket.send_string("R")
    socket.recv_string()

    sleep(1.)  # sleep for a few seconds, can be less

    # Send a trigger with the current time
    # The annotation will be saved to the pupil_data notifications if a
    # recording is running. The Annotation_Player plugin will automatically
    # retrieve, display and export all recorded annotations.
    label = "custom_annotation_label"
    duration = 0.
    minimal_trigger = {
        "subject": "annotation",
        "label": label,
        "timestamp": time_fn(),
        "duration": duration,
        "record": True,
    }
    notify(minimal_trigger)
    sleep(1.)  # sleep for a few seconds, can be less

    minimal_trigger = {
        "subject": "annotation",
        "label": label,
        "timestamp": time_fn(),
        "duration": duration,
        "record": True,
    }
    # add custom keys to your annotation
    minimal_trigger["custom_key"] = "custom value"
    notify(minimal_trigger)
    sleep(1.)  # sleep for a few seconds, can be less

    socket.send_string("r")
    socket.recv_string()
