# Pupil LSL Helpers

## Requirements

```bash
pip3 install -r requirements.txt --user
```

## `lsl_inlet`

`lsl_inlet.py` is a small Python example on how to record lab streaming layer data published by the `Pupil LSL Relay` plugin.
The recorded data is stored as a csv file, by default `lsl-recording.csv`.

```
usage: lsl_inlet.py [-h] [-R RECORDING]

Records data from a LSL pupil_capture inlet to csv.

optional arguments:
  -h, --help            show this help message and exit
  -R RECORDING, --recording RECORDING
```

## Visualize LSL Recording

The Jupyter Notebook loads the prerecorded `lsl-recording.csv` and gives examples on how to 
- Filter the recorded data by confidence
- Visualize the recorded gaze distribution
- Visualize the2d and 3d diameter over time
