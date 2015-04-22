# Pupil Remote

This collection of scripts emulates a toolchain where: 
* a UDP signal is used to broadcast the beginning of a recording. - `udp_broadcast_server.py`
* a bridge script relays the information using 0MQ. - `udp_serial_bridge.py`
* Pupil Capture Plugin `Pupil_Remote` will start the appropriate fn in Capture.


Pupil Remote can be emulated with `test_zmq_server.py`

Currently supported controls:

* "R recording_name" : start a recording, sending "R" again will stop the recording
* "T" : set timebase to 0
* "C": start callibration


