"""Floating point field class and methods."""

import struct

from pynimcodec.bitman import BitArray, append_bits_to_buffer, extract_from_buffer
from ..constants import FieldType
from .base_field import Field

FIELD_TYPE = FieldType.FLOAT


class FloatField(Field):
    """An unsigned integer field.
    
    Attributes:
        name (str): The unique field name.
        type (FieldType): The field type.
        description (str): Optional description for the field.
        optional (bool): Flag indicates if the field is optional in the message.
    """
    
    required_kwargs = ['size']
    
    def __init__(self, name: str, **kwargs) -> None:
        if not all(k in kwargs for k in self.required_kwargs):
            raise ValueError(f'Missing kwarg(s) from {self.required_kwargs}')
        kwargs.pop('type', None)
        super().__init__(name, FIELD_TYPE, **kwargs)
        self._size = 32
    
    @property
    def size(self) -> int:
        return self._size
    
    def decode(self, buffer: bytes, offset: int) -> 'tuple[int|float, int]':
        """Extracts the float value from a buffer."""
        return decode(self, buffer, offset)
    
    def encode(self,
               value: 'int|float',
               buffer: bytearray,
               offset: int,
               ) -> tuple[bytearray, int]:
        "Appends the float value to the buffer at the bit offset."
        return encode(self, value, buffer, offset)


def create(**kwargs) -> FloatField:
    """Create an FloatField."""
    return FloatField(**kwargs)


def decode(field: Field, buffer: bytes, offset: int) -> 'tuple[float, int]':
    """Decode a floating point field value from a buffer at a bit offset.
    
    Args:
        field (Field): The field definition, with `size` attribute.
        buffer (bytes): The encoded buffer to extract from.
        offset (int): The bit offset to extract from.
    
    Returns:
        tuple(float, int): The decoded value and the offset of the next
            field in the buffer.
    
    Raises:
        ValueError: If field is invalid.
    """
    if not isinstance(field, FloatField):
        raise ValueError('Invalid field definition.')
    x = extract_from_buffer(buffer, offset, field.size, as_buffer=True)
    value = struct.unpack('f', x)[0]
    return ( value, offset + field.size )


def encode(field: FloatField,
           value: float,
           buffer: bytearray,
           offset: int,
           ) -> 'tuple[bytearray, int]':
    """Append a floating point field value to a buffer at a bit offset.
    
    Args:
        field (IntField): The field definition.
        value (float): The value to encode.
        buffer (bytearray): The buffer to modify/append to.
        offset (int): The bit offset to append from.
    
    Returns:
        tuple(bytearray, int): The modified buffer and the offset of the next
            field.
    
    Raises:
        ValueError: If the field or value is invalid for the field definition.
    """
    if not isinstance(field, FloatField):
        raise ValueError('Invalid field definition.')
    if not isinstance(value, float):
        raise ValueError('Invalid value.')
    bits = BitArray.from_bytes(struct.pack('f', value), field.size)
    return ( append_bits_to_buffer(bits, buffer, offset), offset + field.size )
