"""
Receive eye movement classification segments from Pupil using ZMQ.
"""
import zmq
from msgpack import loads


addr = "127.0.0.1"  # remote ip or localhost
req_port = "50020"  # same as in the pupil remote gui
context = zmq.Context()


# open a req port to talk to pupil
req = context.socket(zmq.REQ)
req.connect("tcp://{}:{}".format(addr, req_port))
print("- (i) Opened the REQ port: {}".format(req_port))


# ask for the sub port
req.send_string("SUB_PORT")
sub_port = req.recv_string()
print("- (i) Received info of the SUB port: {}".format(sub_port))


# open a sub port to listen to pupil
sub = context.socket(zmq.SUB)
sub.connect("tcp://{}:{}".format(addr, sub_port))
print("- (i) Opened the SUB port: {}".format(sub_port))


# subscribe to eye movement topics
sub.setsockopt_string(zmq.SUBSCRIBE, "eye_movement.")  # subscribe to all eye movement classifications
# sub.setsockopt_string(zmq.SUBSCRIBE, 'eye_movement.fixation')  # subscribe only to fixation classifications
# sub.setsockopt_string(zmq.SUBSCRIBE, 'eye_movement.saccade')  # subscribe only to saccade classifications
# sub.setsockopt_string(zmq.SUBSCRIBE, 'eye_movement.pso')  # subscribe only to post saccadic oscillations classifications
# sub.setsockopt_string(zmq.SUBSCRIBE, 'eye_movement.smooth_pursuit')  # subscribe only to smooth pursuit classifications


print("- (i) Starting the RECV loop:")
print("-----------------------------")
while True:
    try:
        topic = sub.recv_string()
        msg = sub.recv()
        msg = loads(msg, encoding="utf-8")

        # NOTE: For real-time eye movement, new messages might contain updated information for already received eye movement classification segments.
        print("\n{}: {}".format(topic, msg))
    except KeyboardInterrupt:
        break
