import cv2
import numpy as np

"""
Make square markers is a helper script that is used to generate 5x5 square marker png files that can be printed.
See documentation on surface tracking on the Pupil docs website:
https://docs.pupil-labs.com/#surface-tracking
"""


def encode_marker(mId):
    # marker is based on grid of black (0) /white (1) pixels
    #  b|b|b|b|b
    #  b|o|m|o|b    b = black border feature
    #  b|m|m|m|b    o = orientation feature
    #  b|o|m|o|b    m = message feature
    #  b|b|b|b|b
    grid = 5
    m_with_b = np.zeros((grid, grid), dtype=np.uint8)
    m = m_with_b[1:-1, 1:-1]

    # bitdepth = grid-border squared - 3 for orientation (orientation still
    # yields one bit)
    bitdepth = ((5 - 2)**2) - 3

    if mId >= (2**bitdepth):
        raise Exception(
            "ERROR: ID overflow, this marker can only hold {:i} bits of information".format(bitdepth))

    msg = [0] * bitdepth
    for i in range(len(msg))[::-1]:
        msg[i] = mId % 2
        mId = mId >> 1

    # out first bit is encoded in the orientation corners of the marker:
    #               MSB = 0                   MSB = 1
    #               W|*|*|W   ^               B|*|*|B   ^
    #               *|*|*|*  / \              *|*|*|*  / \
    #               *|*|*|*   |  UP           *|*|*|*   |  UP
    #               B|*|*|W   |               W|*|*|B   |

    msb = msg.pop(0)
    if msb:
        orientation = 0, 1, 0, 0
    else:
        orientation = 1, 0, 1, 1

    m[0, 0], m[-1, 0], m[-1, -1], m[0, -1] = orientation

    msg_mask = np.ones(m.shape, dtype=np.bool)
    msg_mask[0, 0], msg_mask[-1, 0], msg_mask[-1, -
                                              1], msg_mask[0, -1] = 0, 0, 0, 0
    m[msg_mask] = msg[::-1]

    return m_with_b


def write_marker_png(marker_id, size=80):
    marker_id_str = "%02d" % marker_id
    m = encode_marker(marker_id) * 255
    m = cv2.resize(m, (size, size), interpolation=cv2.INTER_NEAREST)
    m = cv2.cvtColor(m, cv2.COLOR_GRAY2BGR)
    cv2.imwrite('marker_{}.png'.format(marker_id_str), m)


def write_all_markers_png(width, height):
    rows, cols, m_size = 8, 8, 9
    canvas = np.ones((m_size * rows, m_size * cols), dtype=np.uint8)


    r = 0
    c = 0

    for m_id in range(64):
        if m_id != 32:
            # skip marker_id == 32 
            marker_with_padding = np.ones((9, 9))
            marker_with_padding[2:-2, 2:-2] = encode_marker(m_id)
            m_size = marker_with_padding.shape[0]


            canvas[r:r + m_size, c:c + m_size] = marker_with_padding * 255

            r += m_size
            if r == rows * m_size:
                r = 0
                c += m_size

    canvas = cv2.resize(canvas, (width, height),
                        interpolation=cv2.INTER_NEAREST)
    canvas = cv2.cvtColor(canvas, cv2.COLOR_GRAY2BGR)
    canvas[canvas == 1] = 255
    cv2.imwrite('all_markers.png', canvas)


if __name__ == '__main__':
    write_all_markers_png(1200, 1200)

    for marker_id in range(64):
        if marker_id != 32:
            # exclude marker_id = 33
            write_marker_png(marker_id)
