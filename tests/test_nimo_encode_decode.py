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
    FieldCodec,
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
    encode_message,
    MessageField,
    DynamicField,
    PropertyField
)

logging.basicConfig()
logger = logging.getLogger()


@dataclass
class Location:
    latitude: float
    longitude: float
    altitude: float
    timestamp: int

DECODE_TEST_CASES = {
    'position': {
        'exclude': False,
        'codec': os.path.join(os.getcwd(), 'secrets/coremodem.idpmsg'),
        'raw_payload': "AEgBLoDx/7WUgEUAAKum",
        'decoded': dict({
            "name": "position",
            "codecServiceId": 0,
            "codecMessageId": 72,
            "fields": [
                {
                    "name": "fixStatus",
                    "value": "1",
                    "type": "unsignedint"
                },
                {
                    "name": "latitude",
                    "value": "3047665",
                    "type": "signedint"
                },
                {
                    "name": "longitude",
                    "value": "-38103",
                    "type": "signedint"
                },
                {
                    "name": "altitude",
                    "value": "69",
                    "type": "signedint"
                },
                {
                    "name": "speed",
                    "value": "0",
                    "type": "unsignedint"
                },
                {
                    "name": "heading",
                    "value": "0",
                    "type": "unsignedint"
                },
                {
                    "name": "dayOfMonth",
                    "value": "21",
                    "type": "unsignedint"
                },
                {
                    "name": "minuteOfDay",
                    "value": "934",
                    "type": "unsignedint"
                }
            ]
        })
    },
    'satelliteTelemetery': {
        'exclude': False,
        'codec': os.path.join(os.getcwd(), 'tests/examples/fieldedge-iotdemo.idpmsg'),
        'raw_payload': "/wHM0y78UxiBuqsLApAEvgPuKA==",
        'decoded': dict({"name":"SatelliteTelemetry",
                           "codecServiceId":255,
                           "codecMessageId":1,
                           "fields":[
                               {"name":"timestamp","value":"1718196094","type":"unsignedint"},
                               {"name":"latitude","value":"2722880","type":"signedint"},
                               {"name":"longitude","value":"-4543733","type":"signedint"},
                               {"name":"altitude","value":"82","type":"signedint"},
                               {"name":"speed","value":"0","type":"unsignedint"},
                               {"name":"heading","value":"303","type":"unsignedint"},
                               {"name":"gnssSatellites","value":"8","type":"unsignedint"},
                               {"name":"pdop","value":"1","type":"unsignedint"},
                               {"name":"snr","value":"494","type":"unsignedint"},
                               {"name":"temperature","value":"20","type":"signedint"}]})
    },
    'testService': {
        'exclude': True, #TODO: Currently not functioning
        'codec': os.path.join(os.getcwd(), 'tests/examples/testService.idpmsg'),
        'raw_payload': "/wGABgAABoEYWJjZAEGcHJvcF8xAAAADQRhYmNkA",
        'decoded': dict({"name":"returnMessageFixture",
                           "codecServiceId":255,
                           "codecMessageId":1,
                           "fields":[
                               {"name": 'testBool', "type": 'boolean', "value": 'True'},
                               {"name": 'testUint', "type": 'unsignedint', "value": '12'},
                               {"name": 'latitude', "type": 'signedint', "value": '13'},
                               {"name": 'nonOptionalString', "type": 'string', "value": 'abcd'},
                               {"fields": [
                                   {    'Propertyname': {"name": 'propertyName', "type": 'string', "value": 'prop_1'},
                                        'Propertyvalue': {"name": 'propertyValue', "type": 'unsignedint', "value": '13'}}
                                   ],
                                "name": 'arrayExample'},
                               {"name": 'testData', "type": 'data', "value": 'YWJjZA=='}
                            ]})
    }
}

ENCODE_TEST_CASES = {
    'requestTxMetrics': {
        'exclude': False, # Working
        'codec': os.path.join(os.getcwd(), 'secrets/coremodem.idpmsg'),
        'raw_payload': "AGQA",
        'encode': dict({"name":"requestTxMetrics",
                           "codecServiceId":0,
                           "codecMessageId":100,
                           "fields":[
                               {"name":"period","value":"SinceReset"}
                            ]})
    },
    'testService': {
        'exclude': True, # Not Working
        'codec': os.path.join(os.getcwd(), 'tests/examples/testService.idpmsg'),
        'raw_payload': "/wGABgAABoEYWJjZAEGcHJvcF8xAAAADQRhYmNkA",
        'encode': dict({"name":"forwardMessageFixture",
                           "codecServiceId":255,
                           "codecMessageId":1,
                           "fields":[
                               {"name": 'testBool', "value": 'True'},
                               {"name": 'testUint', "value": '12'},
                               {"name": 'latitude', "value": '13'},
                               {"name": 'nonOptionalString', "value": 'abcd'},
                               {"fields": [
                                   {    'Propertyname': {"name": 'propertyName', "value": 'prop_1'},
                                        'Propertyvalue': {"name": 'propertyValue', "value": '13'}}
                                   ],
                                "name": 'arrayExample'},
                               {"name": 'testData', "value": 'YWJjZA=='}
                            ]})
    },
    'getProperties': {
        'exclude': True, # Not Working
        'codec': os.path.join(os.getcwd(), 'secrets/luaTerminals.idpmsg'),
        'raw_payload': "EAiBCYAKAAA=",
        'encode': dict({
                "name": "getProperties",
                "codecServiceId": 16,
                "codecMessageId": 8,
                "fields": [
                    {
                        "name": "list",
                        "Elements": [
                            {
                                "index": 0,
                                "fields": [
                                    {
                                        "name": "sin",
                                        "value": "19"
                                    },
                                    {
                                        "name": "pinList",
                                        "value": ""
                                    }
                                ]
                            },
                            {
                                "index": 1,
                                "fields": [
                                    {
                                        "name": "sin",
                                        "value": "20"
                                    },
                                    {
                                        "name": "pinList",
                                        "value": ""
                                    }
                                ]
                            }
                        ]
                    }
                ]
            })
    },
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
            expected = test_inputs.get('raw_payload');
            decoded = decode_message(data, test_codec, override_sin=True)
            expected: dict = test_inputs.get('decoded')
            logger.debug(f"\n--- EXPECTED: \n{expected}")
            logger.debug(f"\n----- RESULT: \n{decoded}\n")
            for k, v in expected.items():
                if k != 'Fields':
                    assert k in decoded and decoded[k] == v
                else:
                    for i, field in enumerate(v):
                        for fk, fv in field.items():
                            assert fk in decoded['Fields'][i] and fv == decoded['Fields'][i][fk]

def test_message_definitions_encode_message():
    """"""
    for test_inputs in ENCODE_TEST_CASES.values():
        if not test_inputs.get('exclude', False):
            logger.debug(f"\n")
            test_codec = test_inputs.get('codec')
            expected_raw_payload = test_inputs.get('raw_payload')
            to_encode: dict = test_inputs.get('encode')
            
            encoded_raw_payload = encode_message(to_encode, test_codec, override_sin=True)

            logger.debug(f"--- EXPECTED: \n{expected_raw_payload}")
            logger.debug(f"----- RESULT: \n{encoded_raw_payload.decode('utf-8')}")
            assert(expected_raw_payload == encoded_raw_payload.decode('utf-8'))
