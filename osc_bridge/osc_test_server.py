'''
simple python osc test server that will print pupil/norm_pos mssages


installing pyOSC:
git clone git://gitorious.org/pyosc/devel.git pyosc
cd pyosc
python setup.py install (may need sudo)
'''

from OSC import OSCServer
import sys
from time import sleep

server = OSCServer( ("localhost", 7110) )
server.timeout = 0
run = True

# this method of reporting timeouts only works by convention
# that before calling handle_request() field .timed_out is
# set to False
def handle_timeout(self):
    self.timed_out = True

# funny python's way to add a method to an instance of a class
import types
server.handle_timeout = types.MethodType(handle_timeout, server)

def callback(path, tags, args, source):
    print path,args

server.addMsgHandler( "/pupil/norm_pos", callback )


while run:
    # do the game stuff:
    sleep(0.01)
    # call user script
    # clear timed_out flag
    server.timed_out = False
    # handle all pending requests then return
    while not server.timed_out:
        server.handle_request()

server.close()