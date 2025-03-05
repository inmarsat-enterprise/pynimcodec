import base64
import json
import logging
import math
import os
import xml.etree.ElementTree as ET
from collections import OrderedDict
from copy import deepcopy
from dataclasses import dataclass
from binascii import b2a_base64

import pytest

from pynimcodec.nimo import (
    ArrayField,
    BitmaskListField,
    BooleanField,
    DataField,
    DataFormat,
    EnumField,
    Fields,
    MessageCodec,
    MessageDefinitions,
    Messages,
    ServiceCodec,
    Services,
    SignedIntField,
    StringField,
    UnsignedIntField,
    optimal_bits,
    decode_message,
)

logging.basicConfig()
logger = logging.getLogger()


@dataclass
class Location:
    latitude: float
    longitude: float
    altitude: float
    timestamp: int


@pytest.fixture
def fieldedge_message() -> MessageCodec:
    """Returns a Fieldedge TextMobileTerminated message."""
    fields = Fields()
    fields.add(UnsignedIntField(name='source',size=32,optional=True));
    fields.add(StringField(name='text',size=255,value='Sending a mobile-terminated message to device'));
    #fields.add(StringField(name='text',value='pyTest text message'));
    fields.add(UnsignedIntField(name='timestamp',size=32,optional=True,value=1739375463));
    
    message = MessageCodec(name='TextMobileTerminated',
                        sin=255,
                        min=4,
                        fields=fields,
                        is_forward=True)
    return message


DECODE_TEST_CASES = {
    'locationJsonCodec': {
        'exclude': True,
        'codec': os.path.join(os.getcwd(), 'secrets/coremodem.json'),
        'raw_payload': [
            0,
            72,
            1,
            41,
            117,
            173,
            221,
            71,
            129,
            0,
            88,
            2,
            82,
            20,
            53,
        ],
        'decoded': dict({
            "name": "location",
            "description": "The modem's location",
            "codecServiceId": 0,
            "codecMessageId": 72,
            "fields": [
                {
                    "name": "fixStatus",
                    "description": "Status of GNSS fix",
                    "value": "VALID",
                    "type": "enum"
                },
                {
                    "name": "latitude",
                    "description": "Latitude in 0.001 minutes",
                    "value": 2717101,
                    "type": "int"
                },
                {
                    "name": "longitude",
                    "description": "Longitude in 0.001 minutes",
                    "value": -4550910,
                    "type": "int"
                },
                {
                    "name": "altitude",
                    "description": "Altitude in meters",
                    "value": 88,
                    "type": "int"
                },
                {
                    "name": "speed",
                    "description": "Speed in km/h",
                    "value": 2,
                    "type": "uint"
                },
                {
                    "name": "heading",
                    "description": "Heading in 2-degree increments from North",
                    "value": 82,
                    "type": "uint"
                },
                {
                    "name": "dayOfMonth",
                    "value": 2,
                    "type": "uint"
                },
                {
                    "name": "minuteOfDay",
                    "value": 1077,
                    "type": "uint"
                }
            ]
        })
    },
    'locationXmlCodec': {
        'exclude': True,
        'codec': os.path.join(os.getcwd(), 'secrets/coremodem.idpmsg'),
        'raw_payload': [
            0,
            72,
            1,
            41,
            117,
            173,
            221,
            71,
            129,
            0,
            88,
            2,
            82,
            20,
            53,
        ],
        'decoded': dict({
            "name": "replyPosition",
            "description": "The modem's location",
            "codecServiceId": 0,
            "codecMessageId": 72,
            "fields": [
                {
                    "name": "fixStatus",
                    "description": "Status of GNSS fix",
                    "value": "VALID",
                    "type": "enum"
                },
                {
                    "name": "latitude",
                    "description": "Latitude in 0.001 minutes",
                    "value": 2717101,
                    "type": "int"
                },
                {
                    "name": "longitude",
                    "description": "Longitude in 0.001 minutes",
                    "value": -4550910,
                    "type": "int"
                },
                {
                    "name": "altitude",
                    "description": "Altitude in metres",
                    "value": 88,
                    "type": "int"
                },
                {
                    "name": "speed",
                    "description": "Speed in km/h",
                    "value": 2,
                    "type": "uint"
                },
                {
                    "name": "heading",
                    "description": "Heading in 2-degree steps (North=0)",
                    "value": 82,
                    "type": "uint"
                },
                {
                    "name": "dayOfMonth",
                    "value": 2,
                    "type": "uint"
                },
                {
                    "name": "minuteOfDay",
                    "value": 1077,
                    "type": "uint"
                }
            ]
        })
    },
    'rlSysConfig': {
        'exclude': True,
        'codec': os.path.join(os.getcwd(), 'tests/examples/nimotestjson.json'),
        'raw_payload': [
            0,
            135,
            32,
            6,
            80,
            60,
            6,
            96,
            44,
            6,
            112,
            44,
            6,
            128,
            44,
            6,
            144,
            60,
            12,
            144,
            76,
            12,
            160,
            60,
            12,
            176,
            60,
            12,
            192,
            76,
            18,
            208,
            44,
            18,
            224,
            44,
            18,
            240,
            60,
            19,
            0,
            44,
            19,
            16,
            60,
            25,
            16,
            44,
            25,
            32,
            28,
            31,
            80,
            60,
            31,
            96,
            60,
            31,
            112,
            60,
            31,
            128,
            44,
            31,
            144,
            28,
            31,
            160,
            28,
            255,
            240,
            184,
            6,
            128,
            60,
            6,
            112,
            60,
            6,
            96,
            60,
            6,
            80,
            76,
            6,
            144,
            76,
            12,
            144,
            92,
            12,
            160,
            76,
            12,
            176,
            76,
            12,
            192,
            92,
            5,
            0,
            184,
            0,
            200,
            0,
            216,
            0,
            232,
            0,
            248,
            9,
            0,
            184,
            0,
            200,
            0,
            216,
            0,
            232,
            0,
            248,
            1,
            8,
            1,
            24,
            1,
            40,
            1,
            56,
            60,
            0,
            16,
            32,
            8,
            0,
            32,
            32,
            8,
            0,
            48,
            32,
            8,
            0,
            64,
            32,
            8,
            0,
            80,
            32,
            8,
            0,
            96,
            32,
            8,
            0,
            112,
            32,
            8,
            0,
            128,
            32,
            8,
            0,
            144,
            32,
            8,
            0,
            160,
            32,
            8,
            0,
            176,
            32,
            8,
            0,
            192,
            32,
            8,
            0,
            208,
            32,
            8,
            0,
            224,
            32,
            8,
            0,
            240,
            32,
            8,
            1,
            0,
            32,
            8,
            1,
            48,
            32,
            8,
            1,
            80,
            64,
            8,
            1,
            96,
            64,
            8,
            1,
            112,
            96,
            8,
            1,
            128,
            64,
            8,
            1,
            144,
            64,
            8,
            1,
            160,
            64,
            8,
            1,
            176,
            96,
            8,
            1,
            192,
            64,
            8,
            1,
            208,
            64,
            8,
            1,
            224,
            64,
            8,
            1,
            240,
            64,
            8,
            2,
            0,
            96,
            8,
            2,
            16,
            64,
            8,
            2,
            32,
            64,
            8,
            2,
            48,
            64,
            8,
            2,
            64,
            64,
            8,
            2,
            80,
            64,
            8,
            2,
            96,
            64,
            8,
            2,
            112,
            64,
            8,
            2,
            144,
            32,
            8,
            2,
            160,
            32,
            8,
            2,
            176,
            32,
            8,
            2,
            192,
            32,
            8,
            2,
            208,
            32,
            8,
            2,
            224,
            32,
            8,
            2,
            240,
            32,
            8,
            3,
            0,
            32,
            8,
            3,
            16,
            32,
            8,
            3,
            32,
            32,
            8,
            3,
            48,
            32,
            8,
            3,
            64,
            32,
            8,
            3,
            80,
            32,
            8,
            3,
            96,
            32,
            8,
            3,
            112,
            32,
            8,
            3,
            128,
            32,
            8,
            3,
            144,
            32,
            8,
            3,
            160,
            32,
            8,
            3,
            176,
            32,
            8,
            3,
            208,
            32,
            8,
            5,
            160,
            32,
            8,
            5,
            176,
            32,
            8,
            5,
            192,
            32,
            8,
            5,
            240,
            32,
            8
        ],
        'decoded': {},
    
    },
    'satelliteTelemetery':{
        'codec': os.path.join(os.getcwd(), 'tests/examples/fieldedge-iotdemo.idpmsg'),
        'raw_payload': [
            255,
            1,
            206,
            121,
            165,
            72,
            83,
            24,
            125,
            186,
            171,
            12,
            2,
            152,
            3,
            174,
            3,
            38,
            62
            ],
        'decoded': dict({
            "name": "SatelliteTelemetry",
            "codecServiceId": 255,
            "codecMessageId": 1,
            "fields": [
                {
                    "name": "timestamp",
                    "value": 1732039332,
                    "type": "uint"
                },
                {
                    "name": "latitude",
                    "value": 2722878,
                    "type": "int"
                },
                {
                    "name": "longitude",
                    "value": -4543732,
                    "type": "int"
                },
                {
                    "name": "altitude",
                    "value": 83,
                    "type": "int"
                },
                {
                    "name": "speed",
                    "value": 0,
                    "type": "uint"
                },
                {
                    "name": "heading",
                    "value": 235,
                    "type": "uint"
                },
                {
                    "name": "gnssSatellites",
                    "value": 8,
                    "type": "uint"
                },
                {
                    "name": "pdop",
                    "value": 1,
                    "type": "uint"
                },
                {
                    "name": "snr",
                    "value": 294,
                    "type": "uint"
                },
                {
                    "name": "temperature",
                    "value": 31,
                    "type": "int"
                }
            ]
        })
    },
    'satelliteTelemeteryOGWS': {
        'codec': os.path.join(os.getcwd(), 'tests/examples/fieldedge-iotdemo.idpmsg'),
        'raw_payload': "/wHM0y78UxiBuqsLApAEvgPuKA==",
        'decoded': dict({"name":"SatelliteTelemetry",
                           "codecServiceId":255,
                           "codecMessageId":1,
                           "fields":[
                               {"name":"timestamp","value":1718196094,"type":"uint"},
                               {"name":"latitude","value":2722880,"type":"int"},
                               {"name":"longitude","value":-4543733,"type":"int"},
                               {"name":"altitude","value":82,"type":"int"},
                               {"name":"speed","value":0,"type":"uint"},
                               {"name":"heading","value":303,"type":"uint"},
                               {"name":"gnssSatellites","value":8,"type":"uint"},
                               {"name":"pdop","value":1,"type":"uint"},
                               {"name":"snr","value":494,"type":"uint"},
                               {"name":"temperature","value":20,"type":"int"}]})
    }
}

def test_message_definitions_decode_message():
    """"""
    for test_inputs in DECODE_TEST_CASES.values():
        if not test_inputs.get('exclude', False):
            test_codec = test_inputs.get('codec')
            raw_payload = test_inputs.get('raw_payload')
            if isinstance(raw_payload, (list)):
                data = bytes(raw_payload)
            else:
                data = base64.b64decode(raw_payload)
            res = decode_message(data, test_codec, override_sin=True)
            expected: dict = test_inputs.get('decoded')
            for k, v in expected.items():
                if k != 'fields':
                    assert k in res and res[k] == v
                else:
                    for i, field in enumerate(v):
                        for fk, fv in field.items():
                            assert fk in res['fields'][i] and fv == res['fields'][i][fk]



def test_rm_codec(return_message):
    msg: MessageCodec = return_message
    msg_copy = deepcopy(return_message)
    encoded = msg.encode(data_format=DataFormat.HEX)
    hex_message = (format(encoded['sin'], '02X') +
                   format(encoded['min'], '02X') +
                   encoded['data'])
    msg.decode(bytes.fromhex(hex_message))
    assert(msg_copy == msg)


def test_rm_codec_base64(fieldedge_message):
    msg: MessageCodec = fieldedge_message
    msg_copy = deepcopy(fieldedge_message)
    encoded = msg.encode(data_format=DataFormat.BASE64)
    hex_message = (format(encoded['sin'], '02X') +
                   format(encoded['min'], '02X') +
                   base64.b64decode(encoded['data']).hex())
    msg.decode(bytes.fromhex(hex_message))
    payloadRaw = b2a_base64(bytearray.fromhex(hex_message)).strip().decode()
    #logger.debug(payloadRaw)
    assert(msg_copy == msg)