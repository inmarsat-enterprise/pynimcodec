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
    decode_message,
)

logging.basicConfig()
logger = logging.getLogger()

SC1000_DECODE_TEST_CASES = {
    'blockageReport': {
        'exclude': True,
        'codec': os.path.join(os.getcwd(), 'secrets/viasat_sc1000.idpmsg'),
        'raw_payload': "NxtnxXDrKUAxTGHO6qwEAAAAAAAEgA==",
        'decoded': dict({
            "name": "blockageReport",
            "codecServiceId": 55,
            "codecMessageId": 27,
            "fields": [
                {
                    "name": "timestamp",
                    "value": 1740992747,
                    "type": "uint"
                },
                {
                    "name": "reportSource",
                    "value": "blockage",
                    "type": "enum"
                },
                {
                    "name": "batteryVoltage",
                    "value": 40,
                    "type": "uint"
                },
                {
                    "name": "internalTemperature",
                    "value": 6,
                    "type": "int"
                },
                {
                    "name": "latitude",
                    "value": 2722873,
                    "type": "int"
                },
                {
                    "name": "longitude",
                    "value": -4543743,
                    "type": "int"
                },
                {
                    "name": "speed",
                    "value": 0,
                    "type": "uint"
                },
                {
                    "name": "heading",
                    "value": 0,
                    "type": "uint"
                },
                {
                    "name": "motionState",
                    "value": 0,
                    "type": "bool"
                },
                {
                    "name": "staleFix",
                    "value": 0,
                    "type": "bool"
                },
                {
                    "name": "blockageDuration",
                    "value": 9,
                    "type": "uint"
                }
            ]
        })
    },
    'positionBasicReport': {
        'exclude': True,
        'codec': os.path.join(os.getcwd(), 'secrets/viasat_sc1000.idpmsg'),
        'raw_payload': "NxRnxYXUITgxTGH26qwU",
        'decoded': dict({
            "name": "positionBasicReport",
            "codecServiceId": 55,
            "codecMessageId": 20,
            "fields": [
                {
                    "name": "timestamp",
                    "value": 1740998100,
                    "type": "uint"
                },
                {
                    "name": "reportSource",
                    "value": "stationaryPeriodic",
                    "type": "enum"
                },
                {
                    "name": "batteryVoltage",
                    "value": 39,
                    "type": "uint"
                },
                {
                    "name": "internalTemperature",
                    "value": 6,
                    "type": "int"
                },
                {
                    "name": "latitude",
                    "value": 2722878,
                    "type": "int"
                },
                {
                    "name": "longitude",
                    "value": -4543739,
                    "type": "int"
                },
                {
                    "name": "motionState",
                    "value": 0,
                    "type": "bool"
                },
                {
                    "name": "staleFix",
                    "value": 0,
                    "type": "bool"
                }
            ]
        })
    },
    'diagnosticReport': {
        'exclude': False,
        'codec': os.path.join(os.getcwd(), 'secrets/viasat_sc1000.idpmsg'),
        'raw_payload': "NxpnwHVy8UfpTGJe6qvsAQIAAAAAAAAAAAAAAAAAAAAAAAA=",
        'decoded': dict({
            "name": "diagnosticReport",
            "codecServiceId": 55,
            "codecMessageId": 26,
            "fields": [
                {
                    "name": "timestamp",
                    "value": 1740666226,
                    "type": "uint"
                },
                {
                    "name": "reportSource",
                    "value": "BLERequest",
                    "type": "enum"
                },
                {
                    "name": "batteryVoltage",
                    "value": 40,
                    "type": "uint"
                },
                {
                    "name": "internalTemperature",
                    "value": -3,
                    "type": "int"
                },
                {
                    "name": "latitude",
                    "value": 2722891,
                    "type": "int"
                },
                {
                    "name": "longitude",
                    "value": -4543749,
                    "type": "int"
                },
                {
                    "name": "speed",
                    "value": 0,
                    "type": "uint"
                },
                {
                    "name": "heading",
                    "value": 129,
                    "type": "uint"
                },
                {
                    "name": "motionState",
                    "value": 0,
                    "type": "bool"
                },
                {
                    "name": "staleFix",
                    "value": 0,
                    "type": "bool"
                },
                {
                    "name": "sensorTriggerID",
                    "value": 0,
                    "type": "uint"
                },
                {
                    "name": "sensor1Type",
                    "value": "None",
                    "type": "enum"
                },
                {
                    "name": "sensor1Value",
                    "value": 0,
                    "type": "int"
                },
                {
                    "name": "sensor1BatteryLevel",
                    "value": 0,
                    "type": "uint"
                },
                {
                    "name": "sensor2Type",
                    "value": "None",
                    "type": "enum"
                },
                {
                    "name": "sensor2Value",
                    "value": 0,
                    "type": "int"
                },
                {
                    "name": "sensor2BatteryLevel",
                    "value": 0,
                    "type": "uint"
                },
                {
                    "name": "sensor3Type",
                    "value": "None",
                    "type": "enum"
                },
                {
                    "name": "sensor3Value",
                    "value": 0,
                    "type": "int"
                },
                {
                    "name": "sensor3BatteryLevel",
                    "value": 0,
                    "type": "uint"
                },
                {
                    "name": "sensor4Type",
                    "value": "None",
                    "type": "enum"
                },
                {
                    "name": "sensor4Value",
                    "value": 0,
                    "type": "int"
                },
                {
                    "name": "sensor4BatteryLevel",
                    "value": 0,
                    "type": "uint"
                },
                {
                    "name": "serviceStatus",
                    "value": 0,
                    "type": "bool"
                },
                {
                    "name": "serviceHours",
                    "value": 0,
                    "type": "uint"
                },
                {
                    "name": "rawGNSSJammingValue",
                    "value": 0,
                    "type": "uint"
                },
                {
                    "name": "droppedMessageCount",
                    "value": 0,
                    "type": "uint"
                }
            ]
        })
    },
    'getTerminalInfoReply': {
        'exclude': True,
        'codec': os.path.join(os.getcwd(), 'secrets/viasat_sc1000.idpmsg'),
        'raw_payload': "Nw1nwHWbEQAGAgEBAAAC",
        'decoded': dict({
            "name": "getTerminalInfoReply",
            "codecServiceId": 55,
            "codecMessageId": 13,
            "fields": [
                {
                    "name": "timestamp",
                    "value": 1740666267,
                    "type": "uint"
                },
                {
                    "name": "hardwareVariant",
                    "value": 17,
                    "type": "uint"
                },
                {
                    "name": "hardwareVersion",
                    "value": 0,
                    "type": "uint"
                },
                {
                    "name": "firmwareVersionMajor",
                    "value": 6,
                    "type": "uint"
                },
                {
                    "name": "firmwareVersionMinor",
                    "value": 2,
                    "type": "uint"
                },
                {
                    "name": "firmwareVersionPatch",
                    "value": 1,
                    "type": "uint"
                },
                {
                    "name": "bluetoothVersionMajor",
                    "value": 1,
                    "type": "uint"
                },
                {
                    "name": "bluetoothVersionMinor",
                    "value": 0,
                    "type": "uint"
                },
                {
                    "name": "bluetoothVersionPatch",
                    "value": 0,
                    "type": "uint"
                },
                {
                    "name": "resetReason",
                    "value": "External",
                    "type": "enum"
                }
            ]
        })
    },
    'getReportPeriodReply': {
        'exclude': False,
        'codec': os.path.join(os.getcwd(), 'secrets/viasat_sc1000.idpmsg'),
        'raw_payload': "NxBnwHWbCAE=",
        'decoded': dict({
            "name": "getReportPeriodReply",
            "codecServiceId": 55,
            "codecMessageId": 16,
            "fields": [
                {
                    "name": "timestamp",
                    "value": 1740666267,
                    "type": "uint"
                },
                {
                    "name": "stationaryTimePeriod",
                    "value": 8,
                    "type": "uint"
                },
                {
                    "name": "movingTimePeriod",
                    "value": 1,
                    "type": "uint"
                }
            ]
        })
    }
}

SC1000_ENCODE_TEST_CASES = {
    'getTerminalInfo': {
        'exclude': True,
        'codec': os.path.join(os.getcwd(), 'secrets/viasat_sc1000.idpmsg'),
        'raw_payload': "Nw0=",
        'encode': dict({
            "codecServiceId": 55,
            "codecMessageId": 13,
            # "fields": [
            # ]
        })
    },
}

def test_message_definitions_decode_message():
    """"""
    for test_inputs in SC1000_DECODE_TEST_CASES.values():
        if not test_inputs.get('exclude', False):
            logger.debug(f"\n")
            test_codec = test_inputs.get('codec')
            raw_payload = test_inputs.get('raw_payload')
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
                            
def test_message_definitions_encode_message():
    
    for test_inputs in SC1000_ENCODE_TEST_CASES.values():
        if not test_inputs.get('exclude', False):
            logger.debug(f"\n")
            test_codec = test_inputs.get('codec')
            raw_payload = test_inputs.get('raw_payload')
            to_encode: dict = test_inputs.get('encode')
            
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
            
            logger.debug(f"--- EXPECTED: \n{raw_payload}")
            logger.debug(f"----- RESULT: \n{encoded}")