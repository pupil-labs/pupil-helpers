"""
Receive data from Pupil server broadcast over TCP
test script to see what the stream looks like
and for debugging  
"""
import zmq
 
#network setup
port = "5000"
context = zmq.Context()
socket = context.socket(zmq.SUB)
socket.connect("tcp://127.0.0.1:"+port)
#filter by messages by stating string 'STRING'. '' receives all messages
socket.setsockopt(zmq.SUBSCRIBE, '')

# in this example the surface is named 'screen'. Replace with your surface name.
surface_name = 'screen'
 
while True:
    msg = socket.recv()

    items = msg.split("\n") 
    msg_type = items.pop(0)
    items = dict([i.split(':',1) for i in items[:-1] ])
    
    if msg_type == 'Gaze':
        try:
            gp = items['realtime gaze on '+surface_name]
            gp_x, gp_y = map(float,gp[1:-1].split(','))
            if (0<= gp_x <=1 and 0<= gp_y <=1):
                print "gaze on surface: %s\t - normalized coords: %s, %s" %(surface_name, gp_x, gp_y)
        except KeyError:
            pass
    else:
        # process non gaze position events from plugins here
        pass