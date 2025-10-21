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

DECODE_TEST_CASES = {
    'getProperties': {
        'exclude': False,
        'codec': os.path.join(os.getcwd(), 'secrets/luaTerminals.idpmsg'),
        'raw_payload': "EAUMEBEBSTiAEgFA0AAIYKgeBgAA6AQIAAFKaLnVggtQArzECGKAFeYgQ0g9ILQCCAURACJAEFDERsBAABAAA0AAIydBQAAxA5BBhKV3GCkAAWgADCDQABxB5CBCJCSAATQACgABVAALIABdAAMIABlAANENkJDYCgDAiA0HgIQKgBBkAAOgACEAASgACkAAWgADEAAagCDkAQegCEEAQigCEkAQmgCFEAQqgAFkDwugBGEAAyQ2gUHjEy4BMCQJgaAEEYAAqA8GMHIIIJQJhSAELYABiDwNMOIPIQQJiKAESYACaDwUMVIWIXQJjCAEZYADSDwbMcIdIeIfQAkCAAhQAESAAjQAEiAAlQAEyAAoQAFKLQqQAFaLQsQAFqLQuQAF6LQULwEAAEYGAEEcSD20Ngrv+MYKUGcAF0B6g7v//ayQIYFBKAEKQABbmi506gMSA7QaAAOAAHoABAAIiQkgEE0AAoi0FUAQsAAXIYQFjKAcaQADaf//HiHyIGABCwAI0gJYSIASVn+TpAZAoQAlLP8rSA4RYgDLWf5ekTiDBAAYs/zMzQjUzYhUdASAkgJYBoPAQwUwaBTMytzGyuZcyMLoDkEIAQlAAFIAAtAAGIAA1AAHIAA9AAIIABFAAJEJkKIABVFoLELkMABGSGiGzHgAj7AAWKQEgIAQGgIBAAAqAEGAEDkEAACQABQAwtIH0BiBQNIOIPAAIEKgCFkBAuAAYQAjwAR8ARAgIIQAESAEjMkAASgAJgBk6QPoKEChSRURWAIsACWkZEeACPUBB8AA/QAi5YAmBIBQNAUCGCoBQZAQDoBwggkgpAAFoAgxAAGoAg5IEsB6AEQoAI0AEqACdABSgArQAWoAL0AGKADNABqgA3QAcoAO0AHqAD9ACCgBDQAioAR0AJKAEtACagBPQAooAU0AKqAFdACwAAyygIAAIgMgQAAKkD6AZAoDoAAhACEpA+gKSD6AWgADAABpBxB4ABBIH0CKBQSQACaAEUSB9AqkH0BZAALgAGCGSGgADaQPoHECg6gAHkAI+kD6CBIPoEKAAiAARkSESgAJkgfQToFChAAUoASpIH0FaQfQLEABaRcRekOEDBACYs4jJh4ZsDzQjUjZAAboAThJOIHKU4gOkrsseAAPUAB8AA/QAIJIyABHQCpCABJU/////qCABRQCqSABTU/////rSABbQCriABdU/////siABlQCsyABnU/////tAAGkmomsADYkD6G1Ao3IAG9AC4JA+hxSD6DkgAcwAOhOpOwAHdIH0PCBR5QAPSAF7SB9D4kH0H1AANAoCYEQGgeBEAAKY2IgMFElzYXREYXRhIFBybyAtIE1vZGVtAoDGJoXGBgbAcDzAxMDgyMDU4U0tZQTQyRgRQAIQWUCwDNS4wBkBASAAKAAFgBDCDSDjD0BQgAoRSBiIkYmRABgKHgCQCgaAEA=",
        'decoded': dict({
            "name": "propertyValues",
            "codecMessageId": 5,
            "codecServiceId": 16,
            "fields": [
                    {
                        "name": "list",
                        "type": "array",
                        "elements": [
                            {
                                "index": 0,
                                "fields": [
                                    {
                                        "name": "sin",
                                        "value": "16",
                                        "type": "unsignedint"
                                    },
                                    {
                                        "name": "propList",
                                        "type": "array",
                                        "elements": [
                                            {
                                                "index": 0,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "1",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "10000",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 1,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "2",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "5",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 2,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "3",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "0",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 3,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "4",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "True",
                                                        "type": "boolean"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 4,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "5",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "30",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 5,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "6",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "0",
                                                        "type": "enum"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 6,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "7",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "4",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 7,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "8",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "0",
                                                        "type": "enum"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 8,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "10",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "1757009282",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 9,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "11",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "5740673",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 10,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "12",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "5740673",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 11,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "13",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "False",
                                                        "type": "boolean"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 12,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "15",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "1440",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 13,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "16",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "5",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 14,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "17",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "1",
                                                        "type": "enum"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 15,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "18",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "4",
                                                        "type": "enum"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 16,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "20",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "True",
                                                        "type": "boolean"
                                                    }
                                                ]
                                            }
                                        ]
                                    }
                                ]
                            },
                            {
                                "index": 1,
                                "fields": [
                                    {
                                        "name": "sin",
                                        "value": "17",
                                        "type": "unsignedint"
                                    },
                                    {
                                        "name": "propList",
                                        "type": "array",
                                        "elements": [
                                            {
                                                "index": 0,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "1",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "0",
                                                        "type": "enum"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 1,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "2",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "0",
                                                        "type": "enum"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 2,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "3",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "0",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 3,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "4",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "-99",
                                                        "type": "signedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 4,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "5",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "0",
                                                        "type": "enum"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 5,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "6",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "False",
                                                        "type": "boolean"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 6,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "7",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "False",
                                                        "type": "boolean"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 7,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "8",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "True",
                                                        "type": "boolean"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 8,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "9",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "24006",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 9,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "10",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "0",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 10,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "11",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "0",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 11,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "12",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "False",
                                                        "type": "boolean"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 12,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "13",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "0",
                                                        "type": "enum"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 13,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "14",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "False",
                                                        "type": "boolean"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 14,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "15",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "False",
                                                        "type": "boolean"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 15,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "16",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "False",
                                                        "type": "boolean"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 16,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "17",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "False",
                                                        "type": "boolean"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 17,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "18",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "0",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 18,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "19",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "0",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 19,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "20",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "0",
                                                        "type": "enum"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 20,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "21",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "0",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 21,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "22",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "0",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 22,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "23",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "0",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 23,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "24",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "0",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 24,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "25",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "0",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 25,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "26",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "False",
                                                        "type": "boolean"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 26,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "27",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "False",
                                                        "type": "boolean"
                                                    }
                                                ]
                                            }
                                        ]
                                    }
                                ]
                            },
                            {
                                "index": 2,
                                "fields": [
                                    {
                                        "name": "sin",
                                        "value": "18",
                                        "type": "unsignedint"
                                    },
                                    {
                                        "name": "propList",
                                        "type": "array",
                                        "elements": [
                                            {
                                                "index": 0,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "1",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "3",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 1,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "2",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "False",
                                                        "type": "boolean"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 2,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "3",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "60",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 3,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "4",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "False",
                                                        "type": "boolean"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 4,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "5",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "1",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 5,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "6",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "0",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 6,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "7",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "0",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 7,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "8",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "0",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 8,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "9",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "0",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 9,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "10",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "0",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 10,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "11",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "0",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 11,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "12",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "0",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 12,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "13",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "2",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 13,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "14",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "2",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 14,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "15",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "2",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 15,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "16",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "2",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 16,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "17",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "2",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 17,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "18",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "2",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 18,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "19",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "2",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 19,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "20",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "2",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 20,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "21",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "0",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 21,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "22",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "30",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 22,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "23",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "1",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 23,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "24",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "0",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 24,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "25",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "False",
                                                        "type": "boolean"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 25,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "27",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "20",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 26,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "30",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "True",
                                                        "type": "boolean"
                                                    }
                                                ]
                                            }
                                        ]
                                    }
                                ]
                            },
                            {
                                "index": 3,
                                "fields": [
                                    {
                                        "name": "sin",
                                        "value": "19",
                                        "type": "unsignedint"
                                    },
                                    {
                                        "name": "propList",
                                        "type": "array",
                                        "elements": [
                                            {
                                                "index": 0,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "1",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "True",
                                                        "type": "boolean"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 1,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "2",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "19",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 2,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "3",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "1",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 3,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "4",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "0",
                                                        "type": "signedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 4,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "5",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "15",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 5,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "6",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "True",
                                                        "type": "boolean"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 6,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "7",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "False",
                                                        "type": "boolean"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 7,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "8",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "False",
                                                        "type": "boolean"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 8,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "9",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "19",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 9,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "10",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "1",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 10,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "11",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "0",
                                                        "type": "signedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 11,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "12",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "60",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 12,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "13",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "True",
                                                        "type": "boolean"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 13,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "14",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "False",
                                                        "type": "boolean"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 14,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "15",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "False",
                                                        "type": "boolean"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 15,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "16",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "19",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 16,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "17",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "1",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 17,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "18",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "0",
                                                        "type": "signedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 18,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "19",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "60",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 19,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "20",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "True",
                                                        "type": "boolean"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 20,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "21",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "False",
                                                        "type": "boolean"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 21,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "22",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "False",
                                                        "type": "boolean"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 22,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "23",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "19",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 23,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "24",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "1",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 24,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "25",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "0",
                                                        "type": "signedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 25,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "26",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "60",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 26,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "27",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "True",
                                                        "type": "boolean"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 27,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "28",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "False",
                                                        "type": "boolean"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 28,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "29",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "False",
                                                        "type": "boolean"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 29,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "30",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "False",
                                                        "type": "boolean"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 30,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "31",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "1",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 31,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "32",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "0",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 32,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "33",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "0",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 33,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "34",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "0",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 34,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "35",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "0",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 35,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "36",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "0",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 36,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "37",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "0",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 37,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "38",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "0",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 38,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "40",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "0",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 39,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "41",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "180",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 40,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "42",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "0",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 41,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "43",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "180",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 42,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "44",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "0",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 43,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "45",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "180",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 44,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "46",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "0",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 45,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "47",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "180",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            }
                                        ]
                                    }
                                ]
                            },
                            {
                                "index": 4,
                                "fields": [
                                    {
                                        "name": "sin",
                                        "value": "20",
                                        "type": "unsignedint"
                                    },
                                    {
                                        "name": "propList",
                                        "type": "array",
                                        "elements": [
                                            {
                                                "index": 0,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "1",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "0",
                                                        "type": "enum"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 1,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "2",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "True",
                                                        "type": "boolean"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 2,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "3",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "1",
                                                        "type": "enum"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 3,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "4",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "606001691",
                                                        "type": "signedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 4,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "5",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "-7577435",
                                                        "type": "signedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 5,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "6",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "3047669",
                                                        "type": "signedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 6,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "7",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "-38108",
                                                        "type": "signedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 7,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "8",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "10",
                                                        "type": "signedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 8,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "9",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "1",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 9,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "10",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "0",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 10,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "11",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "1757008808",
                                                        "type": "signedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 11,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "12",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "474",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 12,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "13",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "0",
                                                        "type": "enum"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 13,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "14",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "0",
                                                        "type": "enum"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 14,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "15",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "0",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 15,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "16",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "1",
                                                        "type": "enum"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 16,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "17",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "False",
                                                        "type": "boolean"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 17,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "18",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "4",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 18,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "19",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "0",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 19,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "20",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "180",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 20,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "21",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "2",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 21,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "22",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "0",
                                                        "type": "enum"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 22,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "23",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "False",
                                                        "type": "boolean"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 23,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "24",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "11",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 24,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "25",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "7",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 25,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "26",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "0",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 26,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "27",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "65535",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 27,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "30",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "False",
                                                        "type": "boolean"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 28,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "31",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "False",
                                                        "type": "boolean"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 29,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "32",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "0",
                                                        "type": "signedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 30,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "33",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "0",
                                                        "type": "signedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 31,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "35",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "300",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 32,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "36",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "1",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 33,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "37",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "-1",
                                                        "type": "signedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 34,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "39",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "400",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 35,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "40",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "1",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 36,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "41",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "-1",
                                                        "type": "signedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 37,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "43",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "450",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 38,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "44",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "3",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 39,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "45",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "-1",
                                                        "type": "signedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 40,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "47",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "5000",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 41,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "48",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "0",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 42,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "49",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "-1",
                                                        "type": "signedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 43,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "51",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "True",
                                                        "type": "boolean"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 44,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "52",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "False",
                                                        "type": "boolean"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 45,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "53",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "True",
                                                        "type": "boolean"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 46,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "54",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "False",
                                                        "type": "boolean"
                                                    }
                                                ]
                                            }
                                        ]
                                    }
                                ]
                            },
                            {
                                "index": 5,
                                "fields": [
                                    {
                                        "name": "sin",
                                        "value": "21",
                                        "type": "unsignedint"
                                    },
                                    {
                                        "name": "propList",
                                        "type": "array",
                                        "elements": [
                                            {
                                                "index": 0,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "1",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "False",
                                                        "type": "boolean"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 1,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "2",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "300",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 2,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "3",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "60",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 3,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "4",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "True",
                                                        "type": "boolean"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 4,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "5",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "True",
                                                        "type": "boolean"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 5,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "6",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "fences.dat",
                                                        "type": "string"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 6,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "7",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "False",
                                                        "type": "boolean"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 7,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "8",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "1",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 8,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "9",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "0",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 9,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "10",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "0",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 10,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "11",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "0",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 11,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "12",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "0",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 12,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "13",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "0",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 13,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "14",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "0",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 14,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "15",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "0",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 15,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "16",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "0",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 16,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "17",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "0",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 17,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "18",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "False",
                                                        "type": "boolean"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 18,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "19",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "False",
                                                        "type": "boolean"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 19,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "20",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "0",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 20,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "21",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "180",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 21,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "22",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "False",
                                                        "type": "boolean"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 22,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "23",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "False",
                                                        "type": "boolean"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 23,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "24",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "1",
                                                        "type": "enum"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 24,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "25",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "False",
                                                        "type": "boolean"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 25,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "26",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "False",
                                                        "type": "boolean"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 26,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "27",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "True",
                                                        "type": "boolean"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 27,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "30",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "1",
                                                        "type": "enum"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 28,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "31",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "0",
                                                        "type": "signedint"
                                                    }
                                                ]
                                            }
                                        ]
                                    }
                                ]
                            },
                            {
                                "index": 6,
                                "fields": [
                                    {
                                        "name": "sin",
                                        "value": "22",
                                        "type": "unsignedint"
                                    },
                                    {
                                        "name": "propList",
                                        "type": "array",
                                        "elements": [
                                            {
                                                "index": 0,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "1",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "False",
                                                        "type": "boolean"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 1,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "2",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "2",
                                                        "type": "enum"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 2,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "3",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "8",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 3,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "4",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "0",
                                                        "type": "enum"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 4,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "5",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "1",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 5,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "6",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "2",
                                                        "type": "enum"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 6,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "7",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "False",
                                                        "type": "boolean"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 7,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "8",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "0",
                                                        "type": "enum"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 8,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "9",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "0",
                                                        "type": "enum"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 9,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "10",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "3",
                                                        "type": "enum"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 10,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "11",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "1000",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 11,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "12",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "20",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 12,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "13",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "False",
                                                        "type": "boolean"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 13,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "14",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "False",
                                                        "type": "boolean"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 14,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "15",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "0",
                                                        "type": "enum"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 15,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "16",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "False",
                                                        "type": "boolean"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 16,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "21",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "2",
                                                        "type": "enum"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 17,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "22",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "8",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 18,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "23",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "0",
                                                        "type": "enum"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 19,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "24",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "1",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 20,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "30",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "1",
                                                        "type": "enum"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 21,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "31",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "2",
                                                        "type": "enum"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 22,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "32",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "8",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 23,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "33",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "0",
                                                        "type": "enum"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 24,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "34",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "1",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 25,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "35",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "True",
                                                        "type": "boolean"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 26,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "36",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "0",
                                                        "type": "enum"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 27,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "37",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "0",
                                                        "type": "enum"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 28,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "38",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "3",
                                                        "type": "enum"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 29,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "39",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "1000",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 30,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "40",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "20",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 31,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "41",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "False",
                                                        "type": "boolean"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 32,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "42",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "False",
                                                        "type": "boolean"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 33,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "43",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "2",
                                                        "type": "enum"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 34,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "44",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "1",
                                                        "type": "enum"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 35,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "45",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "False",
                                                        "type": "boolean"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 36,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "50",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "False",
                                                        "type": "boolean"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 37,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "60",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "2",
                                                        "type": "enum"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 38,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "61",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "8",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 39,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "62",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "0",
                                                        "type": "enum"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 40,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "63",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "1",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            }
                                        ]
                                    }
                                ]
                            },
                            {
                                "index": 7,
                                "fields": [
                                    {
                                        "name": "sin",
                                        "value": "23",
                                        "type": "unsignedint"
                                    },
                                    {
                                        "name": "propList",
                                        "type": "array",
                                        "elements": [
                                            {
                                                "index": 0,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "1",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "True",
                                                        "type": "boolean"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 1,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "2",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "5",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 2,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "3",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "10",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 3,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "4",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "True",
                                                        "type": "boolean"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 4,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "5",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "5",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 5,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "6",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "8",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 6,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "7",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "7",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 7,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "8",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "False",
                                                        "type": "boolean"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 8,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "9",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "False",
                                                        "type": "boolean"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 9,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "10",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "0",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 10,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "11",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "2",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 11,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "12",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "0",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 12,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "13",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "2",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 13,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "14",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "600",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 14,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "15",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "1",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 15,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "16",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "",
                                                        "type": "data"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 16,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "17",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "",
                                                        "type": "data"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 17,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "18",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "",
                                                        "type": "data"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 18,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "19",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "",
                                                        "type": "data"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 19,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "20",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "",
                                                        "type": "data"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 20,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "21",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "",
                                                        "type": "data"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 21,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "22",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "",
                                                        "type": "data"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 22,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "23",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "",
                                                        "type": "data"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 23,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "24",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "",
                                                        "type": "data"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 24,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "25",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "",
                                                        "type": "data"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 25,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "26",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "",
                                                        "type": "data"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 26,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "27",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "",
                                                        "type": "data"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 27,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "28",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "",
                                                        "type": "data"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 28,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "29",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "",
                                                        "type": "data"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 29,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "30",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "",
                                                        "type": "data"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 30,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "31",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "",
                                                        "type": "data"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 31,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "32",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "",
                                                        "type": "data"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 32,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "33",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "",
                                                        "type": "data"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 33,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "34",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "",
                                                        "type": "data"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 34,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "35",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "",
                                                        "type": "data"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 35,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "36",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "",
                                                        "type": "data"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 36,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "37",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "",
                                                        "type": "data"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 37,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "38",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "",
                                                        "type": "data"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 38,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "39",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "",
                                                        "type": "data"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 39,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "40",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "",
                                                        "type": "data"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 40,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "41",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "",
                                                        "type": "data"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 41,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "42",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "",
                                                        "type": "data"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 42,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "43",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "",
                                                        "type": "data"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 43,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "44",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "0",
                                                        "type": "enum"
                                                    }
                                                ]
                                            }
                                        ]
                                    }
                                ]
                            },
                            {
                                "index": 8,
                                "fields": [
                                    {
                                        "name": "sin",
                                        "value": "25",
                                        "type": "unsignedint"
                                    },
                                    {
                                        "name": "propList",
                                        "type": "array",
                                        "elements": [
                                            {
                                                "index": 0,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "1",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "0",
                                                        "type": "enum"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 1,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "2",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "False",
                                                        "type": "boolean"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 2,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "3",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "False",
                                                        "type": "boolean"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 3,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "4",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "0",
                                                        "type": "enum"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 4,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "5",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "1000",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 5,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "6",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "20",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 6,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "7",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "0",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 7,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "8",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "1",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 8,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "9",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "1000",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 9,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "10",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "2000",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 10,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "11",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "0",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 11,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "12",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "0",
                                                        "type": "enum"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 12,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "13",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "False",
                                                        "type": "boolean"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 13,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "14",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "False",
                                                        "type": "boolean"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 14,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "15",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "0",
                                                        "type": "enum"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 15,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "16",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "1000",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 16,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "17",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "20",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 17,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "18",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "0",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 18,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "19",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "1",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 19,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "20",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "1000",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 20,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "21",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "2000",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 21,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "22",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "0",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 22,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "23",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "0",
                                                        "type": "enum"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 23,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "24",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "False",
                                                        "type": "boolean"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 24,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "25",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "False",
                                                        "type": "boolean"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 25,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "26",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "0",
                                                        "type": "enum"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 26,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "27",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "1000",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 27,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "28",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "20",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 28,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "29",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "0",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 29,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "30",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "1",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 30,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "31",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "1000",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 31,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "32",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "2000",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 32,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "33",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "0",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 33,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "34",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "0",
                                                        "type": "enum"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 34,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "35",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "False",
                                                        "type": "boolean"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 35,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "36",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "False",
                                                        "type": "boolean"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 36,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "37",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "0",
                                                        "type": "enum"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 37,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "38",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "1000",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 38,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "39",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "20",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 39,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "40",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "0",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 40,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "41",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "1",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 41,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "42",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "1000",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 42,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "43",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "2000",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 43,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "44",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "0",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 44,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "45",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "False",
                                                        "type": "boolean"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 45,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "46",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "False",
                                                        "type": "boolean"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 46,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "47",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "3600",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 47,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "48",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "1",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 48,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "49",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "-30",
                                                        "type": "signedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 49,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "50",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "60",
                                                        "type": "signedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 50,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "51",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "15",
                                                        "type": "signedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 51,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "52",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "False",
                                                        "type": "boolean"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 52,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "53",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "False",
                                                        "type": "boolean"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 53,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "54",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "0",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 54,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "55",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "1",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 55,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "56",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "10000",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 56,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "57",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "20000",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 57,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "58",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "23958",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 58,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "60",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "0",
                                                        "type": "enum"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 59,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "61",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "0",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 60,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "62",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "0",
                                                        "type": "enum"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 61,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "63",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "0",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 62,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "65",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "False",
                                                        "type": "boolean"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 63,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "70",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "0",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 64,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "71",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "5",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 65,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "72",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "0",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 66,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "73",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "2147483647",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 67,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "80",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "0",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 68,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "81",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "5",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 69,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "82",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "0",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 70,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "83",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "2147483647",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 71,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "90",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "0",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 72,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "91",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "5",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 73,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "92",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "0",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 74,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "93",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "2147483647",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 75,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "100",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "0",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 76,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "101",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "5",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 77,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "102",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "0",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 78,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "103",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "2147483647",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 79,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "104",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "0",
                                                        "type": "enum"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 80,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "105",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "False",
                                                        "type": "boolean"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 81,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "106",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "False",
                                                        "type": "boolean"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 82,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "107",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "0",
                                                        "type": "enum"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 83,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "108",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "1000",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 84,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "109",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "20",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 85,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "110",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "0",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 86,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "111",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "1",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 87,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "112",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "1000",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 88,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "113",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "2000",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 89,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "114",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "0",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 90,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "115",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "0",
                                                        "type": "enum"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 91,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "116",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "False",
                                                        "type": "boolean"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 92,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "117",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "False",
                                                        "type": "boolean"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 93,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "118",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "0",
                                                        "type": "enum"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 94,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "119",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "1000",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 95,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "120",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "20",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 96,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "121",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "0",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 97,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "122",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "1",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 98,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "123",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "1000",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 99,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "124",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "2000",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 100,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "125",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "0",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            }
                                        ]
                                    }
                                ]
                            },
                            {
                                "index": 9,
                                "fields": [
                                    {
                                        "name": "sin",
                                        "value": "26",
                                        "type": "unsignedint"
                                    },
                                    {
                                        "name": "propList",
                                        "type": "array",
                                        "elements": [
                                            {
                                                "index": 0,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "1",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "True",
                                                        "type": "boolean"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 1,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "2",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "False",
                                                        "type": "boolean"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 2,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "3",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "30",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 3,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "4",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "0",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 4,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "5",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "True",
                                                        "type": "boolean"
                                                    }
                                                ]
                                            }
                                        ]
                                    }
                                ]
                            },
                            {
                                "index": 10,
                                "fields": [
                                    {
                                        "name": "sin",
                                        "value": "27",
                                        "type": "unsignedint"
                                    },
                                    {
                                        "name": "propList",
                                        "type": "array",
                                        "elements": [
                                            {
                                                "index": 0,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "1",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "IsatData Pro - Modem",
                                                        "type": "string"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 1,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "2",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "14.006",
                                                        "type": "string"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 2,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "3",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "01082058SKYA42F",
                                                        "type": "string"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 3,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "4",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "1082058",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 4,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "5",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "5.0",
                                                        "type": "string"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 5,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "6",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "8",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 6,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "9",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "0",
                                                        "type": "enum"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 7,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "10",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "0",
                                                        "type": "enum"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 8,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "11",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "1",
                                                        "type": "enum"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 9,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "12",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "False",
                                                        "type": "boolean"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 10,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "13",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "False",
                                                        "type": "boolean"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 11,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "14",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "True",
                                                        "type": "boolean"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 12,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "15",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "10",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 13,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "16",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "10",
                                                        "type": "enum"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 14,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "17",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "785",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 15,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "18",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "True",
                                                        "type": "boolean"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 16,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "19",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "False",
                                                        "type": "boolean"
                                                    }
                                                ]
                                            }
                                        ]
                                    }
                                ]
                            },
                            {
                                "index": 11,
                                "fields": [
                                    {
                                        "name": "sin",
                                        "value": "32",
                                        "type": "unsignedint"
                                    },
                                    {
                                        "name": "propList",
                                        "type": "array",
                                        "elements": [
                                            {
                                                "index": 0,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "1",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "120",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 1,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "2",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "5",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            },
                                            {
                                                "index": 2,
                                                "fields": [
                                                    {
                                                        "name": "pin",
                                                        "value": "3",
                                                        "type": "unsignedint"
                                                    },
                                                    {
                                                        "name": "value",
                                                        "value": "1",
                                                        "type": "unsignedint"
                                                    }
                                                ]
                                            }
                                        ]
                                    }
                                ]
                            }
                        ]
                    }
                ]
        })
    },
}

def test_message_definitions_decode_properties():
    """"""
    for test_inputs in DECODE_TEST_CASES.values():
        if not test_inputs.get('exclude', False):
            test_codec = test_inputs.get('codec')
            raw_payload = test_inputs.get('raw_payload')
            if isinstance(raw_payload, (list)):
                data = bytes(raw_payload)
            else:
                data = base64.b64decode(raw_payload)
            decoded = decode_message(data, test_codec, override_sin=True)
            expected: dict = test_inputs.get('decoded')
            logger.debug(f"\n--- EXPECTED: \n{expected}")
            logger.debug(f"\n----- RESULT: \n{decoded}")
            for k, v in expected.items():
                if k != 'Fields':
                    assert k in decoded and decoded[k] == v
                else:
                    for i, field in enumerate(v):
                        for fk, fv in field.items():
                            assert fk in decoded['Fields'][i] and fv == decoded['Fields'][i][fk]