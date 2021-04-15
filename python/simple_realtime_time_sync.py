"""Simple Time-Sync

## Introduction

Eye-tracking data is often analysed in the context of externally controlled stimuli
or other physiological sensors, e.g. EEG. In order to correlate the recorded data, its
temporal alignment is of importance. By default, most sensors or experiment softwares
come with their own clock to measure time consistently. These clocks rarely share a
common starting point which would allow for automatic time alignment. In return, these
clocks can guarantee to be monotonicly increasing and very accurate when it comes to
measuring time differences. Pupil Core software is no exception in this regard. In the
example below, we show how one can calculate the offset between a custom "local" clock
and the clock used in Pupil Core software in real time.

## Local clocks

When syncing time, one needs to decide on which clock to sync to. This often is
dependent on the use case and the required measurement precision. The recommended clock
for simple Python scripts is `time.perf_counter()` [1]. If you need time measured in
Unix epoch (less accurate but defines a common starting point), use `time.time()` [2].
Experiment software like psychopy provide their own clock functions [3].

Important: What ever clock function you use, make sure that you use it consistenly
across the experiment. Any change to the clock, e.g. via a reset, invalidates the
measured clock offset and requires you to remeasure it.

Since Pupil Core measures time in seconds, this script expects the local clock to
measure time in seconds as well.

[1] https://docs.python.org/3/library/time.html#time.perf_counter
[2] https://docs.python.org/3/library/time.html#time.time
[3] https://www.psychopy.org/api/clock.html

## Simplifying assumptions

For this script, we make a few simplifying assumptions. Specifically, we assume that
both involved clocks (local and remote) do not drift. The term `drift` refers to the
issue that the clock offsets might change over time due to inaccuracies of the clocks.
A possible solution is to periodically measure the offset and correct for potential
drift. In this example, we measure the offset once and assume no drift on the offset.

For a more accurate and stable time sync see
https://docs.pupil-labs.com/core/software/pupil-capture/#network-plugins
which is based on https://en.wikipedia.org/wiki/Network_Time_Protocol

## Requirements

- `time` module; built-in functionality; includes local clock function for this example
- `pyzmq` module; pip install pyzmq; handles network communication to Core software
"""
import time

import zmq


def main():
    """This example performs these steps
    1. Setup network connection (always required)
    2. Setup local clock function (always required)
    3. Measure clock offset once
    4. Measure clock offset more reliably (multiple measurements)
    5. Infer remote clock time from local clock measurement
    """
    socket = setup_pupil_remote_connection(ip_adress="127.0.0.1")

    # local_clock = time.time  # Unix time, less accurate
    # local_clock = psychopy.clock.MonotonicClock().getTime  # new psychopy clock
    # local_clock = existing_psychopy_clock.getTime  # existing psychopy clock
    local_clock = time.perf_counter

    offset = measure_clock_offset(socket, clock_function=local_clock)
    print(f"Clock offset (1 measurement): {offset} seconds")

    number_of_measurements = 10
    stable_offset_mean = measure_clock_offset_stable(
        socket, clock_function=local_clock, nsamples=number_of_measurements
    )
    print(
        f"Mean clock offset ({number_of_measurements} measurements): "
        f"{stable_offset_mean} seconds"
    )

    local_time = local_clock()
    pupil_time_calculated_locally = local_time + stable_offset_mean
    print(f"Local time: {local_time}")
    print(f"Pupil time (calculated locally): {pupil_time_calculated_locally}")


def setup_pupil_remote_connection(
    ip_adress: str = "127.0.0.1", port: int = 50020
) -> zmq.Socket:
    """Creates a zmq-REQ socket and connects it to Pupil Capture or Service

    See https://docs.pupil-labs.com/developer/core/network-api/ for details.
    """
    ctx = zmq.Context.instance()
    socket = ctx.socket(zmq.REQ)
    socket.connect(f"tcp://{ip_adress}:{port}")
    return socket


def request_pupil_time(socket):
    """Uses an existing Pupil Core software connection to request the remote time.
    Returns the current "pupil time" at the timepoint of reception.

    See https://docs.pupil-labs.com/core/terminology/#pupil-time for more information
    about "pupil time".
    """
    socket.send_string("t")
    pupil_time = socket.recv()
    return float(pupil_time)


def measure_clock_offset(socket, clock_function):
    """Calculates the offset between the Pupil Core software clock and a local clock.

    Requesting the remote pupil time takes time. This delay needs to be considered
    when calculating the clock offset. We measure the local time before (A) and
    after (B) the request and assume that the remote pupil time was measured at (A+B)/2,
    i.e. the midpoint between A and B.

    As a result, we have two measurements from two different clocks that were taken
    assumingly at the same point in time. The difference between them ("clock offset")
    allows us, given a new local clock measurment, to infer the corresponding time on
    the remote clock.
    """
    local_time_before = clock_function()
    pupil_time = request_pupil_time(socket)
    local_time_after = clock_function()

    local_time = (local_time_before + local_time_after) / 2.0
    clock_offset = pupil_time - local_time
    return clock_offset


def measure_clock_offset_stable(socket, clock_function, nsamples=10):
    """Returns the mean clock offset after multiple measurements to reduce the effect
    of varying network delay.

    Since the network connection to Pupil Capture/Service is not necessarily stable,
    one has to assume that the delays to send and receive commands are not symmetrical
    and might vary. To reduce the possible clock-offset estimation error, this function
    repeats the measurement multiple times and returns the mean clock offset.

    The variance of these measurements is expected to be higher for remote connections
    (two different computers) than for local connections (script and Core software
    running on the same computer). You can easily extend this function to perform
    further statistical analysis on your clock-offset measurements to examine the
    accuracy of the time sync.
    """
    assert nsamples > 0, "Requires at least one sample"
    offsets = [measure_clock_offset(socket, clock_function) for x in range(nsamples)]
    return sum(offsets) / len(offsets)  # mean offset


if __name__ == "__main__":
    main()
