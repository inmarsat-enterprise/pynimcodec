import xml.etree.ElementTree as ET

from .constants import XML_NAMESPACE, DataFormat, DATA_TYPES, SIN_RANGE
from .fields import (ArrayField, BooleanField, DataField, EnumField,
                     SignedIntField, StringField, UnsignedIntField)
from .fields.base_field import FieldCodec, Fields
from .fields.helpers import optimal_bits
from .message_definitions import MessageDefinitions
from .messages import MessageCodec, Messages
from .services import ServiceCodec, Services

__all__ = [
    'ArrayField',
    'BooleanField',
    'DataField',
    'EnumField',
    'SignedIntField',
    'StringField',
    'UnsignedIntField',
    'CodecList',
    'FieldCodec',
    'Fields',
    'DataFormat',
    'DATA_TYPES',
    'SIN_RANGE',
    'MessageDefinitions',
    'MessageCodec',
    'Messages',
    'ServiceCodec',
    'Services',
    'optimal_bits',
]

for ns in XML_NAMESPACE:
    ET.register_namespace(ns, XML_NAMESPACE[ns])
