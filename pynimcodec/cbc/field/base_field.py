"""Base class for all Fields."""

from enum import Enum
from typing import Any

from pynimcodec.bitman import append_bits_to_buffer, extract_from_buffer
from pynimcodec.cbc.codec.base_codec import CbcCodec
from pynimcodec.utils import camel_case

from ..constants import FieldType
from ..codec.base_codec import CodecList


class Field(CbcCodec):
    """Base type for all fields."""
    
    required_args = ['name', 'type']
    
    def __init__(self, name: str, type: FieldType, **kwargs) -> None:
        super().__init__(name, kwargs.pop('description', None))
        self._type: FieldType = None
        self.type = type
        self._optional: bool = False
        self.optional = kwargs.get('optional', False)
    
    @property
    def type(self) -> FieldType:
        return self._type
    
    @type.setter
    def type(self, field_type: 'FieldType|str'):
        if (not isinstance(field_type, (FieldType, str)) or
            field_type not in FieldType):
            raise ValueError('Invalid field_type.')
        self._type = field_type
    
    @property
    def optional(self) -> bool:
        return self._optional
    
    @optional.setter
    def optional(self, value: bool):
        if not isinstance(value, bool):
            raise ValueError('Invalid boolean for optional.')
        self._optional = value
    
    def to_json(self):
        key_order = ['name', 'type', 'description', 'size', 'optional', 'fixed']
        raw = {}
        for attr_name in dir(self.__class__):
            if (not isinstance(getattr(self.__class__, attr_name), property) or
                attr_name.startswith('_') or
                getattr(self, attr_name) is None or
                getattr(self, attr_name) in ['']):
                # skip
                continue
            elif (attr_name in ['optional', 'fixed'] and
                  getattr(self, attr_name) is False):
                continue
            elif isinstance(getattr(self, attr_name), Fields):
                raw[attr_name] = []
                for fld in getattr(self, attr_name):
                    raw[attr_name].append(fld.to_json())
            elif (issubclass(getattr(self, attr_name).__class__, Enum)):
                raw[attr_name] = getattr(self, attr_name).value
            else:
                raw[attr_name] = getattr(self, attr_name)
        reordered = { camel_case(k): raw[k] for k in key_order if k in raw }
        remaining = { camel_case(k): raw[k] for k in raw if k not in key_order }
        reordered.update(remaining)
        return reordered
        
    def decode(self, buffer: bytes, offset: int) -> 'tuple[Any, int]':
        """Decodes the field value from a buffer at a bit offset.
        
        Allows nested child fields for arrays and structs.
        
        Args:
            buffer (bytes): The buffer to decode from.
            offset (int): The bit offset to decode from.
        
        Returns:
            tuple(Any, int): The decoded type-specific field value and the
                offset of the next field in the buffer.
        """
        raise NotImplementedError('Must be implemented in subclass')
    
    def encode(self,
               value: Any,
               buffer: bytearray,
               offset: int,
               ) -> 'tuple[bytearray, int]':
        """Appends the field value to a buffer at a bit offset.
        
        Allows nested child fields for arrays and structs.
        
        Args:
            value (Any): The type-specific value of the field to encode.
            buffer (bytearray): The buffer to append the encoded field to.
            offset (int): The bit offset within the buffer to write to.
        
        Returns:
            tuple(bytearray, int): The modified buffer and the bit offset for
                the next field within the buffer.
        """
        raise NotImplementedError('Must be implemented in subclass')


class Fields(CodecList[Field]):
    """Container class for a list of Field codecs."""
    
    def __init__(self, *args) -> None:
        super().__init__(Field, *args)


def decode_fields(codec: CbcCodec,
                  buffer: bytes,
                  offset: int,
                  ) -> 'tuple[list[dict], int]':
    """Decodes field values from a buffer for a codec with fields.
    
    Args:
        codec (CbcCodec): The codec with fields definition.
        buffer (bytes): The buffer to decode from.
        offset (int): The bit offset in the buffer to decode from.
    
    Returns:
        tuple(list, int): The decoded fields list and offet resulting.
    """
    fields: Fields = getattr(codec, 'fields')
    if not fields:
        raise ValueError('Codec has no fields attribute.')
    values = []
    for field in fields:
        if field.optional:
            present = extract_from_buffer(buffer, offset, 1)
            offset += 1
            if not present:
                continue
        value, offset = field.decode(buffer, offset)
        values.append({field.name: value})
    return ( values, offset )


def encode_fields(content: dict,
                  codec: CbcCodec,
                  buffer: bytearray,
                  offset: int,
                  ) -> 'tuple[bytearray, int]':
    """Encodes fields from a dictionary with fields values.
    
    Args:
        content (dict): The content of the object containing fields.
            Could be a Message or a Field.
        codec (CbcCodec): The codec definition.
        buffer (bytearray): The buffer to append to.
        offset (int): The bit offset to start appending from.
    
    Returns:
        tuple(bytearray, int): The resulting buffer and offset.
    
    Raises:
        ValueError: If the content or codec is missing `fields` definition.
    """
    
    def get_content_field(name: str) -> 'Field|None':
        """Get a field object from a parent object with value key."""
        for cfield in content['value']:
            assert isinstance(cfield, dict)
            if name in cfield:
                return cfield[name]
    
    if not isinstance(content, dict) or 'value' not in content:
        raise ValueError('Content missing value.')
    fields: Fields = getattr(codec, 'fields')
    if not fields:
        raise ValueError('Codec has no fields attribute.')
    for i, value in enumerate(content['value']):
        if not isinstance(value, dict):
            raise ValueError(f'Invalid fields row {i} must be dictionary.')
        cname = list(value.keys())[0]
        if not any(field.name == cname for field in fields):
            raise ValueError(f'No field {cname} found in codec {codec.name}.')
    for field in fields:
        value = get_content_field(field.name)
        if value is not None:
            if field.optional is True:
                buffer = append_bits_to_buffer([1], buffer, offset)
                offset += 1
            buffer, offset = field.encode(value, buffer, offset)
        elif field.optional is True:
            buffer = append_bits_to_buffer([0], buffer, offset)
            offset += 1
        else:
            raise ValueError(f'Missing required field {field.name}')
    return ( buffer, offset )
