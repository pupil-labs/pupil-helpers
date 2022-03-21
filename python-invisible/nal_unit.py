import struct
import typing as T


def extract_payload_from_nal_unit(unit: T.ByteString) -> T.ByteString:
    """
    - prepend NAL unit start code to payload if necessary
    - handle fragemented units (of type FU-A)

    Inspired by https://github.com/runtheops/rtsp-rtp/blob/master/transport/primitives/nal_unit.py
    Rewritten due to licensing issues.
    """
    start_code = b"\x00\x00\x00\x01"
    offset = 0
    # slice to keep ByteString type; indexing would return int in native byte order
    first_byte = unit[:1]
    # ensure network order for conversion to uint8
    first_byte = struct.unpack("!B", first_byte)[0]
    is_first_bit_one = first_byte & 0b10000000
    if is_first_bit_one:
        # See section 1.3 of https://www.ietf.org/rfc/rfc3984.txt
        raise ValueError("First bit must be zero (forbidden_zero_bit)")

    nal_type = first_byte & 0b00011111
    if nal_type == 28:
        # Fragmentation unit FU-A
        # https://www.ietf.org/rfc/rfc3984.txt
        # Section 5.8.
        fu_header = unit[1:2]  # get second byte while retaining ByteString type
        fu_header = struct.unpack("!B", fu_header)[0]
        offset = 2  # skip first two bytes

        is_fu_start_bit_one = fu_header & 0b10000000
        if is_fu_start_bit_one:
            # reconstruct header of a non-fragmented NAL unit
            first_byte_bits_1_to_3 = first_byte & 0b11100000
            # NAL type of non-fragmented NAL unit:
            fu_header_bits_4_to_8 = fu_header & 0b00011111
            reconstructed_header = first_byte_bits_1_to_3 + fu_header_bits_4_to_8
            start_code += bytes((reconstructed_header,))  # convert int to ByteString
        else:
            # do not prepend start code to payload since we are in the middle of a
            # fragmented unit
            start_code = b""

    return start_code + unit[offset:]
