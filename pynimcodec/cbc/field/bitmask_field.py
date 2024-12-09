"""Bitmask field class and methods."""

from pynimcodec.bitman import BitArray, append_bits_to_buffer, extract_from_buffer
from ..constants import FieldType
from .base_field import Field

FIELD_TYPE = FieldType.BITMASK


class BitmaskField(Field):
    """A bitmask enumerated value field.
    
    Attributes:
        name (str): The unique field name.
        type (FieldType): The field type.
        description (str): Optional description for the field.
        optional (bool): Flag indicates if the field is optional in the message.
        size (int): The size of the encoded field in bits.
        enum (dict): A dictionary of numerically-keyed strings representing
            meaning of the bits.
    """
    
    required_kwargs = ['size', 'enum']
    
    def __init__(self, name: str, **kwargs) -> None:
        if not all(k in kwargs for k in self.required_kwargs):
            raise ValueError(f'Missing kwarg(s) from {self.required_kwargs}')
        kwargs.pop('type', None)
        super().__init__(name, FIELD_TYPE, **kwargs)
        self._size = 0
        self.size = kwargs.get('size')
        self._enum = {}
        if kwargs.get('enum'):
            self.enum = kwargs.get('enum')
    
    @property
    def size(self) -> int:
        return self._size
    
    @size.setter
    def size(self, value: int):
        if not isinstance(value, int) or value < 1:
            raise ValueError('Invalid size must be greater than 0.')
        self._size = value
    
    @property
    def enum(self) -> 'dict[str, str]':
        return self._enum
    
    @enum.setter
    def enum(self, keys_values: 'dict[str, str]'):
        if not isinstance(keys_values, dict) or not keys_values:
            raise ValueError('Invalid enumeration dictionary.')
        for k in keys_values:
            try:
                key_int = int(k)
                if key_int < 0 or key_int > self.size:
                    errmsg = f'Key {k} must be in range 0..{self.size}.'
                    raise ValueError(errmsg)
            except ValueError as exc:
                errmsg = f'Invalid key {k} must be integer parsable.'
                raise ValueError(errmsg) from exc
        seen = set()
        for v in keys_values.values():
            if not isinstance(v, str):
                raise ValueError('Invalid enumeration value must be string.')
            if v in seen:
                raise ValueError('Duplicate value found in list')
            seen.add(v)
        self._enum = keys_values
    
    @property
    def _max_value(self) -> int:
        return 2**self.size - 1
    
    def decode(self, buffer: bytes, offset: int) -> 'tuple[int|float, int]':
        """Extracts the bitmask value from a buffer."""
        return decode(self, buffer, offset)
    
    def encode(self,
               value: 'int|float',
               buffer: bytearray,
               offset: int,
               ) -> tuple[bytearray, int]:
        "Appends the bitmask value to the buffer at the bit offset."
        return encode(self, value, buffer, offset)


def create(**kwargs) -> BitmaskField:
    """Create an BitmaskField."""
    return BitmaskField(**kwargs)


def decode(field: Field, buffer: bytes, offset: int) -> 'tuple[list[str], int]':
    """Decode a bitmask field value from a buffer at a bit offset.
    
    Args:
        field (Field): The field definition, with `size` attribute.
        buffer (bytes): The encoded buffer to extract from.
        offset (int): The bit offset to extract from.
    
    Returns:
        tuple(str, int): The decoded list of set bits and the offset of the next
            field in the buffer.
    
    Raises:
        ValueError: If field is invalid.
    """
    if not isinstance(field, BitmaskField):
        raise ValueError('Invalid field definition.')
    bits = BitArray.from_int(extract_from_buffer(buffer, offset, field.size))
    value = []
    for i, bit in enumerate(reversed(bits)):
        if bit:
            value.append(field.enum[f'{i}'] or f'UNDEFINED({i})')
    return ( value, offset + field.size )


def encode(field: BitmaskField,
           value: 'list[str]|int',
           buffer: bytearray,
           offset: int,
           ) -> 'tuple[bytearray, int]':
    """Append a bitmask field value to a buffer at a bit offset.
    
    Args:
        field (IntField): The field definition.
        value (list[str]|int): The value to encode, either as a list of
            enumerated bit names or a raw integer of the bitmask.
        buffer (bytearray): The buffer to modify/append to.
        offset (int): The bit offset to append from.
    
    Returns:
        tuple(bytearray, int): The modified buffer and the offset of the next
            field.
    
    Raises:
        ValueError: If the field or value is invalid for the field definition.
    """
    if not isinstance(field, BitmaskField):
        raise ValueError('Invalid field definition.')
    if not isinstance(value, (list, int)):
        raise ValueError('Invalid value.')
    if isinstance(value, list):
        if not all(isinstance(x, str) for x in value):
            raise ValueError('Invalid list all values must be string type.')
        value_int = 0
        for s in value:
            if s not in field.enum.values():
                raise ValueError(f'{s} not found in bitmask')
            for k, v in field.enum.items():
                if v == s:
                    value_int += 2**int(k)
                    break   # from enum iteration
        value = value_int
    if value < 0 or value > field._max_value:
        raise ValueError(f'Invalid value must be in range 0..{field._max_value}')
    bits = BitArray.from_int(value, field.size)
    return ( append_bits_to_buffer(bits, buffer, offset), offset + field.size )
