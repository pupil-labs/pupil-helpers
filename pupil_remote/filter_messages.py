"""
Receive data from Pupil using ZMQ.
"""
import zmq
from msgpack import loads
from pupil_remote_control import Requester

context = zmq.Context()
#open a req port to talk to pupil
addr = '127.0.0.1'                  # remote ip or localhost
req_port = 50020                    # same as in the pupil remote gui
url = "tcp://%s:%s"%(addr,req_port)
req = Requester(context,url)        # initialize Pupil Remote utility
sub_port = req.send_cmd('SUB_PORT') # ask for the sub port

# open a sub port to listen to pupil
sub = context.socket(zmq.SUB)
sub.connect("tcp://%s:%s" %(addr,sub_port))

# set subscriptions to topics
# recv just pupil/gaze/notifications
sub.setsockopt(zmq.SUBSCRIBE, 'pupil.')
# sub.setsockopt(zmq.SUBSCRIBE, 'gaze')
sub.setsockopt(zmq.SUBSCRIBE, 'notify.')
sub.setsockopt(zmq.SUBSCRIBE, 'logging.')
# or everything
# sub.setsockopt(zmq.SUBSCRIBE, '')


while True:
    topic,msg =  sub.recv_multipart()
    msg = loads(msg)
    print  "\n",topic,":",msg
