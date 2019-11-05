# Create Marker Sheets

Here is an example script for how to create your custom marker sheets.
The Apriltag markers can be downloaded from [the official Apriltag repository](https://github.com/AprilRobotics/apriltag-imgs/tree/master/ "GitHub Apriltag Image Repository").

See the script [`create_marker_sheet.py`](./create_marker_sheet.py). It assumes to be placed into the Apriltag image repository, alongside the folders with the Apriltag families. Change the global parameters `FAMILY` and `PAGE` to control which set of markers to generate the sheet from.

Here are two examples, ready to download and use:

| `FAMILY="tag36h11"` and `PAGE=0`                                    | `FAMILY="tag36h11"` and `PAGE=1`                                     |
| ------------------------------------------------------------------- | -------------------------------------------------------------------- |
| [![](./apriltags_tag36h11_0-23.png)](./apriltags_tag36h11_0-23.png) | [![](./apriltags_tag36h11_24-47.png)](./apriltags_tag36h11_0-23.png) |
