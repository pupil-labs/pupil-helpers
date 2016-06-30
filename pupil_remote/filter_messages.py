"""
Receive data from Pupil using ZMQ.
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

# set subscriptions to topics
# recv just pupil/gaze/notifications
sub.setsockopt(zmq.SUBSCRIBE, 'pupil.')
# sub.setsockopt(zmq.SUBSCRIBE, 'gaze.')
sub.setsockopt(zmq.SUBSCRIBE, 'notify.')
sub.setsockopt(zmq.SUBSCRIBE, 'logging.')
# or everything
# sub.setsockopt(zmq.SUBSCRIBE, '')


while True:
    topic,msg =  sub.recv_multipart()
    msg = loads(msg)
    print  "\n",topic,":",msg