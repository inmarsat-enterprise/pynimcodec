"""Utilities for processing a Message Definitions collection of Services."""
import json
import logging
import os
from collections import OrderedDict

from . import ET, XML_NAMESPACE
from .fields import (
    ArrayField,
    BitmaskListField,
    BooleanField,
    DataField,
    EnumField,
    SignedIntField,
    StringField,
    UnsignedIntField,
)
from .fields.base_field import FieldCodec, Fields
from .messages import MessageCodec, Messages
from .services import ServiceCodec, Services

_log = logging.getLogger(__name__)


class MessageDefinitions:
    """A set of Message Definitions grouped into Services.

    Attributes:
        services (Services): A list of `ServiceCodec` with Messages defined.
        name (str): (optional)
        description (str): (optional)
        version (str): (optional)
    
    """
    def __init__(self, services: Services = None, **kwargs):
        if services is not None:
            if not isinstance(services, Services):
                raise ValueError('Invalid Services')
        if isinstance(services, Services):
            self._services = services
        else:
            self._services = Services()
        supported_kwargs = ['name', 'description', 'version']
        for k in supported_kwargs:
            if k in kwargs:
                setattr(self, f'_{k}', kwargs[k])
            else:
                setattr(self, f'_{k}', None)
    
    @property
    def name(self) -> str:
        return self._name
    
    @name.setter
    def name(self, value: str):
        if not isinstance(value, str) or not value:
            raise ValueError('Invalid name')
        self._name = value
    
    @property
    def description(self) -> str:
        return self._description
    
    @description.setter
    def description(self, value: str):
        if not isinstance(value, str) or not value:
            raise ValueError('Invalid name')
        self._description = value
    
    @property
    def version(self) -> str:
        return self._version
    
    @version.setter
    def version(self, value: str):
        if not isinstance(value, str) or not value:
            raise ValueError('Invalid name')
        self._version = value
    
    @property
    def services(self) -> 'list[ServiceCodec]':
        return self._services
    
    @services.setter
    def services(self, services: Services):
        if not isinstance(services, Services):
            raise ValueError('Invalid Services object')
        self._services = services
    
    def xml(self) -> ET.ElementTree:
        """Gets the XML structure of the complete message definitions."""
        extras = {
            f'xmlns:{k}': v for k, v in XML_NAMESPACE.items() if k != 'xsi'
        }
        tree = ET.ElementTree(ET.Element('MessageDefinition', **extras))
        root = tree.getroot()
        services = ET.SubElement(root, 'Services')
        for service in self.services:
            assert isinstance(service, ServiceCodec)
            services.append(service.xml())
        return tree
    
    def mdf_export(self,
                   filename: str,
                   pretty: bool = False,
                   indent: int = 0,
                   include_service_description: bool = False,
                   ) -> None:
        """Creates an XML file at the target location.
        
        Args:
            filename: The full path/filename to save to. `.idpmsg` is
                recommended as a file extension.
            pretty: If True sets indent = 2 (legacy compatibility)
            indent: If nonzero will indent each layer of the XML by n spaces.
            include_service_description: By default removes Description from
                Service for Inmarsat IDP Admin API V1 compatibility.

        """
        tree = self.xml()
        if not include_service_description:
            root = tree.getroot()
            for service in root.iter('Service'):
                d = service.find('Description')
                if d is not None:
                    service.remove(d)
        if pretty:
            indent = 2
        if isinstance(indent, int) and indent > 0:
            ET.indent(tree, space=' '*indent)
        with open(filename, 'wb') as f:
            tree.write(f, encoding='utf-8', xml_declaration=True)
    
    @classmethod
    def _parse_xml_field(cls, field: ET.Element) -> FieldCodec:
        f_type = field.attrib[f'{{{XML_NAMESPACE["xsi"]}}}type']
        f_name = field.find('Name').text
        f_kwargs = {}
        xml_tags = ['Size', 'Description', 'Optional', 'Fixed', 'Default']
        for xml_tag in xml_tags:
            e = field.find(xml_tag)
            if e is not None:
                val = e.text
                k_tag = xml_tag.lower()
                if k_tag in ['size']:
                    val = int(val)
                elif k_tag in ['optional', 'fixed']:
                    val = bool(val)
                f_kwargs[k_tag] = val
        if f_type == 'BooleanField':
            f_codec = BooleanField(f_name, **f_kwargs)
        elif f_type == 'EnumField':
            xml_items = field.find('Items')
            items = [i.text for i in xml_items.findall('string')]
            f_codec = EnumField(f_name, items, **f_kwargs)
        elif f_type == 'UnsignedIntField':
            if 'default' in f_kwargs:
                f_kwargs['default'] = int(f_kwargs['default'])
            f_codec = UnsignedIntField(f_name, **f_kwargs)
        elif f_type == 'SignedIntField':
            if 'default' in f_kwargs:
                f_kwargs['default'] = int(f_kwargs['default'])
            f_codec = SignedIntField(f_name, **f_kwargs)
        elif f_type == 'StringField':
            f_codec = StringField(f_name, **f_kwargs)
        elif f_type == 'DataField':
            f_codec = DataField(f_name, **f_kwargs)
        elif f_type == 'ArrayField':
            array_fields = Fields()
            xml_fields = field.find('Fields')
            for xml_array_field in xml_fields.findall('Field'):
                array_fields.add(cls._parse_xml_field(xml_array_field))
            f_codec = ArrayField(f_name, array_fields, **f_kwargs)
        elif f_type == 'BitmaskListField':
            xml_items = field.find('Items')
            items = [i.text for i in xml_items.findall('string')]
            array_fields = Fields()
            xml_fields = field.find('Fields')
            for xml_array_field in xml_fields.findall('Field'):
                array_fields.add(cls._parse_xml_field(xml_array_field))
            f_kwargs['fields'] = array_fields
            f_codec = BitmaskListField(f_name, items, **f_kwargs)
        else:
            raise ValueError(f'Invalid field type {f_type}')
        return f_codec
    
    @classmethod
    def from_mdf(cls, filename: str, **kwargs):
        """Creates a class instance from a XML message definition file."""
        services = Services()
        tree = ET.parse(filename)
        root = tree.getroot()
        for service in root.iter('Service'):
            sin = int(service.find('SIN').text)
            override_sin = kwargs.get('override_sin', False)
            svc_codec = ServiceCodec(service.find('Name').text, sin,
                                     override_sin=override_sin)
            msg_types: 'list[str]' = ['ReturnMessages', 'ForwardMessages']
            for msg_type in msg_types:
                msg_defs = service.find(msg_type)
                if msg_defs is not None:
                    msg_codecs = Messages(sin, msg_type.startswith('Forward'))
                    for msg_def in msg_defs.findall('Message'):
                        kwargs = {
                            'is_forward': 'Forward' in msg_type,
                            'override_sin': override_sin,
                        }
                        xml_kwargs = ['Description']
                        for xml_kwarg in xml_kwargs:
                            found = msg_def.find(xml_kwarg)
                            if found is not None:
                                kwargs[xml_kwarg.lower()] = found.text
                        msg_codec = MessageCodec(
                            msg_def.find('Name').text,
                            sin,
                            int(msg_def.find('MIN').text),
                            **kwargs,
                        )
                        msg_fields = Fields()
                        xml_fields = msg_def.find('Fields')
                        for field in xml_fields.findall('Field'):
                            msg_fields.add(cls._parse_xml_field(field))
                        msg_codec.fields = msg_fields
                        msg_codecs.add(msg_codec)
                    if msg_type.startswith('Return'):
                        svc_codec.messages_return = msg_codecs
                    else:
                        svc_codec.messages_forward = msg_codecs
            services.add(svc_codec)
        return cls(services)
    
    def json(self) -> OrderedDict:
        """Creates a JSON-based definition."""
        msg_def = OrderedDict({'services': [s.json() for s in self.services]})
        for attr in ['version', 'description', 'name']:
            if hasattr(self, attr) and getattr(self, attr):
                msg_def[attr] = getattr(self, attr)
                msg_def.move_to_end(attr, last=False)
        return { 'nimoMessageDefinition': msg_def }
    
    def json_export(self, filename: str, indent: 'int|None' = 2) -> dict:
        """Converts the message definition to a JSON structured dictionary"""
        with open(filename, 'wb') as f:
            json.dump(self.json(), f, indent=indent)
    
    @classmethod
    def from_json(cls, filename: str):
        """Creates a class instance from a JSON message definition file."""
        raise NotImplementedError


def extract_bits(data: bytes, offset: int, length: int) -> int:
    """"""
    mask = 2**length - 1
    data_int = int.from_bytes(data, 'big')
    shift = 8*len(data) - (offset + length)
    try:
        return (data_int >> shift) & mask
    except ValueError as exc:
        _log.error(exc)


def parse_field(field: dict, data: bytes, offset: int) -> 'tuple[dict, int]':
    """"""
    handler = {
        'arrayField': parse_array_field,
        'uintField': parse_uint_field,
        'intField': parse_int_field,
        'boolField': parse_bool_field,
        'enumField': parse_enum_field,
        'stringField': parse_str_field,
        'dataField': parse_data_field,
    }
    field_type = field.get('type')
    if 'optional' in field:
        field_present = extract_bits(data, offset, 1)
        offset += 1
    else:
        field_present = 1
    if not field_present:
        return {}, offset
    if field_type not in handler:
        raise ValueError(f'No handler for field_type {field_type}')
    return handler[field_type](field, data, offset)


def parse_generic(field: dict, value) -> dict:
    decoded = {
        'name': field.get('name'),
        'value': value,
        'type': str(field.get('type')).replace('Field', ''),
    }
    if 'description' in field:
        decoded['description'] = field.get('description')
    return decoded


def parse_field_length(data: bytes, offset: int) -> 'tuple[int, int]':
    """"""
    l_flag = extract_bits(data, offset, 1)
    offset += 1
    l_len = 15 if l_flag else 7
    field_len = extract_bits(data, offset, l_len)
    return field_len, offset + l_len


def parse_bool_field(field: dict, data: bytes, offset: int) -> 'tuple[dict, int]':
    """"""
    value = extract_bits(data, offset, 1)
    return parse_generic(field, value), offset + 1


def parse_enum_field(field: dict, data: bytes, offset: int) -> 'tuple[dict, int]':
    """"""
    bits = field.get('size')
    enumerations = field.get('items')
    value = enumerations[extract_bits(data, offset, bits)]
    return parse_generic(field, value), offset + bits


def parse_str_field(field: dict, data: bytes, offset: int) -> 'tuple[dict, int]':
    """"""
    str_max_len = field.get('size')
    if 'fixed' in field:
        str_len = str_max_len
    else:
        str_len, offset = parse_field_length(data, offset)
    bits = 8 * str_len
    value = extract_bits(data, offset, bits).to_bytes(str_len, 'big').decode()
    return parse_generic(field, value), offset + bits


def parse_data_field(field: dict, data: bytes, offset: int) -> 'tuple[dict, int]':
    """"""
    data_max_len = field.get('size')
    if 'fixed' in field:
        data_len = data_max_len
    else:
        data_len, offset = parse_field_length(data, offset)
    bits = 8 * data_len
    value = extract_bits(data, offset, bits).to_bytes(data_len, 'big')
    return parse_generic(field, value), offset + bits


def parse_uint_field(field: dict, data: bytes, offset: int) -> 'tuple[dict, int]':
    """"""
    bits = field.get('size')
    value = extract_bits(data, offset, bits)
    return parse_generic(field, value), offset + bits


def parse_int_field(field: dict, data: bytes, offset: int) -> 'tuple[dict, int]':
    """"""
    bits = field.get('size')
    value = extract_bits(data, offset, bits)
    if (value & (1 << (bits - 1))) != 0:
        value = value - (1 << bits)
    return parse_generic(field, value), offset + bits


def parse_array_field(field: dict, data: bytes, offset: int) -> 'tuple[dict, int]':
    """Returns decoded field and new bit offset"""
    array_name: str = field.get('name')
    array_max_len: int = field.get('size')
    array_values: 'list[dict]' = []
    if field.get('fixed', False):
        field_len = array_max_len
    else:
        field_len, offset = parse_field_length(data, offset)
    for _row in range(0, field_len):
        decoded_cols = {}
        for col in field.get('fields'):
            if 'optional' in col:
                col_present = extract_bits(data, offset, 1)
                offset += 1
            else:
                col_present = 1
            if not col_present:
                continue
            col_name: str = col.get('name')
            decoded_field, offset = parse_field(col, data, offset)
            if decoded_field:
                decoded_cols[col_name] = decoded_field
        if decoded_cols:
            array_values.append(decoded_cols)
    decoded = { 'name': array_name, 'fields': array_values }
    return decoded, offset


def decode_message(data: bytes,
                   codec_path: str,
                   mobile_originated: bool = True,
                   **kwargs) -> dict:
    """Decodes a message using the codec specified."""
    if not isinstance(data, (bytes, bytearray)):
        raise ValueError('Invalid data bytes')
    if not os.path.exists(codec_path):
        raise ValueError('Invalid codec path')
    codec = None
    codec_sin = data[0]
    codec_min = data[1]
    decoded = {}
    try:
        if codec_path.endswith(('.idpmsg', '.xml', '.json')):
            override_sin = kwargs.get('override_sin', False)
            md: MessageDefinitions = MessageDefinitions.from_mdf(
                codec_path, override_sin=override_sin
            )
            codec = md.json()
    except ET.ParseError:
        try:
           with open(codec_path) as f:
               codec = json.load(f, object_pairs_hook=OrderedDict)
        except json.JSONDecodeError:
            raise ValueError('Unable to parse codec %s', codec_path)
    assert isinstance(codec, dict)
    msgdef: dict = codec.get('nimoMessageDefinition')
    services: 'list[dict]' = msgdef.get('services')
    for service in services:
        if service.get('codecServiceId') != codec_sin:
            continue
        mkey = 'mobileOriginatedMessages'
        if not mobile_originated:
            mkey = mkey.replace('Originated', 'Terminated')
        messages: 'list[dict]' = service.get(mkey)
        for message in messages:
            if message.get('codecMessageId') != codec_min:
                continue
            decoded['name'] = message.get('name')
            if 'description' in message:
                decoded['description'] = message.get('description')
            decoded['codecServiceId'] = codec_sin
            decoded['codecMessageId'] = codec_min
            offset = 16   #: Begin after codec header (SIN, MIN)
            decoded_fields = []
            for field in message.get('fields'):
                assert isinstance(field, dict)
                if 'optional' in field:
                    field_present = extract_bits(data, offset, 1)
                    offset += 1
                else:
                    field_present = 1
                if not field_present:
                    continue
                decoded_field, offset = parse_field(field, data, offset)
                decoded_fields.append(decoded_field)
            decoded['fields'] = decoded_fields
            break
        break
    return decoded
