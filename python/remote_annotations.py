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
    pupil_remote = zmq.Socket(ctx, zmq.REQ)
    pupil_remote.connect("tcp://127.0.0.1:50020")

    pupil_remote.send_string("PUB_PORT")
    pub_port = pupil_remote.recv_string()
    pub_socket = zmq.Socket(ctx, zmq.PUB)
    pub_socket.connect("tcp://127.0.0.1:{}".format(pub_port))

    # In order for the annotations to be correlated correctly with the rest of
    # the data it is required to change Pupil Capture's time base to this scripts
    # clock. We only set the time base once. Consider using Pupil Time Sync for
    # a more precise and long term time synchronization
    time_fn = time  # Use the appropriate time function here

    # Set Pupil Capture's time base to this scripts time. (Should be done before
    # starting the recording)
    pupil_remote.send_string("T {}".format(time_fn()))
    print(pupil_remote.recv_string())

    # send notification:
    def notify(notification):
        """Sends ``notification`` to Pupil Remote"""
        topic = "notify." + notification["subject"]
        payload = serializer.dumps(notification, use_bin_type=True)
        pupil_remote.send_string(topic, flags=zmq.SNDMORE)
        pupil_remote.send(payload)
        return pupil_remote.recv_string()

    def send_trigger(trigger):
        payload = serializer.dumps(trigger, use_bin_type=True)
        pub_socket.send_string(trigger["topic"], flags=zmq.SNDMORE)
        pub_socket.send(payload)

    # Start the annotations plugin
    notify({"subject": "start_plugin", "name": "Annotation_Capture", "args": {}})

    pupil_remote.send_string("R")
    pupil_remote.recv_string()

    sleep(1.)  # sleep for a few seconds, can be less

    # Send a trigger with the current time
    # The annotation will be saved to annotation.pldata if a
    # recording is running. The Annotation_Player plugin will automatically
    # retrieve, display and export all recorded annotations.

    def new_trigger(label, duration):
        return {
            "topic": "annotation",
            "label": label,
            "timestamp": time_fn(),
            "duration": duration,
        }

    label = "custom_annotation_label"
    duration = 0.
    minimal_trigger = new_trigger(label, duration)
    send_trigger(minimal_trigger)
    sleep(1.)  # sleep for a few seconds, can be less

    minimal_trigger = new_trigger(label, duration)
    send_trigger(minimal_trigger)

    # add custom keys to your annotation
    minimal_trigger["custom_key"] = "custom value"
    send_trigger(minimal_trigger)
    sleep(1.)  # sleep for a few seconds, can be less

    # stop recording
    pupil_remote.send_string("r")
    pupil_remote.recv_string()
