"""
Stream Pupil gaze coordinate data using zmq to control a mouse with your eye.
Please note that marker tracking must be enabled, and in this example we have named the surface "screen."
You can name the surface what you like in Pupil capture and then write the name of the surface you'd like to use on line 17.
"""
import zmq
import json
import subprocess as sp
import sys
from platform import system

try:
    from pymouse import PyMouse
    m = PyMouse()
    m.move(0,0) # hack to init PyMouse -- still needed
except ImportError:
    pass

def set_mouse(x=0,y=0,click=0):
    if system() == "Darwin":
        sp.Popen(["./mac_os_helpers/mouse", "-x", "%s" %x, "-y", "%s" %y, "-click", "%s" %click])
    else:
        if click:
            m.click(x,y)
        else:
            m.move(x,y)

def get_screen_size():
    screen_size = None
    if system() == "Darwin":
        screen_size = sp.check_output(["./mac_os_helpers/get_screen_size"]).split(",")
        screen_size = float(screen_size[0]),float(screen_size[1])
    else:
        screen_size = m.screen_size()
    return screen_size  


port = "5000"
context = zmq.Context()
socket = context.socket(zmq.SUB)
socket.connect("tcp://127.0.0.1:"+port)
#get gaze data only
socket.setsockopt(zmq.SUBSCRIBE, 'gaze_positions')
smooth_x, smooth_y = 0.5, 0.5

# screen size
x_dim, y_dim = get_screen_size()
print "x_dim: %s, y_dim: %s" %(x_dim,y_dim)

# specify the name of the surface you want to use
surface_name = "screen"
while True:
    topic,msg =  socket.recv_multipart()
    gaze_positions = json.loads(msg)

    for gaze_position in gaze_positions:

        try:
            gaze_on_screen = gaze_position["realtime gaze on "+surface_name]
            raw_x,raw_y = gaze_on_screen
            
            # smoothing out the gaze so the mouse has smoother movement
            smooth_x += 0.5 * (raw_x-smooth_x)
            smooth_y += 0.5 * (raw_y-smooth_y)
            x = smooth_x
            y = smooth_y

            y = 1-y # inverting y so it shows up correctly on screen
            x *= int(x_dim)
            y *= int(y_dim)
            # PyMouse or MacOS bugfix - can not go to extreme corners because of hot corners?
            x = min(x_dim-10, max(10,x))
            y = min(y_dim-10, max(10,y))

            print "%s,%s" %(x,y)
            set_mouse(x,y)
        except KeyError:
            pass




