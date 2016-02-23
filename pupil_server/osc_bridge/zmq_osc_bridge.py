'''
a script that will replay pupil server messages to a osc server.

as implemented here only the pupil_norm_pos is relayed.
implementeing other messages to be send as well is a matter of renaming the vaiables.

installing pyOSC:

git clone git://gitorious.org/pyosc/devel.git pyosc
cd pyosc
python setup.py install (may need sudo)
'''


#zmq setup
import zmq
import json

context = zmq.Context()
socket = context.socket(zmq.SUB)
socket.connect("tcp://127.0.0.1:5000")
#filter by messages by stating string 'STRING'. '' receives all messages
socket.setsockopt(zmq.SUBSCRIBE, 'pupil_positions')

# #osc setup
from OSC import OSCClient, OSCMessage
client = OSCClient()
client.connect( ("localhost", 7110) )

while True:
    topic,msg =  socket.recv_multipart()
    pupil_positions = json.loads(msg)

    for pupil_position in pupil_positions:
        pupil_x,pupil_y = pupil_position['norm_pos']
        client.send( OSCMessage("/pupil/norm_pos", (pupil_y,pupil_y)) )

