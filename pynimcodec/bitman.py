"""Utilities for bit manipulation."""

from typing import Any, Iterable


class BitArray(list):
    """An array of bits for bitwise manipulation."""
    
    def __init__(self, *args) -> None:
        for arg in args:
            if arg not in (0, 1):
                raise ValueError('All elements must be 0 or 1.')
        super().__init__(args)
    
    def append(self, value: int) -> None:
        if value not in (0, 1):
            raise ValueError('Only 0 or 1 can be appended to BitArray.')
        super().append(value)
    
    def extend(self, iterable: Iterable) -> None:
        if not all(bit in (0, 1) for bit in iterable):
            raise ValueError('All elements must be 0 or 1.')
        super().extend(iterable)
    
    def insert(self, index: int, value: int) -> None:
        if value not in (0, 1):
            raise ValueError('Only 0 or 1 can be inserted into BitArray.')
        super().insert(index, value)
    
    def __setitem__(self, index, value):
        if value not in (0, 1):
            raise ValueError('Only 0 or 1 can be assigned to BitArray element.')
        super().__setitem__(index, value)
    
    def __getitem__(self, index: int) -> int:
        return super().__getitem__(index)

    def __delitem__(self, index: int) -> None:
        super().__delitem__(index)
    
    def __repr__(self):
        return f'BitArray({super().__repr__()})'
    
    def __str__(self):
        return '0b' + ''.join(str(bit) for bit in self)
    
    @classmethod
    def from_int(cls, value: int, length: int = None) -> 'BitArray':
        """Create a BitArray instance from an integer.
        
        Args:
            value (int): The integer value to convert to bits.
            length (int): The number of bits to use, padding with 0s or
                two's complement. If None uses the minimum required bits.
            
        Returns:
            BitArray: The created BitArray instance.
        
        Raises:
            ValueError: If value is not a valid integer or length is too small
                to represent the number of bits.
        """
        if not isinstance(value, int):
            raise ValueError('Invalid integer')
        if length is None:
            length = value.bit_length() + (1 if value < 0 else 0)
        if not isinstance(length, int) or length <= 0:
            raise ValueError('Length must be a positive integer.')
        if value < 0:
            max_value = (1 << length)
            value = max_value + value
        bits = list(map(int, bin(value)[2:]))
        if len(bits) > length:
            raise ValueError('Length too small to represent the value.')
        bits = [0] * (length - len(bits)) + bits
        return cls(*bits)
    
    @classmethod
    def from_bytes(cls, value: 'bytes|bytearray') -> 'BitArray':
        """Create a BitArray instance from a buffer of bytes.
        
        Args:
            value (bytes): The buffer to convert to bits.
        
        Returns:
            BitArray: The created BitArray instance.
        
        Raises:
            ValueError: If value is not valid bytes.
        """
        if not isinstance(value, (bytes, bytearray)):
            raise ValueError('Invalid bytes')
        bits = []
        for byte in value:
            bits.extend(int(bit) for bit in f'{byte:08b}')
        return cls(*bits)


def is_int(candidate: Any, allow_string: bool = False) -> bool:
    """Check if a value is an integer."""
    if isinstance(candidate, int):
        return True
    if allow_string:
        try:
            return isinstance(int(candidate), int)
        except ValueError:
            pass
    return False


def extract_from_buffer(buffer: bytes,
                        offset: int,
                        length: int = None,
                        signed: bool = False,
                        as_buffer: bool = False,
                        ) -> 'int|bytes':
    """Extract the value of bits from a buffer at a bit offset.
    
    Args:
        buffer (bytes): The buffer to extract from.
        offset (int): The bit offset to start from.
        length (int): The number of bits to extract. If None, extracts to the
            end of the buffer.
        signed (bool): If True will extract a signed value (two's complement).
        as_buffer (bool): Return the value as a buffer (default returns integer).
    
    Returns:
        int|bytes: The extracted value.
    
    Raises:
        ValueError: If the buffer, offset or length are invalid.
    """
    if not isinstance(buffer, (bytes, bytearray)):
        raise ValueError('Invalid buffer')
    if not isinstance(offset, int) or offset < 0 or offset >= len(buffer) * 8:
        raise ValueError('Invalid offset')
    if length is not None and (not isinstance(length, int) or length < 1):
        raise ValueError('Invalid length')
    if length is None:
        length = len(buffer) * 8 - offset
    if offset + length > len(buffer) * 8:
        raise ValueError('Bit offset + length exceeds buffer size.')
    start_byte = offset // 8
    end_byte = (offset + length - 1) // 8 + 1
    bit_start_within_byte = offset % 8
    raw_data = int.from_bytes(buffer[start_byte:end_byte], byteorder='big')
    total_bits = (end_byte - start_byte) * 8
    shift_amount = total_bits - bit_start_within_byte - length
    extracted_bits = (raw_data >> shift_amount) & ((1 << length) - 1)
    if signed and (extracted_bits & (1 << (length - 1))):
        extracted_bits -= (1 << length)
    if as_buffer:
        return int.to_bytes(extracted_bits, length // 8, 'big')
    return extracted_bits


def append_bits_to_buffer(bit_array: BitArray,
                          buffer: bytearray,
                          offset: int = 0,
                          ) -> bytearray:
    """Add bits to a buffer at a bit offset.
    
    Args:
        bit_array (BitArray): The bit array to append to the buffer.
        buffer (bytearray): The buffer to append to.
        offset (int): The offset to start appending. Defaults to the start of
            the buffer.
    
    Returns:
        bytearray: The modified buffer.
    
    Raises:
        ValueError: If bit_array, buffer or offset are invalid.
    """
    if (not isinstance(bit_array, (BitArray, list)) or
        not all(b in (0, 1) for b in bit_array)):
        raise ValueError('Invalid BitArray')
    if not isinstance(buffer, bytearray):
        raise ValueError('Invalid buffer')
    if not isinstance(offset, int) or offset < 0:
        raise ValueError('offset must be a non-negative integer')
    if len(buffer) == 0:
        buffer.append(0)
    if offset > len(buffer) * 8:
        raise ValueError(f'offset {offset} exceeds the current buffer size.')
    total_bits = offset + len(bit_array)
    required_bytes = (total_bits + 7) // 8
    while len(buffer) < required_bytes:
        buffer.append(0)
    byte_offset = offset // 8
    bit_offset_in_byte = offset % 8
    for bit in bit_array:
        if bit == 1:
            buffer[byte_offset] |= (1 << (7 - bit_offset_in_byte))
        else:
            buffer[byte_offset] &= ~(1 << (7 - bit_offset_in_byte))
        bit_offset_in_byte += 1
        if bit_offset_in_byte == 8:
            bit_offset_in_byte = 0
            byte_offset += 1
    return buffer


def append_bytes_to_buffer(data: bytes,
                           buffer: bytearray,
                           offset: int = 0,
                           ) -> bytearray:
    """Add bytes to a buffer at a bit offset.
    
    Allows appended data to be misaligned to byte boundaries in the buffer.
    
    Args:
        data (bytes): The bytes to add to the buffer.
        buffer (bytearray): The buffer to modify.
        offset (int): The bit offset to start from. Defaults to start of buffer.
    
    Returns:
        bytearray: The modified buffer.
    
    Raises:
        ValueError: If data, buffer or offset are invalid.
    """
    if not isinstance(data, (bytes, bytearray)):
        raise ValueError('Invalid data must be bytes-like.')
    if not isinstance(buffer, bytearray):
        raise ValueError('Invalid buffer must be a mutable bytearray.')
    if not isinstance(offset, int) or offset < 0:
        raise ValueError('Invalid bit offset must be positive integer.')
    byte_offset = offset // 8
    bit_offset_within_byte = offset % 8
    # Ensure buffer is large enough for the starting offet
    while len(buffer) <= byte_offset:
        buffer.append(0)
    for byte in data:
        if bit_offset_within_byte == 0:
            # Aligned to byte boundary simply append or overwrite
            if byte_offset < len(buffer):
                buffer[byte_offset] = byte
            else:
                buffer.append(byte)
        else:
            # If misaligned, split the byte across the boundary
            bits_to_write_in_current_byte = 8 - bit_offset_within_byte
            current_byte_mask = (byte >> bit_offset_within_byte) & 0xFF
            next_byte_mask = byte << bits_to_write_in_current_byte & 0xFF
            buffer[byte_offset] |= current_byte_mask
            if byte_offset + 1 >= len(buffer):
                buffer.append(0)
            buffer[byte_offset + 1] |= next_byte_mask
        byte_offset += 1
        bit_offset_within_byte = (bit_offset_within_byte + 8) % 8
    return buffer
