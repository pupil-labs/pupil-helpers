"""
Receive world camera data from Pupil using ZMQ.
Make sure the frame publisher plugin is loaded and confugured to gray or rgb
"""
import zmq
from msgpack import unpackb, packb
import numpy as np
import cv2

context = zmq.Context()
# open a req port to talk to pupil
addr = "127.0.0.1"  # remote ip or localhost
req_port = "50020"  # same as in the pupil remote gui
req = context.socket(zmq.REQ)
req.connect("tcp://{}:{}".format(addr, req_port))
# ask for the sub port
req.send_string("SUB_PORT")
sub_port = req.recv_string()


# send notification:
def notify(notification):
    """Sends ``notification`` to Pupil Remote"""
    topic = "notify." + notification["subject"]
    payload = packb(notification, use_bin_type=True)
    req.send_string(topic, flags=zmq.SNDMORE)
    req.send(payload)
    return req.recv_string()


# open a sub port to listen to pupil
sub = context.socket(zmq.SUB)
sub.connect("tcp://{}:{}".format(addr, sub_port))

# set subscriptions to topics
# recv just pupil/gaze/notifications
sub.setsockopt_string(zmq.SUBSCRIBE, "frame.")


def recv_from_sub():
    """Recv a message with topic, payload.

    Topic is a utf-8 encoded string. Returned as unicode object.
    Payload is a msgpack serialized dict. Returned as a python dict.

    Any addional message frames will be added as a list
    in the payload dict with key: '__raw_data__' .
    """
    topic = sub.recv_string()
    payload = unpackb(sub.recv(), raw=False)
    extra_frames = []
    while sub.get(zmq.RCVMORE):
        extra_frames.append(sub.recv())
    if extra_frames:
        payload["__raw_data__"] = extra_frames
    return topic, payload


recent_world = None
recent_eye0 = None
recent_eye1 = None


FRAME_FORMAT = "bgr"


# Set the frame format via the Network API plugin
notify({"subject": "frame_publishing.set_format", "format": FRAME_FORMAT})

try:
    while True:
        topic, msg = recv_from_sub()

        if topic.startswith("frame.") and msg["format"] != FRAME_FORMAT:
            print(
                f"different frame format ({msg['format']}); skipping frame from {topic}"
            )
            continue

        if topic == "frame.world":
            recent_world = np.frombuffer(
                msg["__raw_data__"][0], dtype=np.uint8
            ).reshape(msg["height"], msg["width"], 3)
        elif topic == "frame.eye.0":
            recent_eye0 = np.frombuffer(msg["__raw_data__"][0], dtype=np.uint8).reshape(
                msg["height"], msg["width"], 3
            )
        elif topic == "frame.eye.1":
            recent_eye1 = np.frombuffer(msg["__raw_data__"][0], dtype=np.uint8).reshape(
                msg["height"], msg["width"], 3
            )

        if (
            recent_world is not None
            and recent_eye0 is not None
            and recent_eye1 is not None
        ):
            cv2.imshow("world", recent_world)
            cv2.imshow("eye0", recent_eye0)
            cv2.imshow("eye1", recent_eye1)
            cv2.waitKey(1)
            pass  # here you can do calculation on the 3 most recent world, eye0 and eye1 images
except KeyboardInterrupt:
    pass
finally:
    cv2.destroyAllWindows()
