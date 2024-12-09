"""String field class and methods."""

from pynimcodec.bitman import append_bytes_to_buffer, extract_from_buffer
from ..constants import FieldType
from .base_field import Field
from .field_length import decode_field_length, encode_field_length

FIELD_TYPE = FieldType.STRING


class StringField(Field):
    """A string field.
    
    Attributes:
        name (str): The unique field name.
        type (FieldType): The field type.
        description (str): Optional description for the field.
        optional (bool): Flag indicates if the field is optional in the message.
        size (int): The maximum size of the string in bytes (characters).
        fixed (bool): Flag indicating if the value should be padded or truncated.
    """
    
    required_kwargs = ['size']
    optional_kwargs = ['fixed']
    
    def __init__(self, name: str, **kwargs) -> None:
        if not all(k in kwargs for k in self.required_kwargs):
            raise ValueError(f'Missing kwarg(s) from {self.required_kwargs}')
        kwargs.pop('type', None)
        super().__init__(name, FIELD_TYPE, **kwargs)
        self._size = 0
        self.size = kwargs.get('size')
        self._fixed = False
        self.fixed = kwargs.get('fixed', False)
    
    @property
    def size(self) -> int:
        return self._size
    
    @size.setter
    def size(self, value: int):
        if not isinstance(value, int) or value < 1:
            raise ValueError('Invalid size must be greater than 0.')
        self._size = value
    
    @property
    def fixed(self) -> bool:
        return self._fixed
    
    @fixed.setter
    def fixed(self, value: bool):
        if not isinstance(value, bool):
            raise ValueError('Invalid value for fixed.')
        self._fixed = value
    
    def decode(self, buffer: bytes, offset: int) -> 'tuple[int|float, int]':
        """Extracts the string value from a buffer."""
        return decode(self, buffer, offset)
    
    def encode(self,
               value: 'int|float',
               buffer: bytearray,
               offset: int,
               ) -> tuple[bytearray, int]:
        "Appends the string value to the buffer at the bit offset."
        return encode(self, value, buffer, offset)


def create(**kwargs) -> StringField:
    """Create a StringField."""
    return StringField(**kwargs)


def decode(field: Field, buffer: bytes, offset: int) -> 'tuple[str, int]':
    """Decode a string field value from a buffer at a bit offset.
    
    Args:
        field (Field): The field definition, with `size` attribute.
        buffer (bytes): The encoded buffer to extract from.
        offset (int): The bit offset to extract from.
    
    Returns:
        tuple(str, int): The decoded value and the offset of the next
            field in the buffer.
    
    Raises:
        ValueError: If field is invalid.
    """
    if not isinstance(field, StringField):
        raise ValueError('Invalid field definition.')
    if not field.fixed:
        length, offset = decode_field_length(buffer, offset)
    else:
        length = field.size
    value = extract_from_buffer(buffer, offset, length * 8, as_buffer=True).decode()
    return ( value, offset + length * 8 )


def encode(field: StringField,
           value: str,
           buffer: bytearray,
           offset: int,
           ) -> 'tuple[bytearray, int]':
    """Append a string field value to a buffer at a bit offset.
    
    Args:
        field (IntField): The field definition.
        value (str): The value to encode.
        buffer (bytearray): The buffer to modify/append to.
        offset (int): The bit offset to append from.
    
    Returns:
        tuple(bytearray, int): The modified buffer and the offset of the next
            field.
    
    Raises:
        ValueError: If the field or value is invalid for the field definition.
    """
    if not isinstance(field, StringField):
        raise ValueError('Invalid field definition.')
    if not isinstance(value, str):
        raise ValueError('Invalid value.')
    if len(value) > field.size:
        value = value[0:field.size]
    if field.fixed:
        while len(value) < field.size:
            value += ' '
    else:
        buffer, offset = encode_field_length(len(value), buffer, offset)
    return (
        append_bytes_to_buffer(value.encode(), buffer, offset),
        offset + len(value) * 8
    )
