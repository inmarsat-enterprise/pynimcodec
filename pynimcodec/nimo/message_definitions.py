from collections import OrderedDict
import logging
import json
import os

from . import ET, XML_NAMESPACE
from .services import ServiceCodec, Services

_log = logging.getLogger(__name__)


class MessageDefinitions:
    """A set of Message Definitions grouped into Services.

    Attributes:
        services: The list of Services with Messages defined.
    
    """
    def __init__(self, services: Services = None):
        if services is not None:
            if not isinstance(services, Services):
                raise ValueError('Invalid Services')
        self.services = services or Services()
    
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
    
    def json(self) -> dict:
        """Converts the message definition to a JSON structured dictionary"""
        raise NotImplementedError
        return {
            'nimoMessageDefinition': {
                'services': [s.json() for s in self.services]
            }
        }


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
                   ) -> dict:
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
        codec = ET.parse(codec_path)
    except ET.ParseError:
        try:
           with open(codec_path) as f:
               codec = json.load(f, object_pairs_hook=OrderedDict)
        except json.JSONDecodeError:
            raise ValueError('Unable to parse codec %s', codec_path)
    if isinstance(codec, ET.ElementTree):
        raise NotImplementedError
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
