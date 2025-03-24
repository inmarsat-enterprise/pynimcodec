"""Bitmask Array field class and methods."""

from pynimcodec.bitman import (
    BitArray,
    append_bits_to_buffer,
    append_bytes_to_buffer,
    extract_from_buffer,
)
from pynimcodec.utils import snake_case

from ..constants import FieldType
from .base_field import Field, Fields
from .enum import valid_enum

FIELD_TYPE = FieldType.BITMASKARRAY


class BitmaskArrayField(Field):
    """A bitmask array field.
    
    Combines a bitmask with an array such that the bitmask provides a key to
    which rows are populated.
    
    Attributes:
        name (str): The unique field name.
        type (FieldType): The field type.
        description (str): Optional description for the field.
        optional (bool): Flag indicates if the field is optional in the message.
        size (int): The maximum size of the bitmask (bits) and array (rows).
        enum (dict): A dictionary of numerically-keyed strings representing
            meaning of the bits e.g. {"0": "LSB", "8": "MSB"}
        fields (Field[]): A list of fields defining columns of the array.
    """
    
    def __init__(self, name: str, **kwargs) -> None:
        kwargs['type'] = FIELD_TYPE
        self._add_kwargs(['size', 'enum', 'fields'], [])
        super().__init__(name, **kwargs)
        self._size: int = 0
        self._enum: 'dict[str, str]' = {}
        self._fields: Fields = Fields()
        self.size = kwargs.pop('size')
        self.enum = kwargs.pop('enum')
        self.fields = kwargs.pop('fields')
    
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
        self._enum = valid_enum(self.size, keys_values, bitmask=True)
    
    @property
    def _max_value(self) -> int:
        return 2**self.size - 1
    
    @property
    def fields(self) -> 'list[Field]':
        return self._fields
    
    @fields.setter
    def fields(self, fields: 'list[Field]'):
        if (not isinstance(fields, list) or
            not all(isinstance(x, Field) for x in fields)):
            raise ValueError('Invalid list of fields')
        self._fields = fields
    
    def decode(self, buffer: bytes, offset: int) -> 'tuple[int|float, int]':
        """Extracts the array value from a buffer."""
        return decode(self, buffer, offset)
    
    def encode(self,
               value: 'int|float',
               buffer: bytearray,
               offset: int,
               ) -> tuple[bytearray, int]:
        "Appends the array value to the buffer at the bit offset."
        return encode(self, value, buffer, offset)


def create(**kwargs) -> BitmaskArrayField:
    """Create a BitmaskArrayField."""
    return BitmaskArrayField(**{snake_case(k): v for k, v in kwargs.items()})


def decode(field: Field, buffer: bytes, offset: int) -> 'tuple[dict, int]':
    """Decode an array field value from a buffer at a bit offset.
    
    Args:
        field (Field): The field definition, with `size` attribute.
        buffer (bytes): The encoded buffer to extract from.
        offset (int): The bit offset to extract from.
    
    Returns:
        tuple(dict, int): The decoded dictionary of lists and the offset of the
            next field in the buffer.
    
    Raises:
        ValueError: If field is invalid.
    """
    if not isinstance(field, BitmaskArrayField):
        raise ValueError('Invalid BitmaskArrayField definition.')
    bitmask = extract_from_buffer(buffer, offset, field.size)
    offset += field.size
    value_keys = []
    bits = BitArray.from_int(bitmask)
    for i, bit in enumerate(reversed(bits)):
        if bit:
            value_keys.append(field.enum[f'{i}'])
    value = { k: [] for k in value_keys }
    for row in range(bin(bitmask).count('1')):
        decoded = {} if len(field.fields) > 1 else None
        for col in field.fields:
            if col.optional:
                present = extract_from_buffer(buffer, offset, 1)
                offset += 1
                if not present:
                    continue
            if len(field.fields) == 1:
                decoded, offset = col.decode(buffer, offset)
            else:
                decoded[col.name], offset = col.decode(buffer, offset)
        value[value_keys[row]].append(decoded)
    return ( value, offset )


def encode(field: BitmaskArrayField,
           value: 'dict[str, list]',
           buffer: bytearray,
           offset: int,
           ) -> 'tuple[bytearray, int]':
    """Append an array field values to a buffer at a bit offset.
    
    Args:
        field (IntField): The field definition.
        value (dict[str, list]): The dictionary of lists to encode.
        buffer (bytearray): The buffer to modify/append to.
        offset (int): The bit offset to append from.
    
    Returns:
        tuple(bytearray, int): The modified buffer and the offset of the next
            field.
    
    Raises:
        ValueError: If the field or value is invalid for the field definition.
    """
    if not isinstance(field, BitmaskArrayField):
        raise ValueError('Invalid BitmaskArrayField definition.')
    if (not isinstance(value, dict) or
        not all(isinstance(x, list) for x in value.values())):
        raise ValueError(f'Invalid {field.name} value array.')
    bitmask = 0
    tmp_buffer = bytearray()
    tmp_offset = 0
    for k, v in value.items():
        if k not in field.enum.values():
            raise ValueError(f'{k} not found in {field.name} enumeration.')
        for ek, ev in field.enum.items():
            if ev == k:
                bitmask += 2**int(ek)
        for i, row in enumerate(v):
            for col in field.fields:
                if col.optional:
                    present = 1 if not isinstance(row, dict) or col.name in row else 0
                    buffer = append_bits_to_buffer([present], buffer, offset)
                    offset += 1
                    if not present:
                        continue
                if not isinstance(row, dict):
                    if len(field.fields) > 1:
                        raise ValueError(f'{field.name} row {i} missing column keys')
                    tmp_buffer, tmp_offset = col.encode(row, tmp_buffer, tmp_offset)
                else:
                    if col.name not in row:
                        raise ValueError(f'{field.name} row {i} missing {col.name}')
                    tmp_buffer, tmp_offset = col.encode(row[col.name], tmp_buffer, tmp_offset)
    buffer = append_bits_to_buffer(BitArray.from_int(bitmask, field.size), buffer)
    offset += field.size
    buffer = append_bytes_to_buffer(bytes(tmp_buffer), buffer, offset)
    offset += tmp_offset
    return ( buffer, offset )
