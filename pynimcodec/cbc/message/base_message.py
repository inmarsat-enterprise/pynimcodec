"""Compact Binary Codec Message class and methods."""

from pynimcodec.bitman import append_bytes_to_buffer
from pynimcodec.cbc.codec.base_codec import CbcCodec, CodecList
from pynimcodec.cbc.constants import MessageDirection
from pynimcodec.cbc.field.base_field import Fields, encode_fields, decode_fields
from pynimcodec.cbc.field.common import create_field


class Message(CbcCodec):
    """A message data structure."""
    
    required_args = ['name', 'direction', 'message_key', 'fields']
    
    def __init__(self,
                 name: str,
                 direction: MessageDirection,
                 message_key: int,
                 fields: Fields,
                 **kwargs) -> None:
        super().__init__(name, kwargs.pop('description', None))
        self._direction: MessageDirection = None
        self._message_key: int = None
        self._fields: Fields = None
        self._coap_compatible: bool = kwargs.get('coap_compatible', True)
        self._vsat_reserved: bool = kwargs.get('vsat_reserved', False)
        self._nimo_compatible: bool = kwargs.get('nimo_compatible', False)
        self.direction = direction
        self.message_key = message_key
        self.fields = fields
    
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


def create_message(obj: dict) -> Message:
    """Creates a Message from a dictionary definition."""
    if not isinstance(obj, dict):
        raise ValueError('Invalid object to create Message.')
    if 'messageKey' in obj:
        obj['message_key'] = obj.pop('messageKey')
    if not all(k in obj for k in Message.required_args):
        raise ValueError(f'Missing required argument ({Message.required_args})')
    valid_msgdir = [e.value for e in MessageDirection]
    if not isinstance(obj['direction'], MessageDirection):
        if obj['direction'] not in valid_msgdir:
            raise ValueError(f'Invalid Message direction ({valid_msgdir})')
        obj['direction'] = MessageDirection(obj['direction'])
    if not isinstance(obj['fields'], list):
        raise ValueError('Invalid fields definition')
    for i, field in enumerate(obj['fields']):
        obj['fields'][i] = create_field(field)
    obj['fields'] = Fields(obj['fields'])
    return Message(**obj)


def decode_message(buffer: bytes, message: Message, **kwargs) -> dict:
    """Decodes a Message from a data buffer.
    
    Which Message codec to use is determined by parsing either the first two
    bytes of Non-IP over-the-air data received, or the 3rd-4th bytes if using
    Constrained Application Protocol (CoAP) transport.
    
    Args:
        buffer (bytes): The data buffer containing the message payload after
            removing the NIDD or CoAP header.
        message (Message): The message codec to use for decoding.
        **nim (bool): Indicates the buffer begins with the 2-byte message_key.
        **coap (bool): Indicates the buffer includes CoAP header.
    
    Returns:
        dict: The decoded message structure.
    """
    if not isinstance(buffer, (bytes, bytearray)) or len(buffer) == 0:
        raise ValueError('Invalid data buffer')
    if not isinstance(message, Message):
        raise ValueError('Invalid message codec')
    offset = 0
    if kwargs.get('nim') is True:
        if kwargs.get('coap') is True:
            raise ValueError('nim and coap are mutually exclusive flags')
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
    decoded['value'], _ = decode_fields(message, buffer, offset)
    return decoded


def encode_message(content: dict, message: Message, **kwargs) -> 'bytes':
    """Encodes message content using a message definition.
    
    The data bytes produced should be appended to either the first two bytes of
    Non-IP over-the-air data or as the CoAP MessageID (3rd-4th bytes).
    
    Args:
        content (dict): The message content data structure.
        message (Message): The message codec to use for encoding.
        **nim (bool): Include the message_key as the first 2 bytes for transport.
        **coap (bool): Create a CoAP message using message_key as MessageID
    
    Returns:
        bytes: The data buffer for payload (without message_key header bytes)
    """
    if (not isinstance(content, dict) or 'value' not in content
        or not all(isinstance(f, dict) for f in content['value'])):
        raise ValueError('Invalid content to encode.')
    if not isinstance(message, Message):
        raise ValueError('Invalid message codec.')
    buffer = bytearray()
    offset = 0
    if kwargs.get('nim') is True:
        if kwargs.get('coap') is True:
            raise ValueError('nim and coap are mutually exclusive flags')
        buffer = append_bytes_to_buffer(message.message_key.to_bytes(2, 'big'),
                                        buffer,
                                        offset)
        offset = 16
    if kwargs.get('coap') is True:
        raise NotImplementedError
    buffer, offset = encode_fields(content, message, buffer, offset)
    return bytes(buffer)            
