# Pupil Helper Python Examples

The following scripts use the [Pupil Network API](https://docs.pupil-labs.com/developer/core/network-api/)
to remote control and receive data from [Pupil Capture](https://docs.pupil-labs.com/core/software/pupil-capture/)
and [Pupil Service](https://docs.pupil-labs.com/core/software/pupil-service/).

- [`pupil_remote_control.py`](pupil_remote_control.py):
[Remote control](https://docs.pupil-labs.com/developer/core/network-api/#pupil-remote) example.
- [`filter_messages.py`](filter_messages.py): Receive real-time data from Pupil Capture or Pupil Service.
- [`filter_gaze_on_surface.py`](filter_gaze_on_surface.py):
Receive [surface-mapped gaze](https://docs.pupil-labs.com/core/terminology/#surface-aoi-coordinate-system).
Requires [surface tracking](https://docs.pupil-labs.com/core/software/pupil-capture/#surface-tracking) to be enabled in Pupil Capture.
- [`mouse_control.py`](mouse_control.py): Use [surface-mapped gaze](https://docs.pupil-labs.com/core/terminology/#surface-aoi-coordinate-system)
gaze to control your mouse. [Demo](https://www.youtube.com/watch?v=qHmfMxGST7A&t=3s).
Requires [surface tracking](https://docs.pupil-labs.com/core/software/pupil-capture/#surface-tracking) to be enabled in Pupil Capture. 
- [`recv_world_video_frames.py`](recv_world_video_frames.py): Receive scene and eye camera images in real-time from Pupil Capture or Pupil Service..
- [`recv_world_video_frames_with_visualization.py`](recv_world_video_frames_with_visualization.py):
Receive and visualize scene and eye camera images in real-time from Pupil Capture or Pupil Service..
- [`remote_annotations.py`](remote_annotations.py):
[Annotate events remotely](https://docs.pupil-labs.com/developer/core/network-api/#remote-annotations) in Pupil Capture. Useful for event-based post-hoc analyses.
- [`serial_bridge.py`](serial_bridge.py):
Script that receives [pupil data](https://docs.pupil-labs.com/core/terminology/#pupil-positions)
in real-time from Pupil Capture or Pupil Service and relays it via a serial interface.
- [`simple_realtime_time_sync.py`](simple_realtime_time_sync.py): Script that calculates
offset between local and remote pupil clock. Offset can be used to create time-synchronized
time measurements in your local experiment.
- [`test_pupil_detector_network_api.py`](test_pupil_detector_network_api.py):
Retrieve and set pupil detection configuration in Pupil Capture or Pupil Service.

## Dependencies

In order to run the Python examples in this directory you will need to install these dependencies.

```sh
pip install zmq msgpack==0.5.6
```

### Additional dependencies

For some of the examples you will need additonal depencies in order to run them:

- `mouse_control.py `: `pip install PyUserInput`
- `recv_world_video_frames.py`: `pip install numpy`
- `recv_world_video_frames_with_visualization.py `: `pip install numpy opencv-python`
- `serial_bridge.py`: `pip install pyserial`

## Pupil Core Network Client

Instead of copying some of the examples above, you can use their functionality via the
[Pupil Core network client Python module](https://pupil-core-network-client.readthedocs.io/en/latest/).
