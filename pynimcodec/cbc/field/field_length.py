"""Functions for handling variable Field length."""

from pynimcodec.bitman import BitArray, append_bits_to_buffer, extract_from_buffer


def decode_field_length(buffer: bytes, offset: int) -> 'tuple[int, int]':
    """Decode the length (L) of a variable-length field."""
    L_flag = extract_from_buffer(buffer, offset, 1)
    offset += 1
    L_len = 15 if L_flag else 7
    return (
        extract_from_buffer(buffer, offset, L_len),
        offset + L_len,
    )


def encode_field_length(size: int,
                        buffer: bytearray,
                        offset: int,
                        ) -> 'tuple[bytearray, int]':
    """Encode the length (L) of a variable-length field."""
    bits = BitArray.from_int(size, 8 if size < 128 else 16)
    if size > 127:
        bits[0] = 1
    buffer = append_bits_to_buffer(bits, buffer, offset)
    return ( buffer, offset + len(bits) )
