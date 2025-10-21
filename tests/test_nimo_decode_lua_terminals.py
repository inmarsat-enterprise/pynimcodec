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
    },
    'propertyValues': {
        'exclude': False,
        'codec': os.path.join(os.getcwd(), 'secrets/luaTerminals.idpmsg'),
        'raw_payload': "EAUCEy4BMCQJgaAEEYAAqBQGMHIIIJQJhSAELYABiDwNMOIPIQQJiKAESYACaDwUMVIWIXQJjCAEZYADSDwbMcIdIeIfQAkCAAhQAESAAjQAEiAAlQAEyAAoQAFKLQqQAFaLQsQAFqLQuQAF6LQULwEAAEYGAEEcSD2xugrv+MZDcGcAF0B5g7v//aykIaASoSgACkhg2FuaO+a8QxIDvhoAA4AAegAEAAiJCSAQTQACiLQVQACwABchhASMoCBpAANp//8eIfIgYAELAAjSAlhIgBJWf5OkBkChACUs/ytIDhFiAMtZ/l6ROIMEABiz/MzNCNTNiA==",
        'decoded': dict({
            "name":"propertyValues",
            "codecServiceId":16,
            "codecMessageId":5,
            "fields":[
                {"name":"list","type":"array","elements":[
                    {"index":0,"fields":[
                        {"name":"sin","value":"19","type":"unsignedint"},
                        {"name":"propList","type":"array","elements":[
                            {"index":0,"fields":[{"name":"pin","value":"1","type":"unsignedint"},{"name":"value","value":"True","type":"boolean"}]},
                            {"index":1,"fields":[{"name":"pin","value":"2","type":"unsignedint"},{"name":"value","value":"19","type":"unsignedint"}]},
                            {"index":2,"fields":[{"name":"pin","value":"3","type":"unsignedint"},{"name":"value","value":"1","type":"unsignedint"}]},
                            {"index":3,"fields":[{"name":"pin","value":"4","type":"unsignedint"},{"name":"value","value":"0","type":"signedint"}]},
                            {"index":4,"fields":[{"name":"pin","value":"5","type":"unsignedint"},{"name":"value","value":"20","type":"unsignedint"}]},
                            {"index":5,"fields":[{"name":"pin","value":"6","type":"unsignedint"},{"name":"value","value":"True","type":"boolean"}]},
                            {"index":6,"fields":[{"name":"pin","value":"7","type":"unsignedint"},{"name":"value","value":"False","type":"boolean"}]},
                            {"index":7,"fields":[{"name":"pin","value":"8","type":"unsignedint"},{"name":"value","value":"False","type":"boolean"}]},
                            {"index":8,"fields":[{"name":"pin","value":"9","type":"unsignedint"},{"name":"value","value":"19","type":"unsignedint"}]},
                            {"index":9,"fields":[{"name":"pin","value":"10","type":"unsignedint"},{"name":"value","value":"1","type":"unsignedint"}]},
                            {"index":10,"fields":[{"name":"pin","value":"11","type":"unsignedint"},{"name":"value","value":"0","type":"signedint"}]},
                            {"index":11,"fields":[{"name":"pin","value":"12","type":"unsignedint"},{"name":"value","value":"60","type":"unsignedint"}]},
                            {"index":12,"fields":[{"name":"pin","value":"13","type":"unsignedint"},{"name":"value","value":"True","type":"boolean"}]},
                            {"index":13,"fields":[{"name":"pin","value":"14","type":"unsignedint"},{"name":"value","value":"False","type":"boolean"}]},
                            {"index":14,"fields":[{"name":"pin","value":"15","type":"unsignedint"},{"name":"value","value":"False","type":"boolean"}]},
                            {"index":15,"fields":[{"name":"pin","value":"16","type":"unsignedint"},{"name":"value","value":"19","type":"unsignedint"}]},
                            {"index":16,"fields":[{"name":"pin","value":"17","type":"unsignedint"},{"name":"value","value":"1","type":"unsignedint"}]},
                            {"index":17,"fields":[{"name":"pin","value":"18","type":"unsignedint"},{"name":"value","value":"0","type":"signedint"}]},
                            {"index":18,"fields":[{"name":"pin","value":"19","type":"unsignedint"},{"name":"value","value":"60","type":"unsignedint"}]},
                            {"index":19,"fields":[{"name":"pin","value":"20","type":"unsignedint"},{"name":"value","value":"True","type":"boolean"}]},
                            {"index":20,"fields":[{"name":"pin","value":"21","type":"unsignedint"},{"name":"value","value":"False","type":"boolean"}]},
                            {"index":21,"fields":[{"name":"pin","value":"22","type":"unsignedint"},{"name":"value","value":"False","type":"boolean"}]},
                            {"index":22,"fields":[{"name":"pin","value":"23","type":"unsignedint"},{"name":"value","value":"19","type":"unsignedint"}]},
                            {"index":23,"fields":[{"name":"pin","value":"24","type":"unsignedint"},{"name":"value","value":"1","type":"unsignedint"}]},
                            {"index":24,"fields":[{"name":"pin","value":"25","type":"unsignedint"},{"name":"value","value":"0","type":"signedint"}]},
                            {"index":25,"fields":[{"name":"pin","value":"26","type":"unsignedint"},{"name":"value","value":"60","type":"unsignedint"}]},
                            {"index":26,"fields":[{"name":"pin","value":"27","type":"unsignedint"},{"name":"value","value":"True","type":"boolean"}]},
                            {"index":27,"fields":[{"name":"pin","value":"28","type":"unsignedint"},{"name":"value","value":"False","type":"boolean"}]},
                            {"index":28,"fields":[{"name":"pin","value":"29","type":"unsignedint"},{"name":"value","value":"False","type":"boolean"}]},
                            {"index":29,"fields":[{"name":"pin","value":"30","type":"unsignedint"},{"name":"value","value":"False","type":"boolean"}]},
                            {"index":30,"fields":[{"name":"pin","value":"31","type":"unsignedint"},{"name":"value","value":"1","type":"unsignedint"}]},
                            {"index":31,"fields":[{"name":"pin","value":"32","type":"unsignedint"},{"name":"value","value":"0","type":"unsignedint"}]},
                            {"index":32,"fields":[{"name":"pin","value":"33","type":"unsignedint"},{"name":"value","value":"0","type":"unsignedint"}]},
                            {"index":33,"fields":[{"name":"pin","value":"34","type":"unsignedint"},{"name":"value","value":"0","type":"unsignedint"}]},
                            {"index":34,"fields":[{"name":"pin","value":"35","type":"unsignedint"},{"name":"value","value":"0","type":"unsignedint"}]},
                            {"index":35,"fields":[{"name":"pin","value":"36","type":"unsignedint"},{"name":"value","value":"0","type":"unsignedint"}]},
                            {"index":36,"fields":[{"name":"pin","value":"37","type":"unsignedint"},{"name":"value","value":"0","type":"unsignedint"}]},
                            {"index":37,"fields":[{"name":"pin","value":"38","type":"unsignedint"},{"name":"value","value":"0","type":"unsignedint"}]},
                            {"index":38,"fields":[{"name":"pin","value":"40","type":"unsignedint"},{"name":"value","value":"0","type":"unsignedint"}]},
                            {"index":39,"fields":[{"name":"pin","value":"41","type":"unsignedint"},{"name":"value","value":"180","type":"unsignedint"}]},
                            {"index":40,"fields":[{"name":"pin","value":"42","type":"unsignedint"},{"name":"value","value":"0","type":"unsignedint"}]},
                            {"index":41,"fields":[{"name":"pin","value":"43","type":"unsignedint"},{"name":"value","value":"180","type":"unsignedint"}]},
                            {"index":42,"fields":[{"name":"pin","value":"44","type":"unsignedint"},{"name":"value","value":"0","type":"unsignedint"}]},
                            {"index":43,"fields":[{"name":"pin","value":"45","type":"unsignedint"},{"name":"value","value":"180","type":"unsignedint"}]},
                            {"index":44,"fields":[{"name":"pin","value":"46","type":"unsignedint"},{"name":"value","value":"0","type":"unsignedint"}]},
                            {"index":45,"fields":[{"name":"pin","value":"47","type":"unsignedint"},{"name":"value","value":"180","type":"unsignedint"}]}
                        ]}]},
                    {"index":1,"fields":[
                        {"name":"sin","value":"20","type":"unsignedint"},
                        {"name":"propList","type":"array","elements":[
                            {"index":0,"fields":[{"name":"pin","value":"1","type":"unsignedint"},{"name":"value","value":"0","type":"enum"}]},
                            {"index":1,"fields":[{"name":"pin","value":"2","type":"unsignedint"},{"name":"value","value":"True","type":"boolean"}]},
                            {"index":2,"fields":[{"name":"pin","value":"3","type":"unsignedint"},{"name":"value","value":"1","type":"enum"}]},
                            {"index":3,"fields":[{"name":"pin","value":"4","type":"unsignedint"},{"name":"value","value":"606001373","type":"signedint"}]},
                            {"index":4,"fields":[{"name":"pin","value":"5","type":"unsignedint"},{"name":"value","value":"-7576521","type":"signedint"}]},
                            {"index":5,"fields":[{"name":"pin","value":"6","type":"unsignedint"},{"name":"value","value":"3047667","type":"signedint"}]},
                            {"index":6,"fields":[{"name":"pin","value":"7","type":"unsignedint"},{"name":"value","value":"-38103","type":"signedint"}]},
                            {"index":7,"fields":[{"name":"pin","value":"8","type":"unsignedint"},{"name":"value","value":"149","type":"signedint"}]},
                            {"index":8,"fields":[{"name":"pin","value":"9","type":"unsignedint"},{"name":"value","value":"0","type":"unsignedint"}]},
                            {"index":9,"fields":[{"name":"pin","value":"10","type":"unsignedint"},{"name":"value","value":"3099","type":"unsignedint"}]},
                            {"index":10,"fields":[{"name":"pin","value":"11","type":"unsignedint"},{"name":"value","value":"1760533233","type":"signedint"}]},
                            {"index":11,"fields":[{"name":"pin","value":"12","type":"unsignedint"},{"name":"value","value":"479","type":"unsignedint"}]},
                            {"index":12,"fields":[{"name":"pin","value":"13","type":"unsignedint"},{"name":"value","value":"0","type":"enum"}]},
                            {"index":13,"fields":[{"name":"pin","value":"14","type":"unsignedint"},{"name":"value","value":"0","type":"enum"}]},
                            {"index":14,"fields":[{"name":"pin","value":"15","type":"unsignedint"},{"name":"value","value":"0","type":"unsignedint"}]},
                            {"index":15,"fields":[{"name":"pin","value":"16","type":"unsignedint"},{"name":"value","value":"1","type":"enum"}]},
                            {"index":16,"fields":[{"name":"pin","value":"17","type":"unsignedint"},{"name":"value","value":"False","type":"boolean"}]},
                            {"index":17,"fields":[{"name":"pin","value":"18","type":"unsignedint"},{"name":"value","value":"4","type":"unsignedint"}]},
                            {"index":18,"fields":[{"name":"pin","value":"19","type":"unsignedint"},{"name":"value","value":"0","type":"unsignedint"}]},
                            {"index":19,"fields":[{"name":"pin","value":"20","type":"unsignedint"},{"name":"value","value":"180","type":"unsignedint"}]},
                            {"index":20,"fields":[{"name":"pin","value":"21","type":"unsignedint"},{"name":"value","value":"0","type":"unsignedint"}]},
                            {"index":21,"fields":[{"name":"pin","value":"22","type":"unsignedint"},{"name":"value","value":"0","type":"enum"}]},
                            {"index":22,"fields":[{"name":"pin","value":"23","type":"unsignedint"},{"name":"value","value":"False","type":"boolean"}]},
                            {"index":23,"fields":[{"name":"pin","value":"24","type":"unsignedint"},{"name":"value","value":"9","type":"unsignedint"}]},
                            {"index":24,"fields":[{"name":"pin","value":"25","type":"unsignedint"},{"name":"value","value":"8","type":"unsignedint"}]},
                            {"index":25,"fields":[{"name":"pin","value":"26","type":"unsignedint"},{"name":"value","value":"0","type":"unsignedint"}]},
                            {"index":26,"fields":[{"name":"pin","value":"27","type":"unsignedint"},{"name":"value","value":"65535","type":"unsignedint"}]},
                            {"index":27,"fields":[{"name":"pin","value":"30","type":"unsignedint"},{"name":"value","value":"False","type":"boolean"}]},
                            {"index":28,"fields":[{"name":"pin","value":"31","type":"unsignedint"},{"name":"value","value":"False","type":"boolean"}]},
                            {"index":29,"fields":[{"name":"pin","value":"32","type":"unsignedint"},{"name":"value","value":"0","type":"signedint"}]},
                            {"index":30,"fields":[{"name":"pin","value":"33","type":"unsignedint"},{"name":"value","value":"0","type":"signedint"}]},
                            {"index":31,"fields":[{"name":"pin","value":"35","type":"unsignedint"},{"name":"value","value":"300","type":"unsignedint"}]},
                            {"index":32,"fields":[{"name":"pin","value":"36","type":"unsignedint"},{"name":"value","value":"1","type":"unsignedint"}]},
                            {"index":33,"fields":[{"name":"pin","value":"37","type":"unsignedint"},{"name":"value","value":"-1","type":"signedint"}]},
                            {"index":34,"fields":[{"name":"pin","value":"39","type":"unsignedint"},{"name":"value","value":"400","type":"unsignedint"}]},
                            {"index":35,"fields":[{"name":"pin","value":"40","type":"unsignedint"},{"name":"value","value":"1","type":"unsignedint"}]},
                            {"index":36,"fields":[{"name":"pin","value":"41","type":"unsignedint"},{"name":"value","value":"-1","type":"signedint"}]},
                            {"index":37,"fields":[{"name":"pin","value":"43","type":"unsignedint"},{"name":"value","value":"450","type":"unsignedint"}]},
                            {"index":38,"fields":[{"name":"pin","value":"44","type":"unsignedint"},{"name":"value","value":"3","type":"unsignedint"}]},
                            {"index":39,"fields":[{"name":"pin","value":"45","type":"unsignedint"},{"name":"value","value":"-1","type":"signedint"}]},
                            {"index":40,"fields":[{"name":"pin","value":"47","type":"unsignedint"},{"name":"value","value":"5000","type":"unsignedint"}]},
                            {"index":41,"fields":[{"name":"pin","value":"48","type":"unsignedint"},{"name":"value","value":"0","type":"unsignedint"}]},
                            {"index":42,"fields":[{"name":"pin","value":"49","type":"unsignedint"},{"name":"value","value":"-1","type":"signedint"}]},
                            {"index":43,"fields":[{"name":"pin","value":"51","type":"unsignedint"},{"name":"value","value":"True","type":"boolean"}]},
                            {"index":44,"fields":[{"name":"pin","value":"52","type":"unsignedint"},{"name":"value","value":"False","type":"boolean"}]},
                            {"index":45,"fields":[{"name":"pin","value":"53","type":"unsignedint"},{"name":"value","value":"True","type":"boolean"}]},
                            {"index":46,"fields":[{"name":"pin","value":"54","type":"unsignedint"},{"name":"value","value":"False","type":"boolean"}]}
                        ]}]}]}]}
        )
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