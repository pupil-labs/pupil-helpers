import argparse
import csv
import itertools
import logging

import pylsl

logger = logging.getLogger(__name__)
TIMEOUT = 3.0


def main(csv_out_path):
    logger.info("Looking for Pupil Capture streams...")
    streams = pylsl.resolve_byprop("name", "pupil_capture", timeout=TIMEOUT)

    if not streams:
        logger.error("No LSL streams of name 'pupil_capture' found")
        exit(-1)

    logger.info("Connecting to {}".format(streams[0].hostname()))
    inlet = pylsl.StreamInlet(streams[0])
    inlet.open_stream(timeout=TIMEOUT)

    logger.info("Recording at {}".format(csv_out_path))
    record(inlet, csv_out_path)


def csv_header(inlet):
    yield "timestamp"
    description = inlet.info(timeout=TIMEOUT).desc()
    channel = description.child("channels").first_child()
    while not channel.empty():
        yield channel.child_value("label")
        channel = channel.next_sibling()


def record(inlet, csv_out_path):
    with open(csv_out_path, "w") as csv_file:
        csv_writer = csv.writer(csv_file)
        record_header(inlet, csv_writer)
        record_loop(inlet, csv_writer)


def record_header(inlet, csv_writer):
    header = csv_header(inlet)
    csv_writer.writerow(header)


def record_loop(inlet, csv_writer):
    samples_written = 0
    while True:
        try:
            samples_written += record_chunk(inlet, csv_writer)
            logger.debug("{} samples written".format(samples_written))
        except KeyboardInterrupt:
            logger.error("User cancelled connection")
            break
        except pylsl.LostError:
            logger.error("Connection lost")
            break


def record_chunk(inlet, csv_writer):
    chunk = inlet.pull_chunk(timeout=TIMEOUT)
    rows = [itertools.chain((ts,), datum) for datum, ts in zip(*chunk)]
    csv_writer.writerows(rows)
    return len(rows)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    parser = argparse.ArgumentParser(
        description="Records data from a LSL pupil_capture inlet to csv."
    )
    parser.add_argument("-R", "--recording", default="lsl-recording.csv")
    args = parser.parse_args()
    main(csv_out_path=args.recording)
