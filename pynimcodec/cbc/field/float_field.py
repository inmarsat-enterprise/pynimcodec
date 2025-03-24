"""Floating point field class and methods."""

import struct
import warnings

from pynimcodec.bitman import BitArray, append_bits_to_buffer, extract_from_buffer
from pynimcodec.utils import snake_case

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
        size (int): The size in bits either 32 (default) or 64 (double)
        precision (int): The precision of the value when decoding (default 6)
    """
    
    def __init__(self, name: str, **kwargs) -> None:
        kwargs['type'] = FIELD_TYPE
        self._add_kwargs([], ['size', 'precision'])
        super().__init__(name, **kwargs)
        self._supported_sizes = [32, 64]
        self._size: int = 32
        self._precision: int = 6
        self.size = kwargs.pop('size', 32)
        self.precision = kwargs.pop('precision', 6)
    
    @property
    def size(self) -> int:
        return self._size
    
    @size.setter
    def size(self, value: int):
        if value is None:
            return
        if value not in self._supported_sizes:
            raise ValueError(f'Invalid size must be from [{self._supported_sizes}]')
        self._size = value
    
    @property
    def precision(self) -> int:
        """The number of decimal places to round to."""
        return self._precision
    
    @precision.setter
    def precision(self, value: int):
        if not isinstance(value, int) or value < 1:
            raise ValueError('Invalid precision must be int > 0')
        if self.size == 32 and value > 7:
            warnings.warn('Precision maximum 7 for 32-bit float')
        elif self.size == 64 and value < 8:
            warnings.warn('64-bit double not required for low precision')
        self._precision = value
    
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
    return FloatField(**{snake_case(k): v for k, v in kwargs.items()})


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
        raise ValueError('Invalid FloatField definition.')
    x = extract_from_buffer(buffer, offset, field.size, as_buffer=True)
    s_fmt = 'f' if field.size == 32 else 'd'
    value = round(struct.unpack(s_fmt, x)[0], field.precision)
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
    def value_precision(number: float) -> int:
        number_str = str(number)
        if '.' in number_str:
            return len(number_str.split('.')[1].rstrip('0'))
        return 0
    
    if not isinstance(field, FloatField):
        raise ValueError('Invalid FloatField definition.')
    if not isinstance(value, float):
        raise ValueError(f'Invalid {field.name} value.')
    value = round(value, value_precision(value))
    s_fmt = 'f' if field.size == 32 else 'd'
    bits = BitArray.from_bytes(struct.pack(s_fmt, value))
    return ( append_bits_to_buffer(bits, buffer, offset), offset + field.size )
