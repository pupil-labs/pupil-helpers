"""
Receive data from Pupil server broadcast using ZMQ.
"""
import zmq
import json

#network setup
port = "5000"
context = zmq.Context()
socket = context.socket(zmq.SUB)
socket.connect("tcp://127.0.0.1:"+port)

#recv all messages
socket.setsockopt(zmq.SUBSCRIBE, '')
#recv just pupil postions
# socket.setsockopt(zmq.SUBSCRIBE, 'pupil_positions')
# recv just gaze postions
# socket.setsockopt(zmq.SUBSCRIBE, 'gaze_positions')

while True:
    topic,msg =  socket.recv_multipart()
    msg = json.loads(msg)
    print  "\n\n",topic,":\n",msg
