"""Common encoding/decoding functions for all Fields."""

from typing import Any

from pynimcodec.bitman import extract_from_buffer
from ..constants import FieldType
from .base_field import Field
from . import (array_field, bitmask_field, bitmaskarray_field, bool_field,
               data_field, enum_field, float_field, int_field, string_field,
               struct_field, uint_field)

__all__ = ['create_field', 'decode_field', 'encode_field']


_codecs = {
    FieldType.ARRAY: array_field,
    FieldType.BITMASK: bitmask_field,
    FieldType.BITMASKARRAY: bitmaskarray_field,
    FieldType.BOOL: bool_field,
    FieldType.DATA: data_field,
    FieldType.ENUM: enum_field,
    FieldType.FLOAT: float_field,
    FieldType.INT: int_field,
    FieldType.STRING: string_field,
    FieldType.STRUCT: struct_field,
    FieldType.UINT: uint_field,
}


def create_field(obj: dict) -> Field:
    """Creates the appropriate field type based on a dictionary definition."""
    if not isinstance(obj, dict):
        raise ValueError('Invalid object to create field.')
    if 'type' not in obj or obj['type'] not in FieldType:
        raise ValueError('Invalid field type.')
    if 'fields' in obj:
        if not isinstance(obj['fields'], list):
            raise ValueError('Invalid fields definition')
        for i, field in enumerate(obj['fields']):
            obj['fields'][i] = create_field(field)
    return _codecs[FieldType(obj['type'])].create(**obj)


def decode_field(field: Field,
                 buffer: bytes,
                 offset: int,
                 ) -> 'tuple[dict, int]':
    """Decode a field to a dictionary."""
    if not isinstance(field, Field):
        raise ValueError('Invalid field.')
    if not isinstance(buffer, (bytes, bytearray)):
        raise ValueError('Invalid buffer must be bytes-like.')
    if not isinstance(offset, int) or offset < 0:
        raise ValueError('Invalid bit offset must be positive integer.')
    decoded = {}
    field_present = True
    if field.optional is True:
        field_present = extract_from_buffer(buffer, offset, 1) == 1
        offset += 1
    if field_present:
        # TODO lookup decoder based on type
        decoded = { 'name': field.name }
        decoded['value'], offset = _codecs[field.type].decode(field, buffer, offset)
    return ( decoded, offset )


def encode_field(field: Field,
                 value: Any,
                 buffer: bytearray,
                 offset: int,
                 ) -> 'tuple[bytearray, int]':
    """Append an encoded field value to a buffer at a bit offset."""
    if not isinstance(field, Field):
        raise ValueError('Invalid field.')
    if not isinstance(buffer, bytearray):
        raise ValueError('Invalid buffer must be mutable bytearray.')
    if not isinstance(offset, int) or offset < 0:
        raise ValueError('Invalid bit offset must be positive integer.')
    return _codecs[field.type].encode(field, value, buffer, offset)
