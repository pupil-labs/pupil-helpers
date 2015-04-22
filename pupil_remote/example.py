#zmq setup
import zmq
context = zmq.Context()
z = context.socket(zmq.REQ)
z.connect("tcp://localhost:50020") #configure for localhost on port 50020

import time

while 1:
    msg = 'R:%s'%time.time()
    z.send(msg)
    print "sent '%s' "%msg
    confirmation = z.recv()
    print "received: '%s' "%confirmation
    time.sleep(5)

