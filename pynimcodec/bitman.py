"""Utilities for bit manipulation."""

from typing import Any, Iterable, Optional


class BitArray:
    """An array of bits for bitwise manipulation.
    """
    # Internally backed by a bytearray for efficiency.

    def __init__(self, bits: Iterable[int] | None = None, length: int | None = None):
        if bits is None:
            bits = []
        bits = list(bits)
        if not all(b in (0, 1) for b in bits):
            raise ValueError('All elements must be 0 or 1.')
        if length is None:
            length = len(bits)
        if length < 0:
            raise ValueError('Length must be non-negative.')
        self._len = length
        self._bytes = bytearray((length + 7) // 8)
        for i, bit in enumerate(bits[:length]):
            if bit:
                self._bytes[i // 8] |= 1 << (7 - (i % 8))

    def __len__(self) -> int:
        return self._len

    def __getitem__(self, i: int | slice) -> 'int|BitArray':
        if isinstance(i, slice):
            start, stop, step = i.indices(self._len)
            bits = [self[j] for j in range(start, stop, step)]
            return BitArray(bits)   # type: ignore since j will not be a slice
        if not 0 <= i < self._len:
            raise IndexError
        b = self._bytes[i // 8]
        return (b >> (7 - (i % 8))) & 1

    def __setitem__(self, i: int, val: int):
        if val not in (0, 1):
            raise ValueError('Only 0 or 1 allowed.')
        if not 0 <= i < self._len:
            raise IndexError
        mask = 1 << (7 - (i % 8))
        if val:
            self._bytes[i // 8] |= mask
        else:
            self._bytes[i // 8] &= ~mask

    def __delitem__(self, index: int | slice) -> None:
        """Delete a bit or a slice of bits from the BitArray."""
        if isinstance(index, int):
            if not 0 <= index < self._len:
                raise IndexError("BitArray index out of range")
            # Convert all bits to a list, remove the bit, and rebuild
            bits = [self[i] for i in range(self._len)]
            del bits[index]
            self.__init__(bits)   # type: ignore
        elif isinstance(index, slice):
            start, stop, step = index.indices(self._len)
            bits = [self[i] for i in range(self._len)]
            # delete slice
            del bits[start:stop:step]
            self.__init__(bits)   # type: ignore
        else:
            raise TypeError(f"BitArray indices must be int or slice, not {type(index).__name__}")

    def __repr__(self):
        return f'BitArray({[self[i] for i in range(self._len)]})'

    def __str__(self):
        bits = ''.join(str(self[i]) for i in range(self._len))
        return f'0b{bits}'

    # -------------------------------------------------------------------------
    # Constructors
    # -------------------------------------------------------------------------
    @classmethod
    def from_int(cls, value: int, length: int | None = None) -> 'BitArray':
        if not isinstance(value, int):
            raise ValueError('Invalid integer')

        if length is None:
            length = max(1, value.bit_length() + (1 if value < 0 else 0))
        if length <= 0:
            raise ValueError('Length must be positive')

        if value < 0:
            value = (1 << length) + value  # two's complement

        bits = [(value >> i) & 1 for i in reversed(range(length))]
        return cls(bits, length)

    @classmethod
    def from_bytes(cls, data: bytes | bytearray) -> 'BitArray':
        if not isinstance(data, (bytes, bytearray)):
            raise ValueError('Invalid bytes input.')
        bits = []
        for byte in data:
            bits.extend((byte >> i) & 1 for i in reversed(range(8)))
        return cls(bits)

    # -------------------------------------------------------------------------
    # Conversions
    # -------------------------------------------------------------------------
    def to_int(self, signed: bool = False) -> int:
        value = 0
        for i in range(self._len):
            value = (value << 1) | self[i]   # type: ignore self[i] is int
        if signed and self[0]:
            value -= (1 << self._len)
        return value

    def to_bytes(self) -> bytes:
        return bytes(self._bytes[: (self._len + 7) // 8])

    # -------------------------------------------------------------------------
    # Mutations
    # -------------------------------------------------------------------------
    def append(self, value: int) -> None:
        if value not in (0, 1):
            raise ValueError('Only 0 or 1 allowed.')
        byte_index = self._len // 8
        bit_index = self._len % 8
        if bit_index == 0:
            self._bytes.append(0)
        if value:
            self._bytes[byte_index] |= 1 << (7 - bit_index)
        self._len += 1

    def extend(self, iterable: Iterable[int]) -> None:
        for bit in iterable:
            self.append(bit)

    def insert(self, index: int, value: Any) -> None:
        """Insert a bit at position index."""
        if not isinstance(index, int) or not 0 <= index <= self._len:
            raise IndexError
        if value not in (0, 1):
            raise ValueError('Only 0 or 1 allowed.')
        bits = [self[i] for i in range(self._len)]
        bits.insert(index, value)
        self.__init__(bits)   # type: ignore bits will always be list[int]

    # -------------------------------------------------------------------------
    # Bitwise Operations
    # -------------------------------------------------------------------------
    def lshift(self, n: int = 1, extend: bool = True) -> None:
        if not isinstance(n, int) or n < 1:
            raise ValueError('n must be > 0.')
        bits = [self[i] for i in range(self._len)]
        bits = bits[n:] + [0] * n if not extend else bits + [0] * n
        self.__init__(bits[:self._len] if not extend else bits)   # type: ignore bits is always list[int]

    def rshift(self, n: int = 1, preserve: bool = True) -> None:
        if not isinstance(n, int) or n < 1:
            raise ValueError('n must be > 0.')
        bits = [self[i] for i in range(self._len)]
        if preserve:
            bits = [0] * n + bits[:-n]
        else:
            bits = bits[:-n]
        self.__init__(bits)   # type: ignore

    # -------------------------------------------------------------------------
    # Read helpers
    # -------------------------------------------------------------------------
    def read_int(self, signed: bool = False, start: int = 0, end: int | None = None) -> int:
        if end is None:
            end = self._len
        if not (0 <= start < end <= self._len):
            raise ValueError('Invalid start/end.')
        bits = [self[i] for i in range(start, end)]
        value = 0
        for bit in bits:
            value = (value << 1) | bit   # type: ignore
        if signed and bits[0]:
            value -= (1 << len(bits))
        return value

    def read_bytes(self, start: int = 0, end: int | None = None) -> bytes:
        if end is None:
            end = self._len
        bits = [self[i] for i in range(start, end)]
        result = bytearray((len(bits) + 7) // 8)
        for i, bit in enumerate(bits):
            if bit:
                result[i // 8] |= 1 << (7 - (i % 8))
        return bytes(result)


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
                        length: Optional[int] = None,
                        signed: bool = False,
                        as_buffer: bool = False,
                        new_offset: bool = False,
                        ) -> 'int|bytes|tuple[int|bytes, int]':
    """Extract the value of bits from a buffer at a bit offset.
    
    Args:
        buffer (bytes): The buffer to extract from.
        offset (int): The bit offset to start from.
        length (int): The number of bits to extract. If None, extracts to the
            end of the buffer.
        signed (bool): If True will extract a signed value (two's complement).
        as_buffer (bool): Return a `bytes` buffer (default returns `int`).
        new_offset (bool): Include the new bit offset after the read.
    
    Returns:
        int|bytes|tuple: The extracted value. If `new_offset` is set a tuple
            is returned with the value and the new bit offset
    
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
    bit_array = BitArray.from_bytes(buffer[start_byte:end_byte])
    start_bit = offset % 8
    end_bit = start_bit + length
    if as_buffer is True:
        return bit_array.read_bytes(start_bit, end_bit)
    return bit_array.read_int(signed, start_bit, end_bit)


def append_bits_to_buffer(bit_array: BitArray,
                          buffer: 'bytearray|bytes',
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
    if not isinstance(buffer, (bytearray, bytes)):
        raise ValueError('Invalid buffer')
    if not isinstance(offset, int) or offset < 0:
        raise ValueError('offset must be a non-negative integer')
    newbuffer = bytearray(buffer)
    if len(newbuffer) == 0:
        newbuffer.append(0)
    if offset > len(newbuffer) * 8:
        raise ValueError(f'offset {offset} exceeds the current buffer size.')
    total_bits = offset + len(bit_array)
    required_bytes = (total_bits + 7) // 8
    while len(newbuffer) < required_bytes:
        newbuffer.append(0)
    byte_offset = offset // 8
    bit_offset_in_byte = offset % 8
    for bit in bit_array:
        if bit == 1:
            newbuffer[byte_offset] |= (1 << (7 - bit_offset_in_byte))
        else:
            newbuffer[byte_offset] &= ~(1 << (7 - bit_offset_in_byte))
        bit_offset_in_byte += 1
        if bit_offset_in_byte == 8:
            bit_offset_in_byte = 0
            byte_offset += 1
    return newbuffer


def append_bytes_to_buffer(data: bytes,
                           buffer: 'bytearray|bytes',
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
    if not isinstance(buffer, (bytearray, bytes)):
        raise ValueError('Invalid buffer must be bytes-like.')
    if not isinstance(offset, int) or offset < 0:
        raise ValueError('Invalid bit offset must be positive integer.')
    byte_offset = offset // 8
    bit_offset = offset % 8   # within byte
    newbuffer = bytearray(buffer)
    # Ensure buffer is large enough for the starting offet
    while len(newbuffer) <= byte_offset:
        newbuffer.append(0)
    for byte in data:
        if bit_offset == 0:
            # Aligned to byte boundary simply append or overwrite
            if byte_offset < len(newbuffer):
                newbuffer[byte_offset] = byte
            else:
                newbuffer.append(byte)
        else:
            # If misaligned, split the byte across the boundary
            bits_to_write = 8 - bit_offset   # in currrent byte
            current_byte_mask = (byte >> bit_offset) & 0xFF
            # preserve bits not being overwritten
            newbuffer[byte_offset] &= ((0xFF << bits_to_write) & 0xFF)
            # write new bits
            newbuffer[byte_offset] |= current_byte_mask
            if byte_offset + 1 >= len(buffer):
                newbuffer.append(0)
            next_byte_mask = byte << bits_to_write & 0xFF
            newbuffer[byte_offset + 1] |= next_byte_mask
        byte_offset += 1
        bit_offset = (bit_offset + 8) % 8
    return newbuffer
