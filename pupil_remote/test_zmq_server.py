'''
This is a test server. It will listen for commands and echo them.
'''

import zmq
import time

port = "50020"
context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:%s" % port)

while True:
    try:
        msg = socket.recv(flags=zmq.NOBLOCK)
    except zmq.ZMQError :
        msg = None
    if msg:
        print msg
        socket.send("%s - confirmed"%msg)

    time.sleep(.1)
    print 'wait'

context.close()
