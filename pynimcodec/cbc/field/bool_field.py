"""Boolean field class and methods."""

from pynimcodec.bitman import append_bits_to_buffer, extract_from_buffer
from ..constants import FieldType
from .base_field import Field

FIELD_TYPE = FieldType.BOOL


class BoolField(Field):
    """A boolean field.
    
    Attributes:
        name (str): The unique field name.
        type (FieldType): The field type.
        description (str): Optional description for the field.
        optional (bool): Flag indicates if the field is optional in the message.
    """
    
    def __init__(self, name: str, **kwargs) -> None:
        kwargs.pop('type', None)
        super().__init__(name, FIELD_TYPE, **kwargs)
    
    def decode(self, buffer: bytes, offset: int) -> 'tuple[int|float, int]':
        """Extracts the boolean value from a buffer."""
        return decode(self, buffer, offset)
    
    def encode(self,
               value: 'int|float',
               buffer: bytearray,
               offset: int,
               ) -> tuple[bytearray, int]:
        "Appends the boolean value to the buffer at the bit offset."
        return encode(self, value, buffer, offset)


def create(**kwargs) -> BoolField:
    """Create a BoolField."""
    return BoolField(**kwargs)


def decode(field: Field, buffer: bytes, offset: int) -> 'tuple[int|float, int]':
    """Decode a boolean field value from a buffer at a bit offset.
    
    Args:
        field (Field): The field definition, with `size` attribute.
        buffer (bytes): The encoded buffer to extract from.
        offset (int): The bit offset to extract from.
    
    Returns:
        tuple(bool, int): The decoded value and the offset of the next
            field in the buffer.
    
    Raises:
        ValueError: If field is invalid.
    """
    if not isinstance(field, BoolField):
        raise ValueError('Invalid field definition.')
    value = extract_from_buffer(buffer, offset, 1)
    return ( bool(value), offset + 1 )


def encode(field: BoolField,
           value: bool,
           buffer: bytearray,
           offset: int,
           ) -> 'tuple[bytearray, int]':
    """Append a boolean field value to a buffer at a bit offset.
    
    Args:
        field (IntField): The field definition.
        value (bool): The value to encode.
        buffer (bytearray): The buffer to modify/append to.
        offset (int): The bit offset to append from.
    
    Returns:
        tuple(bytearray, int): The modified buffer and the offset of the next
            field.
    
    Raises:
        ValueError: If the field or value is invalid for the field definition.
    """
    if not isinstance(field, BoolField):
        raise ValueError('Invalid field definition.')
    if not isinstance(value, bool):
        raise ValueError('Invalid boolean value.')
    return ( append_bits_to_buffer([int(value)], buffer, offset), offset + 1 )
