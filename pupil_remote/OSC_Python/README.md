# Surface OSC Bridge

`surface_osc_relay.py` subscribes to Pupil Capture surface data and redirects
it using the [`OSC` protocol](http://opensoundcontrol.org/introduction-osc).
An OSC receiver can readout the values and use them for e.g. controlling
instruments.

`recv_surface_data.maxpat` implements such an OSC receiver and parses the
incoming data for further usage.

### Requirements

`surface_osc_relay.py` requires the Python module `pyzmq`, `msgpack-python`,
and `python-osc` to run. `recv_surface_data.maxpat` is a [`Max` patch](https://cycling74.com/products/max)
and can be opened with `Max 7`.

### Usage

1. Start `Pupil Capture`, open the `Surface Tracker` plugin, and setup your surfaces.
2. Run `python3 surface_osc_relay.py` to start the relay.
3. Open `recv_surface_data.maxpat` in `Max 7` and receive surface data.

### Attribution
Idea by @DouglasMackay. Implementation by @papr.
