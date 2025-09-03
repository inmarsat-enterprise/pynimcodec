import os
import json
from collections import OrderedDict

from pynimcodec.nimo.xmlparser import parse_xml_file
from pynimcodec.nimo import (
    ET,
    XML_NAMESPACE,
    MessageDefinitions
)

#test_file = os.path.join(os.getcwd(), 'tests/examples/nimotestxml.idpmsg')
test_file = os.path.join(os.getcwd(), 'secrets/test.idpmsg')
#test_file = os.path.join(os.getcwd(), 'secrets/luaTerminals.idpmsg')

def test_xmlparser():
    if not os.path.exists(test_file):
        raise ValueError
    root = parse_xml_file(test_file)
    assert root is not None

def test_valid_codec():
    try:
        if test_file.endswith(('.idpmsg', '.xml', '.json')):
            md: MessageDefinitions = MessageDefinitions.from_mdf(
                test_file, override_sin=False
            )
            codec = md.json()
    except ET.ParseError:
        try:
           with open(test_file) as f:
               codec = json.load(f, object_pairs_hook=OrderedDict)
        except json.JSONDecodeError:
            raise ValueError('Unable to parse codec %s', test_file)