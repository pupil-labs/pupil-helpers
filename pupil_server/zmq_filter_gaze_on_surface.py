"""
Receive data from Pupil server broadcast over TCP
test script to see what the stream looks like
and for debugging
"""
import zmq
import json

#network setup
port = "5000"
context = zmq.Context()
socket = context.socket(zmq.SUB)
socket.connect("tcp://127.0.0.1:"+port)
#filter by messages by stating string 'STRING'. '' receives all messages
socket.setsockopt(zmq.SUBSCRIBE, 'gaze_positions')
surface_name = 'unnamed'

while True:
    topic,msg =  socket.recv_multipart()
    gaze_positions = json.loads(msg)
    for gaze_position in gaze_positions:
        try:
            gp_x, gp_y = gaze_position["realtime gaze on "+surface_name]
            if (0<= gp_x <=1 and 0<= gp_y <=1):
                print "gaze on surface: %s\t - normalized coords: %s, %s" %(surface_name, gp_x, gp_y)
        except KeyError:
            pass