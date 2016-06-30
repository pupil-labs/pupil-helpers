"""
Receive data from Pupil server broadcast over TCP
test script to see what the stream looks like
and for debugging
"""
import zmq
from msgpack import loads

context = zmq.Context()

#open a req port to talk to pupil
addr = '127.0.0.1' # remote ip or localhost
req_port = "50020" # same as in the pupil remote gui
req = context.socket(zmq.REQ)
req.connect("tcp://%s:%s" %(addr,req_port))
# ask for the sub port
req.send('SUB_PORT')
sub_port = req.recv()
# open a sub port to listen to pupil
sub = context.socket(zmq.SUB)
sub.connect("tcp://%s:%s" %(addr,sub_port))
sub.setsockopt(zmq.SUBSCRIBE, 'gaze')
surface_name = 'unnamed'

while True:
    topic,msg =  sub.recv_multipart()
    gaze_position = loads(msg)
    try:
        gp_x, gp_y = gaze_position["realtime gaze on "+surface_name]
        if (0<= gp_x <=1 and 0<= gp_y <=1):
            print "gaze on surface: %s\t - normalized coords: %s, %s" %(surface_name, gp_x, gp_y)
    except KeyError:
        pass