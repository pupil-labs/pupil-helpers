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
sub.setsockopt(zmq.SUBSCRIBE, 'surface')
surface_name = 'unnamed'

while True:
    topic,msg =  sub.recv_multipart()
    surface = loads(msg)
    try:
        if surface["name"] != surface_name:
            continue
        coords = surface["gaze_on_srf"]
        for coord in coords:
            gp_x, gp_y = coord
            if (0<= gp_x <=1 and 0<= gp_y <=1):
                print "gaze on surface: %s\t - normalized coords: %s, %s" %(surface_name, gp_x, gp_y)
    except KeyError:
        pass
