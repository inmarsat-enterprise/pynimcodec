"""Unsigned integer field class and methods."""

from pynimcodec.bitman import BitArray, append_bits_to_buffer, extract_from_buffer
from ..constants import FieldType
from .base_field import Field
from .calc import calc_encode, calc_decode

FIELD_TYPE = FieldType.UINT


class UintField(Field):
    """An unsigned integer field.
    
    Attributes:
        name (str): The unique field name.
        type (FieldType): The field type.
        description (str): Optional description for the field.
        optional (bool): Flag indicates if the field is optional in the message.
        size (int): The size of the encoded field in bits.
        encalc (str): Optional pre-encoding math expression to apply to value.
        decalc (str): Optional post-decoding math expression to apply to value.
    """
    
    required_kwargs = ['size']
    optional_kwargs = ['calc', 'decalc']
    
    def __init__(self, name: str, **kwargs) -> None:
        if not all(k in kwargs for k in self.required_kwargs):
            raise ValueError(f'Missing kwarg(s) from {self.required_kwargs}')
        kwargs.pop('type', None)
        super().__init__(name, FIELD_TYPE, **kwargs)
        self._size = 0
        self.size = kwargs.get('size')
        self._encalc = ''
        self.encalc = kwargs.get('encalc', '')
        self._decalc = ''
        self.decalc = kwargs.get('decalc', '')
    
    @property
    def size(self) -> int:
        return self._size
    
    @size.setter
    def size(self, value: int):
        if not isinstance(value, int) or value < 1:
            raise ValueError('Invalid size must be greater than 0.')
        self._size = value
    
    @property
    def encalc(self) -> str:
        return self._encalc
    
    @encalc.setter
    def encalc(self, expr: str):
        try:
            calc_encode(expr, -1)
            self._encalc = expr
        except TypeError as exc:
            raise ValueError('Invalid expression.') from exc
    
    @property
    def decalc(self) -> str:
        return self._decalc
    
    @decalc.setter
    def decalc(self, expr: str):
        try:
            calc_decode(expr, -1)
            self._decalc = expr
        except TypeError as exc:
            raise ValueError('Invalid expression.') from exc
    
    @property
    def _max_value(self) -> int:
        return 2**self.size - 1
    
    def decode(self, buffer: bytes, offset: int) -> 'tuple[int|float, int]':
        """Extracts the unsigned integer value from a buffer."""
        return decode(self, buffer, offset)
    
    def encode(self,
               value: 'int|float',
               buffer: bytearray,
               offset: int,
               ) -> tuple[bytearray, int]:
        "Appends the unsigned integer value to the buffer at the bit offset."
        return encode(self, value, buffer, offset)


def create(**kwargs) -> UintField:
    """Create an UintField."""
    return UintField(**kwargs)


def decode(field: Field, buffer: bytes, offset: int) -> 'tuple[int|float, int]':
    """Decode an unsigned integer field value from a buffer at a bit offset.
    
    If the field has `decalc` attribute populated it will apply the math
    expression.
    
    Args:
        field (Field): The field definition, with `size` attribute.
        buffer (bytes): The encoded buffer to extract from.
        offset (int): The bit offset to extract from.
    
    Returns:
        tuple(int|float, int): The decoded value and the offset of the next
            field in the buffer.
    
    Raises:
        ValueError: If field is invalid.
    """
    if not isinstance(field, UintField):
        raise ValueError('Invalid field definition.')
    value = extract_from_buffer(buffer, offset, field.size)
    if field.decalc:
        value = calc_decode(field.decalc, value)
    return ( value, offset + field.size )


def encode(field: UintField,
           value: 'int|float',
           buffer: bytearray,
           offset: int,
           ) -> 'tuple[bytearray, int]':
    """Append an unsigned integer field value to a buffer at a bit offset.
    
    Args:
        field (IntField): The field definition.
        value (int|float): The value to encode. Floats are only allowed if
            'encalc' specifies an integer conversion.
        buffer (bytearray): The buffer to modify/append to.
        offset (int): The bit offset to append from.
    
    Returns:
        tuple(bytearray, int): The modified buffer and the offset of the next
            field.
    
    Raises:
        ValueError: If the field or value is invalid for the field definition.
    """
    if not isinstance(field, UintField):
        raise ValueError('Invalid field definition.')
    if ((not isinstance(value, int) and
         not (isinstance(value, float) and field.encalc)) or value < 0):
        raise ValueError('Invalid value.')
    if field.encalc:
        value = calc_encode(field.encalc, value)
    elif not isinstance(value, int):
        raise ValueError('Invalid unsigned integer value.')
    if value > field._max_value:
        raise ValueError(f'Value too large to encode in {field.size} bits.')
    bits = BitArray.from_int(value, field.size)
    return ( append_bits_to_buffer(bits, buffer, offset), offset + field.size )
