import base64
import json
import logging
import os
import xml.etree.ElementTree as ET
from collections import OrderedDict
from copy import deepcopy
from dataclasses import dataclass
from binascii import b2a_base64

import pytest

from pynimcodec.nimo import (
    optimal_bits,
    decode_message
)

logging.basicConfig()
logger = logging.getLogger()

LUATERM_DECODE_TEST_CASES = {
    'terminalRegistration': {
        'exclude': False,
        'codec': os.path.join(os.getcwd(), 'secrets/luaTerminals.idpmsg'),
        'raw_payload': "EAgHBQEFAgQGMTIuMi4zABEQERITFBUWFxgZGhsgISJ+fws1LjIuMS4yMzM0Mw==",
        'decoded': dict({
            "name": "terminalRegistration",
            "codecServiceId": 16,
            "codecMessageId": 8,
            "fields": [
                {
                    "name": "hardwareVariant",
                    "value": "7",
                    "type": "enum"},
                {
                    "name":"hardwareRevision",
                    "value":"5",
                    "type":"unsignedint"},
                {
                    "name":"hardwareResetReason",
                    "value":"PowerOn",
                    "type":"enum"},
                {
                    "name":"firmwareMajor",
                    "value":"5",
                    "type":"unsignedint"},
                {
                    "name":"firmwareMinor",
                    "value":"2",
                    "type":"unsignedint"},
                {
                    "name":"firmwarePatch",
                    "value":"4",
                    "type":"unsignedint"},
                {
                    "name":"LSFVersion",
                    "value":"12.2.3",
                    "type":"string"},
                {
                    "name":"softwareResetReason",
                    "value":"None",
                    "type":"enum"},
                {
                    "name":"sinList",
                    "value":"EBESExQVFhcYGRobICEifn8=",
                    "type":"data"},
                {
                    "name":"packageVersion",
                    "value":"5.2.1.23343",
                    "type":"string"}
            ]
        })
    },
    'propertyvalues': {
        'exclude': True,
        'codec': os.path.join(os.getcwd(), 'secrets/luaTerminals.idpmsg'),
        'raw_payload': [
            16,
            5,
            1,
            1,
            1,
            2,
            48
        ],
        'decoded': dict({
            "name": "propertyvalues",
            "codecServiceId": 16,
            "codecMessageId": 5,
            "fields": [
                {
                    "name":"list",
                    "type":"array",
                    "fields":[
                        {
                            "name":"sin",
                            "value":"1",
                            "type":"unsignedint"},
                        {
                            "name":"propList",
                            "type":"array",
                            "fields":[
                                {
                                    "name":"pin",
                                    "value":"2",
                                    "type":"unsignedint"},
                                {
                                    "name":"value",
                                    "value":"1",
                                    "type":"bool"}
                            ]
                        }
                    ]
                }
            ]
        })
    },
    'simpleReport': {
        'exclude': False,
        'codec': os.path.join(os.getcwd(), 'secrets/luaTerminals.idpmsg'),
        'raw_payload': [
            19, 1, 112, 1, 116, 7, 131, 191, 255, 218, 201, 208, 0, 128, 0
        ],
        'decoded': dict({
            "name": "simpleReport",
            "codecServiceId": 19,
            "codecMessageId": 1,
            "fields": [
                {
                    "name": "latitude",
                    "value": "3047664",
                    "type": "signedint"
                },
                {
                    "name": "longitude",
                    "value": "-38105",
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
                }
            ]})
    },
    'fullReport': {
        'exclude': False,
        'codec': os.path.join(os.getcwd(), 'secrets/luaTerminals.idpmsg'),
        'raw_payload': "EwIwAuAC6A83f/+1k6ABAAx2c0VtfsAAQAAAQAAAQAAAQAMIUruMQA==",
        'decoded': dict({
            "name": "fullReport",
            "codecServiceId": 19,
            "codecMessageId": 2,
            "fields": [
                {
                    "name": "fixValid",
                    "value": "True",
                    "type": "boolean"
                },
                {
                    "name": "fixType",
                    "value": "1",
                    "type": "enum"
                },
                {
                    "name": "latitude",
                    "value": "3047667",
                    "type": "signedint"
                },
                {
                    "name": "longitude",
                    "value": "-38105",
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
                    "name": "altitude",
                    "value": "118",
                    "type": "signedint"
                },
                {
                    "name": "fixTime",
                    "value": "1756213208",
                    "type": "signedint"
                },
                {
                    "name": "port1Cfg",
                    "value": "0",
                    "type": "enum"
                },
                {
                    "name": "port1Value",
                    "value": "0",
                    "type": "unsignedint"
                },
                {
                    "name": "port2Cfg",
                    "value": "0",
                    "type": "enum"
                },
                {
                    "name": "port2Value",
                    "value": "0",
                    "type": "unsignedint"
                },
                {
                    "name": "port3Cfg",
                    "value": "0",
                    "type": "enum"
                },
                {
                    "name": "port3Value",
                    "value": "0",
                    "type": "unsignedint"
                },
                {
                    "name": "port4Cfg",
                    "value": "0",
                    "type": "enum"
                },
                {
                    "name": "port4Value",
                    "value": "0",
                    "type": "unsignedint"
                },
                {
                    "name": "currentTemperature",
                    "value": "33",
                    "type": "signedint"
                },
                {
                    "name": "inputPowerVoltage",
                    "value": "24006",
                    "type": "unsignedint"
                },
                {
                    "name": "DTEConnected",
                    "value": "False",
                    "type": "boolean"
                }
            ]})
    },
    'eio': {
        'exclude': False,
        'codec': os.path.join(os.getcwd(), 'secrets/luaTerminals.idpmsg'),
        'raw_payload': "EwMACAAACAAACAAACABhCldviA==",
        'decoded': dict({
            "name": "EIO",
            "codecServiceId": 19,
            "codecMessageId": 3,
            "fields": [
                {
                    "name": "port1Cfg",
                    "value": "0",
                    "type": "enum"
                },
                {
                    "name": "port1Value",
                    "value": "0",
                    "type": "unsignedint"
                },
                {
                    "name": "port2Cfg",
                    "value": "0",
                    "type": "enum"
                },
                {
                    "name": "port2Value",
                    "value": "0",
                    "type": "unsignedint"
                },
                {
                    "name": "port3Cfg",
                    "value": "0",
                    "type": "enum"
                },
                {
                    "name": "port3Value",
                    "value": "0",
                    "type": "unsignedint"
                },
                {
                    "name": "port4Cfg",
                    "value": "0",
                    "type": "enum"
                },
                {
                    "name": "port4Value",
                    "value": "0",
                    "type": "unsignedint"
                },
                {
                    "name": "currentTemperature",
                    "value": "33",
                    "type": "signedint"
                },
                {
                    "name": "inputPowerVoltage",
                    "value": "23998",
                    "type": "unsignedint"
                },
                {
                    "name": "DTEConnected",
                    "value": "False",
                    "type": "boolean"
                }
            ]})
    },
    'msgError': {
        'exclude': False,
        'codec': os.path.join(os.getcwd(), 'secrets/luaTerminals.idpmsg'),
        'raw_payload': "EgQfc3ZjLnJlcG9ydDogU0lOIDMwIGlzIG5vdCB2YWxpZBMB",
        'decoded': dict({"name":"msgError",
                           "codecServiceId":18,
                           "codecMessageId":4,
                           "fields":[
                               {
                                    "name": "desc",
                                    "value": "svc.report: SIN 30 is not valid",
                                    "type": "string"
                                },
                                {
                                    "name": "sin",
                                    "value": "19",
                                    "type": "unsignedint"
                                },
                                {
                                    "name": "min",
                                    "value": "1",
                                    "type": "unsignedint"
                                }
                            ]})
    },
    'serviceInfo': {
        'exclude': False,
        'codec': os.path.join(os.getcwd(), 'secrets/luaTerminals.idpmsg'),
        'raw_payload': [
            16,
            4,
            8, 3, 65, 66, 67, 5, 49, 46, 50, 46, 51, 128
        ],
        'decoded': dict({
            "name": "serviceInfo",
            "codecServiceId": 16,
            "codecMessageId": 4,
            "fields": [
                {
                    "name": "sin",
                    "value": "8",
                    "type": "unsignedint"
                },
                {
                    "name": "name",
                    "value": "ABC",
                    "type": "string"
                },
                {
                    "name": "version",
                    "value": "1.2.3",
                    "type": "string"
                },
                {
                    "name": "enabled",
                    "value": "True",
                    "type": "boolean"
                },
                {
                    "name": "running",
                    "value": "False",
                    "type": "boolean"
                }
            ]})
    }
}

def test_message_definitions_decode_message():
    """"""
    for test_inputs in LUATERM_DECODE_TEST_CASES.values():
        if not test_inputs.get('exclude', False):
            logger.debug(f"====================================")
            test_codec = test_inputs.get('codec')
            raw_payload = test_inputs.get('raw_payload')
            if isinstance(raw_payload, (list)):
                data = bytes(raw_payload)
            else:
                data = base64.b64decode(raw_payload)
            res = decode_message(data, test_codec, override_sin=True)
            expected: dict = test_inputs.get('decoded')
            logger.debug(f"--- EXPECTED: \n{expected}")
            logger.debug(f"----- RESULT: \n{res}")
            for k, v in expected.items():
                if k != 'fields':
                    assert k in res and res[k] == v
                else:
                    for i, field in enumerate(v):
                        for fk, fv in field.items():
                            assert fk in res['fields'][i] and fv == res['fields'][i][fk]