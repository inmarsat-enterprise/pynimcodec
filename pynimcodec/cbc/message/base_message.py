"""Compact Binary Codec Message class and methods."""

from pynimcodec.bitman import append_bytes_to_buffer, extract_from_buffer
from pynimcodec.cbc.codec.base_codec import CbcCodec, CodecList
from pynimcodec.cbc.constants import MessageDirection
from pynimcodec.cbc.field.base_field import Field, Fields, encode_fields


class Message(CbcCodec):
    """A message data structure."""
    
    def __init__(self,
                 name: str,
                 direction: MessageDirection,
                 message_key: int,
                 fields: Fields,
                 **kwargs) -> None:
        super().__init__(name, kwargs.pop('description'))
        self._direction: MessageDirection = None
        self.direction = direction
        self._message_key: int = None
        self.message_key = message_key
        self._fields: Fields = Fields()
        self.fields = fields
        self._coap_compatible: bool = kwargs.get('coap_compatible', True)
        self._vsat_reserved: bool = kwargs.get('vsat_reserved', False)
        self._nimo_compatible: bool = kwargs.get('nimo_compatible', False)
    
    @property
    def direction(self) -> MessageDirection:
        return self._direction
    
    @direction.setter
    def direction(self, value: MessageDirection):
        if not isinstance(value, MessageDirection):
            raise ValueError('Invalid direction type')
        self._direction = value
    
    @property
    def message_key(self) -> int:
        return self._message_key
    
    @message_key.setter
    def message_key(self, value: int):
        if not isinstance(value, int) or value not in range(0, 65536):
            raise ValueError('message_key must be a 16-bit unsigned integer')
        if self._coap_compatible and value < 49152:
            raise ValueError('message_key conflict with CoAP compatibility')
        if not self._vsat_reserved and value > 65279:
            raise ValueError('message_key conflict with Viasat reserved range')
        if self._nimo_compatible and value not in range(32768, 65280):
            raise ValueError('message_key conflict with NIMO compatibility')
        self._message_key = value

    @property
    def fields(self) -> Fields:
        return self._fields
    
    @fields.setter
    def fields(self, fields: Fields):
        if (not isinstance(fields, Fields)):
            raise ValueError('Invalid list of fields')
        self._fields = fields
    

class Messages(CodecList[Message]):
    """Container class for a list of Message codecs."""
    
    def __init__(self) -> None:
        super().__init__(Message)


def decode(buffer: bytes, message: Message, **kwargs) -> dict:
    """Decodes a Message from a data buffer.
    
    Which Message codec to use is determined by parsing either the first two
    bytes of raw over-the-air data received, or the 3rd-4th bytes if using
    Constrained Application Protocol (CoAP) transport.
    
    Args:
        buffer (bytes): The data buffer containing the message payload after
            removing the raw or CoAP header.
        message (Message): The message codec to use for decoding.
        **raw (bool): Indicates the buffer begins with the 2-byte message_key.
        **coap (bool): Indicates the buffer includes CoAP header.
    
    Returns:
        dict: The decoded message structure.
    """
    if not isinstance(buffer, (bytes, bytearray)) or len(buffer) == 0:
        raise ValueError('Invalid data buffer')
    if not isinstance(message, Message):
        raise ValueError('Invalid message codec')
    offset = 0
    if kwargs.get('raw') is True:
        if kwargs.get('coap') is True:
            raise ValueError('raw and coap are mutually exclusive flags')
        offset = 16
        message_key = int.from_bytes(buffer[0:2])
        if message_key != message.message_key:
            raise ValueError(f'Expected message key {message.message_key}'
                             f' but got {message_key}')
    if kwargs.get('coap') is True:
        raise NotImplementedError('TODO: parse CoAP header to set bit offset')
    decoded = { 'name': message.name }
    if message.description:
        decoded['description'] = message.description
    decoded['fields'] = []
    for field in message.fields:
        if field.optional is True:
            present = extract_from_buffer(buffer, offset, 1)
            offset += 1
            if not present:
                continue
        decoded_field, offset = field.decode(buffer, offset)
        decoded['fields'].append(decoded_field)


def encode(content: dict, message: Message, **kwargs) -> 'bytes':
    """Encodes message content using a message definition.
    
    The data bytes produced should be appended to either the first two bytes of
    raw over-the-air data or as the CoAP MessageID (3rd-4th bytes).
    
    Args:
        content (dict): The message content data structure.
        message (Message): The message codec to use for encoding.
        **raw (bool): Include the message_key as the first 2 bytes for transport.
        **coap (bool): Create a CoAP message using message_key as MessageID
    
    Returns:
        bytes: The data buffer for payload (without message_key header bytes)
    """
    # Embedded helper function
    def get_content_field(name: str) -> 'Field|None':
        for cfield in content['fields']:
            if cfield['name'] == name:
                return cfield
    # Main function
    if (not isinstance(content, dict) or 'fields' not in content
        or not all(isinstance(f, dict) for f in content['fields'])):
        raise ValueError('Invalid content to encode.')
    if not isinstance(message, Message):
        raise ValueError('Invalid message codec.')
    buffer = bytearray()
    offset = 0
    if kwargs.get('raw') is True:
        if kwargs.get('coap') is True:
            raise ValueError('raw and coap are mutually exclusive flags')
        buffer = append_bytes_to_buffer(message.message_key.to_bytes(2, 'big'))
        offset = 16
    if kwargs.get('coap') is True:
        raise NotImplementedError
    buffer, offset = encode_fields(content, message, buffer, offset)
    return bytes(buffer)            
