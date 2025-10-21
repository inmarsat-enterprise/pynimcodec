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
    encode_message,
)

logging.basicConfig()
logger = logging.getLogger()

SC1000_DECODE_TEST_CASES = {
    'blockageReport': {
        'exclude': False, # Working
        'codec': os.path.join(os.getcwd(), 'secrets/viasat_sc1000.idpmsg'),
        'raw_payload': "NxtnxXDrKUAxTGHO6qwEAAAAAAAEgA==",
        'decoded': dict({
            "name": "blockageReport",
            "codecServiceId": 55,
            "codecMessageId": 27,
            "fields": [
                {
                    "name": "timestamp",
                    "value": "1740992747",
                    "type": "unsignedint"
                },
                {
                    "name": "reportSource",
                    "value": "blockage",
                    "type": "enum"
                },
                {
                    "name": "batteryVoltage",
                    "value": "40",
                    "type": "unsignedint"
                },
                {
                    "name": "internalTemperature",
                    "value": "6",
                    "type": "signedint"
                },
                {
                    "name": "latitude",
                    "value": "2722873",
                    "type": "signedint"
                },
                {
                    "name": "longitude",
                    "value": "-4543743",
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
                    "name": "motionState",
                    "value": "False",
                    "type": "boolean"
                },
                {
                    "name": "staleFix",
                    "value": "False",
                    "type": "boolean"
                },
                {
                    "name": "blockageDuration",
                    "value": "9",
                    "type": "unsignedint"
                }
            ]
        })
    },
    'positionBasicReport': {
        'exclude': False, # Working
        'codec': os.path.join(os.getcwd(), 'secrets/viasat_sc1000.idpmsg'),
        'raw_payload': "NxRnxYXUITgxTGH26qwU",
        'decoded': dict({
            "name": "positionBasicReport",
            "codecServiceId": 55,
            "codecMessageId": 20,
            "fields": [
                {
                    "name": "timestamp",
                    "value": "1740998100",
                    "type": "unsignedint"
                },
                {
                    "name": "reportSource",
                    "value": "stationaryPeriodic",
                    "type": "enum"
                },
                {
                    "name": "batteryVoltage",
                    "value": "39",
                    "type": "unsignedint"
                },
                {
                    "name": "internalTemperature",
                    "value": "6",
                    "type": "signedint"
                },
                {
                    "name": "latitude",
                    "value": "2722878",
                    "type": "signedint"
                },
                {
                    "name": "longitude",
                    "value": "-4543739",
                    "type": "signedint"
                },
                {
                    "name": "motionState",
                    "value": "False",
                    "type": "boolean"
                },
                {
                    "name": "staleFix",
                    "value": "False",
                    "type": "boolean"
                }
            ]
        })
    },
    'positionPlusReport':{
        'exclude': False, # Working
        'codec': os.path.join(os.getcwd(), 'secrets/viasat_sc1000.idpmsg'),
        'raw_payload': "NxVo9olGcSBhTGIG6qw4AACA",
        'decoded': dict({
            "name": "positionPlusReport",
            "codecServiceId": 55,
            "codecMessageId": 21,
            "fields": [
                {
                    "name": "timestamp",
                    "type": "unsignedint",
                    "value": "1760987462"
                },
                {
                    "name": "reportSource",
                    "type": "enum",
                    "value": "heartbeatPeriodic"
                },
                {
                    "name": "batteryVoltage",
                    "type": "unsignedint",
                    "value": "36"
                },
                {
                    "name": "internalTemperature",
                    "type": "signedint",
                    "value": "12"
                },
                {
                    "name": "latitude",
                    "type": "signedint",
                    "value": "2722880"
                },
                {
                    "name": "longitude",
                    "type": "signedint",
                    "value": "-4543730"
                },
                {
                    "name": "speed",
                    "type": "unsignedint",
                    "value": "0"
                },
                {
                    "name": "heading",
                    "type": "unsignedint",
                    "value": "0"
                },
                {
                    "name": "motionState",
                    "type": "boolean",
                    "value": "False"
                },
                {
                    "name": "staleFix",
                    "type": "boolean",
                    "value": "True"
                }
            ]
        })
    },
    'diagnosticReport': {
        'exclude': False, # Working
        'codec': os.path.join(os.getcwd(), 'secrets/viasat_sc1000.idpmsg'),
        'raw_payload': "NxpnwHVy8UfpTGJe6qvsAQIAAAAAAAAAAAAAAAAAAAAAAAA=",
        'decoded': dict({
            "name": "diagnosticReport",
            "codecServiceId": 55,
            "codecMessageId": 26,
            "fields": [
                {
                    "name": "timestamp",
                    "value": "1740666226",
                    "type": "unsignedint"
                },
                {
                    "name": "reportSource",
                    "value": "BLERequest",
                    "type": "enum"
                },
                {
                    "name": "batteryVoltage",
                    "value": "40",
                    "type": "unsignedint"
                },
                {
                    "name": "internalTemperature",
                    "value": "-3",
                    "type": "signedint"
                },
                {
                    "name": "latitude",
                    "value": "2722891",
                    "type": "signedint"
                },
                {
                    "name": "longitude",
                    "value": "-4543749",
                    "type": "signedint"
                },
                {
                    "name": "speed",
                    "value": "0",
                    "type": "unsignedint"
                },
                {
                    "name": "heading",
                    "value": "129",
                    "type": "unsignedint"
                },
                {
                    "name": "motionState",
                    "value": "False",
                    "type": "boolean"
                },
                {
                    "name": "staleFix",
                    "value": "False",
                    "type": "boolean"
                },
                {
                    "name": "sensorTriggerID",
                    "value": "0",
                    "type": "unsignedint"
                },
                {
                    "name": "sensor1Type",
                    "value": "None",
                    "type": "enum"
                },
                {
                    "name": "sensor1Value",
                    "value": "0",
                    "type": "signedint"
                },
                {
                    "name": "sensor1BatteryLevel",
                    "value": "0",
                    "type": "unsignedint"
                },
                {
                    "name": "sensor2Type",
                    "value": "None",
                    "type": "enum"
                },
                {
                    "name": "sensor2Value",
                    "value": "0",
                    "type": "signedint"
                },
                {
                    "name": "sensor2BatteryLevel",
                    "value": "0",
                    "type": "unsignedint"
                },
                {
                    "name": "sensor3Type",
                    "value": "None",
                    "type": "enum"
                },
                {
                    "name": "sensor3Value",
                    "value": "0",
                    "type": "signedint"
                },
                {
                    "name": "sensor3BatteryLevel",
                    "value": "0",
                    "type": "unsignedint"
                },
                {
                    "name": "sensor4Type",
                    "value": "None",
                    "type": "enum"
                },
                {
                    "name": "sensor4Value",
                    "value": "0",
                    "type": "signedint"
                },
                {
                    "name": "sensor4BatteryLevel",
                    "value": "0",
                    "type": "unsignedint"
                },
                {
                    "name": "serviceStatus",
                    "value": "False",
                    "type": "boolean"
                },
                {
                    "name": "serviceHours",
                    "value": "0",
                    "type": "unsignedint"
                },
                {
                    "name": "rawGNSSJammingValue",
                    "value": "0",
                    "type": "unsignedint"
                },
                {
                    "name": "droppedMessageCount",
                    "value": "0",
                    "type": "unsignedint"
                }
            ]
        })
    },
    'getTerminalInfoReply': {
        'exclude': False, # Working
        'codec': os.path.join(os.getcwd(), 'secrets/viasat_sc1000.idpmsg'),
        'raw_payload': "Nw1nwHWbEQAGAgEBAAAC",
        'decoded': dict({
            "name": "getTerminalInfoReply",
            "codecServiceId": 55,
            "codecMessageId": 13,
            "fields": [
                {
                    "name": "timestamp",
                    "value": "1740666267",
                    "type": "unsignedint"
                },
                {
                    "name": "hardwareVariant",
                    "value": "17",
                    "type": "unsignedint"
                },
                {
                    "name": "hardwareVersion",
                    "value": "0",
                    "type": "unsignedint"
                },
                {
                    "name": "firmwareVersionMajor",
                    "value": "6",
                    "type": "unsignedint"
                },
                {
                    "name": "firmwareVersionMinor",
                    "value": "2",
                    "type": "unsignedint"
                },
                {
                    "name": "firmwareVersionPatch",
                    "value": "1",
                    "type": "unsignedint"
                },
                {
                    "name": "bluetoothVersionMajor",
                    "value": "1",
                    "type": "unsignedint"
                },
                {
                    "name": "bluetoothVersionMinor",
                    "value": "0",
                    "type": "unsignedint"
                },
                {
                    "name": "bluetoothVersionPatch",
                    "value": "0",
                    "type": "unsignedint"
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
        'exclude': False, # Working
        'codec': os.path.join(os.getcwd(), 'secrets/viasat_sc1000.idpmsg'),
        'raw_payload': "NxBnwHWbCAE=",
        'decoded': dict({
            "name": "getReportPeriodReply",
            "codecServiceId": 55,
            "codecMessageId": 16,
            "fields": [
                {
                    "name": "timestamp",
                    "value": "1740666267",
                    "type": "unsignedint"
                },
                {
                    "name": "stationaryTimePeriod",
                    "value": "8",
                    "type": "unsignedint"
                },
                {
                    "name": "movingTimePeriod",
                    "value": "1",
                    "type": "unsignedint"
                }
            ]
        })
    }
}

SC1000_ENCODE_TEST_CASES = {
    'getTerminalInfo': {
        'exclude': False,
        'codec': os.path.join(os.getcwd(), 'secrets/viasat_sc1000.idpmsg'),
        'raw_payload': "Nw0=",
        'encode': dict({
            "codecServiceId": 55,
            "codecMessageId": 13,
            "fields":[
                # Empty
            ]
        })
    },
    'setReportPeriod': {
        'exclude': False,
        'codec': os.path.join(os.getcwd(), 'secrets/viasat_sc1000.idpmsg'),
        'raw_payload': "NwEEAQ==",
        'encode': dict({
            "codecServiceId": 55,
            "codecMessageId": 1,
            "fields":[
                {
                    "name": "stationaryTimePeriod",
                    "value": "4"
                },
                {
                    "name": "movingTimePeriod",
                    "value": "1"
                }
            ]
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
    """"""
    for test_inputs in SC1000_ENCODE_TEST_CASES.values():
        if not test_inputs.get('exclude', False):
            logger.debug(f"\n")
            test_codec = test_inputs.get('codec')
            expected_raw_payload = test_inputs.get('raw_payload')
            to_encode: dict = test_inputs.get('encode')
            
            encoded_raw_payload = encode_message(to_encode, test_codec, override_sin=True)

            logger.debug(f"--- EXPECTED: \n{expected_raw_payload}")
            logger.debug(f"----- RESULT: \n{encoded_raw_payload.decode('utf-8')}")
            assert(expected_raw_payload == encoded_raw_payload.decode('utf-8'))
