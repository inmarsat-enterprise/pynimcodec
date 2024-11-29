from enum import IntEnum


class DataFormat(IntEnum):
    TEXT = 1
    HEX = 2
    BASE64 = 3


XML_NAMESPACE = {
    'xsd': 'http://www.w3.org/2001/XMLSchema',
    'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
}

DATA_TYPES = {
    'bool': 'BooleanField',
    'int_8': 'SignedIntField',
    'uint_8': 'UnsignedIntField',
    'int_16': 'SignedIntField',
    'uint_16': 'UnsignedIntField',
    'int_32': 'SignedIntField',
    'uint_32': 'UnsignedIntField',
    'int_64': 'SignedIntField',
    'uint_64': 'UnsignedIntField',
    'float': 'DataField',
    'double': 'DataField',
    'string': 'StringField',
    'data': 'DataField',
    'enum': 'EnumField',
    'array': 'ArrayField',
    'bml': 'BitmaskListField',
}

FIELD_TYPES_JSON = {
    'BooleanField': 'boolField',
    'EnumField': 'enumField',
    'DataField': 'dataField',
    'ArrayField': 'arrayField',
    'SignedIntField': 'intField',
    'UnsignedIntField': 'uintField',
    'StringField': 'stringField',
    'BitmaskListField': 'bmlField',
}

SIN_RANGE = (16, 255)
