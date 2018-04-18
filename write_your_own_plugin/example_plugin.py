'''
(*)~----------------------------------------------------------------------------------
 Pupil - eye tracking platform
 Copyright (C) 2012-2015  Pupil Labs

 Distributed under the terms of the CC BY-NC-SA License.
 License details are in the file license.txt, distributed as part of this software.
----------------------------------------------------------------------------------~(*)
'''

import cv2
import numpy as np
from pyglui import ui
from pyglui.cygl.utils import draw_polyline, draw_points, RGBA, draw_gl_texture
import gl_utils
from glfw import *

from plugin import Plugin
# logging
import logging
logger = logging.getLogger(__name__)


class Example_Plugin(Plugin):
    """Describe your plugin here
    """
    def __init__(self, g_pool, my_persistent_var=10.0, ):
        super(Example_Plugin, self).__init__(g_pool)
        # order (0-1) determines if your plugin should run before other plugins or after
        self.order = .2

        # all markers that are detected in the most recent frame
        self.my_var = my_persistent_var

        self.window = None
        self.menu = None
        self.img = None

        self.animation_state = 0

    def init_ui(self):
        # lets make a menu entry in the sidebar
        self.add_menu()
        self.menu.label = 'My Plugin'

        # and a slider
        self.menu.append(ui.Slider('my_var', self, min=1.0))

        # this is also a good place to open a custom window:
        # let make the size identical to the img size:
        width, height = self.g_pool.capture.frame_size
        # here we use glfw to create a new window: 'share' should point to
        # the main gl context so we can reuse textures from there.
        self.window = glfwCreateWindow(width, height, "Plugin Window", monitor=None, share=glfwGetCurrentContext())

        # now the set up some window callback. Have a look at referece_surface.py to see whats possible
        glfwSetFramebufferSizeCallback(self.window, self.on_resize)

        # lets set up the window gl state
        # if you want to draw or change settings of a window
        # you need to activate it and once done deactivate
        active_window = glfwGetCurrentContext()
        glfwMakeContextCurrent(self.window)
        # set up blending etc
        gl_utils.basic_gl_setup()
        # refresh speed settings
        glfwSwapInterval(0)
        glfwMakeContextCurrent(active_window)

        self.on_resize(self.window, *glfwGetFramebufferSize(self.window))

    # window calback
    def on_resize(self, window, w, h):
        active_window = glfwGetCurrentContext()
        glfwMakeContextCurrent(window)
        gl_utils.adjust_gl_view(w, h)
        glfwMakeContextCurrent(active_window)

    def deinit_ui(self):
        self.remove_menu()

    def recent_events(self, events):
        if 'frame' in events:
            frame = events['frame']
        else:
            return

        # here we make a reference to the frame so we can use in later in gl_display
        # if we only need a grayscale image its much faster to just do frame.gray
        # instead of converting with opencv
        self.img = frame.img

        # lets do some animation math
        self.animation_state += 0.04
        moving_point = [int(400+100*np.sin(self.animation_state)), int(200+100*np.cos(self.animation_state))]

        # Now we can do all the processing we want.
        # Keep in mind that inplace modification of frame.img or frame.gray
        # will show up in later run plugins and in the main window.
        # To illustrage this point I will draw something into the image using Opencv draw funtions
        cv2.putText(self.img, "Hi from Plugin. The variable is: {}".format(self.my_var), (100, 90),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 150, 100))
        cv2.polylines(self.img, np.array([[[100, 100], [800, 100], moving_point]]), color=(0, 0, 255), isClosed=True)
        # however using opengl to draw on the screen is better. See below

    def gl_display(self):
        """
        This is where we can draw to any gl surface
        by default this is the main window, below we change that
        """

        # active our window
        active_window = glfwGetCurrentContext()
        glfwMakeContextCurrent(self.window)

        # start drawing things:
        gl_utils.clear_gl_screen()
        # set coordinate system to be between 0 and 1 of the extents of the window
        gl_utils.make_coord_system_norm_based()
        # draw the image
        draw_gl_texture(self.img)

        # make coordinte system identical to the img pixel coordinate system
        gl_utils.make_coord_system_pixel_based(self.img.shape)
        # draw some points on top of the image
        # notice how these show up in our window but not in the main window
        draw_points([(200, 400), (600, 400)], color=RGBA(0., 4., .8, .8), size=self.my_var)
        draw_polyline([(200, 400), (600, 400)], color=RGBA(0., 4., .8, .8), thickness=3)

        # since this is our own window we need to swap buffers in the plugin
        glfwSwapBuffers(self.window)

        # and finally reactive the main window
        glfwMakeContextCurrent(active_window)

    def get_init_dict(self):
        # anything vars we want to be persistent accross sessions need to show up in the __init__
        # and identically as a dict entry below:
        return {'my_persistent_var': self.my_var}

    def cleanup(self):
        """ called when the plugin gets terminated.
        This happens either voluntarily or forced.
        if you have a GUI or glfw window destroy it here.
        """
        glfwDestroyWindow(self.window)
