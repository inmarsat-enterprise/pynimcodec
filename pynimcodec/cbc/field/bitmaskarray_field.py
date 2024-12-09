"""Bitmask Array field class and methods."""

from pynimcodec.bitman import BitArray, append_bits_to_buffer, extract_from_buffer, append_bytes_to_buffer
from ..constants import FieldType
from .base_field import Field

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
            meaning of the bits.
        fields (Field[]): A list of fields defining columns of the array.
    """
    
    required_kwargs = ['size', 'enum', 'fields']
    
    def __init__(self, name: str, **kwargs) -> None:
        if not all(k in kwargs for k in self.required_kwargs):
            raise ValueError(f'Missing kwarg(s) from {self.required_kwargs}')
        kwargs.pop('type', None)
        super().__init__(name, FIELD_TYPE, **kwargs)
        self._size = 0
        self.size = kwargs.get('size')
        self._fields = []
        self.fields = kwargs.get('fields')
    
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
    return BitmaskArrayField(**kwargs)


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
        raise ValueError('Invalid field definition.')
    bitmask, offset = extract_from_buffer(buffer, offset, field.size)
    value_keys = []
    bits = BitArray.from_int(bitmask)
    for i, bit in enumerate(reversed(bits)):
        if bit:
            value_keys.append(f'{i}')
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
        raise ValueError('Invalid field definition.')
    if (not isinstance(value, dict) or
        not all(isinstance(x, list) for x in value.values())):
        raise ValueError('Invalid value array.')
    bitmask = 0
    for k in value:
        if k not in field.enum.values():
            raise ValueError(f'{k} not found in field enumeration.')
        for ek, ev in field.enum.items():
            if ev == k:
                bitmask += 2**int(ek)
    tmp_buffer = bytearray()
    tmp_offset = 0
    for i, row in enumerate(value):
        for col in field.fields:
            if col.optional:
                present = 1 if not isinstance(row, dict) or col.name in row else 0
                buffer = append_bits_to_buffer([present], buffer, offset)
                offset += 1
                if not present:
                    continue
            if not isinstance(row, dict):
                if len(field.fields) > 1:
                    raise ValueError(f'Row {i} missing column keys')
                tmp_buffer, tmp_offset = col.encode(row, tmp_buffer, tmp_offset)
            else:
                if col.name not in row:
                    raise ValueError(f'Row {i} missing {col.name}')
                tmp_buffer, tmp_offset = col.encode(row[col.name], tmp_buffer, tmp_offset)
    buffer = append_bits_to_buffer(BitArray.from_int(bitmask, field.size))
    buffer = append_bytes_to_buffer(bytes(tmp_buffer), buffer, offset)
    return ( buffer, offset + field.size + len(tmp_buffer) )
