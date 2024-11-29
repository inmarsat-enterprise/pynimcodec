import os

from pynimcodec.nimo.xmlparser import parse_xml_file


test_file = os.path.join(os.getcwd(), 'tests/examples/nimotestxml.idpmsg')

def test_xmlparser():
    if not os.path.exists(test_file):
        raise ValueError
    root = parse_xml_file(test_file)
    assert root is not None
    