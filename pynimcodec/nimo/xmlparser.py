import logging
import xml.etree.ElementTree as ET

_log = logging.getLogger(__name__)


def parse_xml_file(filename: str):
    ns = dict([node for _, node in ET.iterparse(filename, events=['start-ns'])])
    tree = ET.parse(filename)
    root = tree.getroot()
    if root.tag != 'MessageDefinition':
        raise ValueError
    if not root.find('Services'):
        raise ValueError
    for service in root.iter('Service'):
        _log.debug('Service: %s (SIN: %s)',
                   service.find('Name').text,
                   service.find('SIN').text)
        return_messages = service.find('ReturnMessages')
        for message in return_messages.findall('Message'):
            _log.debug('Message: %s (MIN: %s)',
                       message.find('Name').text,
                       message.find('MIN').text)
            fields = message.find('Fields')
            for field in fields.findall('Field'):
                _log.debug('Field: %s (%s)', field.find('Name').text, field.get(f'{{{ns["xsi"]}}}type'))
    return root
