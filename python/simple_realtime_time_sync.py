"""Simple Time Sync

Time sync is important 
"""
import time

import zmq


def main():
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
    """Creates a zmq-REQ socket and connects it to Pupil Capture or Service"""
    ctx = zmq.Context.instance()
    socket = ctx.socket(zmq.REQ)
    socket.connect(f"tcp://{ip_adress}:{port}")
    return socket


def request_pupil_time(socket):
    socket.send_string("t")
    pupil_time = socket.recv()
    return float(pupil_time)


def measure_clock_offset(socket, clock_function):
    local_time_before = clock_function()
    pupil_time = request_pupil_time(socket)
    local_time_after = clock_function()

    local_time = (local_time_before + local_time_after) / 2.0
    clock_offset = pupil_time - local_time
    return clock_offset


def measure_clock_offset_stable(socket, clock_function, nsamples=10):
    assert nsamples > 0, "Requires at least one sample"
    offsets = [measure_clock_offset(socket, clock_function) for x in range(nsamples)]
    return sum(offsets) / len(offsets)  # mean offset


if __name__ == "__main__":
    main()
