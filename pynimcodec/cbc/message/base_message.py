"""Compact Binary Codec Message class and methods."""

from enum import Enum

import aiocoap

from pynimcodec.bitman import append_bytes_to_buffer
from pynimcodec.cbc.codec.base_codec import CbcCodec, CodecList
from pynimcodec.cbc.constants import MessageDirection
from pynimcodec.cbc.field.base_field import Fields, encode_fields, decode_fields
from pynimcodec.cbc.field.common import create_field
from pynimcodec.utils import camel_case


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
    
    def to_json(self):
        key_order = ['name', 'direction', 'message_key', 'description', 'fields']
        raw = {}
        for attr_name in dir(self.__class__):
            if (not isinstance(getattr(self.__class__, attr_name), property) or
                attr_name.startswith('_') or
                getattr(self, attr_name) is None or
                getattr(self, attr_name) in ['']):
                # skip
                continue
            elif isinstance(getattr(self, attr_name), Fields):
                raw[attr_name] = []
                for fld in getattr(self, attr_name):
                    raw[attr_name].append(fld.to_json())
            elif (issubclass(getattr(self, attr_name).__class__, Enum)):
                raw[attr_name] = getattr(self, attr_name).value
            else:
                raw[attr_name] = getattr(self, attr_name)
        reordered = {}
        reordered = { camel_case(k): raw[k] for k in key_order if k in raw }
        remaining = { camel_case(k): raw[k] for k in raw if k not in key_order }
        reordered.update(remaining)
        return reordered
    

class Messages(CodecList[Message]):
    """Container class for a list of Message codecs with unique names."""
    
    def __init__(self, *args) -> None:
        super().__init__(Message, *args)
    
    def append(self, codec: Message) -> bool:
        """Append uniquely named Message codec to the end of the list.
        
        Args:
            codec (Message): The message codec.
        
        Raises:
            ValueError: If duplicate `message_key` for the direction, or
                duplicate `name` in the list.
        """
        for mc in self:
            if (mc.message_key == codec.message_key and
                mc.direction == codec.direction):
                raise ValueError(f'Duplicate {mc.direction.name} message_key')
        return super().append(codec)
    
    def by_key(self, message_key: int, direction: MessageDirection) -> Message:
        """Get a Message using message_key and direction."""
        if message_key not in range(0, 2**16):
            raise ValueError('Invalid message_key must be 16-bit unsigned int')
        if isinstance(direction, str):
            try:
                direction = MessageDirection(direction)
            except ValueError as exc:
                raise ValueError('Invalid message direction') from exc
        if not isinstance(direction, MessageDirection):
            raise ValueError('Invalid direction')
        for m in self:
            if m.message_key == message_key and m.direction == direction:
                return m
        raise ValueError('message_key and direction not found')
    
    def decode(self, buffer: bytes, **kwargs) -> dict:
        """Decode a message from a buffer.
        
        Args:
            buffer (bytes): The buffer to decode from.
            **name (str): The unique name of the message in Messages. If not
                specified must set `direction` and any of `message_key`, `nim`,
                or `coap`.
            **direction (MessageDirection|str): The message direction is
                required if unique `name` is not specified.
            **message_key (int): May be supplied instead of `name`. Must be
                accompanied by `direction`.
            **nim (bool): Indicates the buffer begins with the 2-byte
                `message_key`.
            **coap (bool): Indicates the buffer includes CoAP header.
            **incl_dir (bool): If set, include `direction` in output.
            **incl_key (bool): If set, include `message_key` in output.
            **incl_desc (bool): If set, include `description` in output.
            
        """
        if not isinstance(buffer, (bytes, bytearray)) or len(buffer) == 0:
            raise ValueError('Invalid buffer')
        return decode_message(buffer, messages=self, **kwargs)
    
    def encode(self, content: dict, **kwargs) -> bytes:
        """Encodes a message based on content in a dictionary.
        
        Args:
            content (dict): The message content to encode. Must include keys
                `name` (str) and `value` (list)
            **nim (bool): Optional flag indicating to apply `message_key` as
                the first 2 bytes of NIM message overhead
            **coap (bool): Optional flag indicating to generate CoAP overhead
                using `message_key` as the MessageID in header
        
        Returns:
            bytes: The encoded message buffer.
        
        Raises:
            ValueError: If the content is invalid or both `nim` and `coap` flags
                are set.
        """
        return encode_message(content, messages=self, **kwargs)


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


def decode_message(buffer: bytes, **kwargs) -> dict:
    """Decodes a Message from a data buffer.
    
    Which Message codec to use is determined by parsing either the first two
    bytes of Non-IP over-the-air data received, or the 3rd-4th bytes if using
    Constrained Application Protocol (CoAP) transport.
    
    Args:
        buffer (bytes): The data buffer containing the message payload.
            May include NIM or CoAP header bytes.
        **messages (Messages): The messages codec list to use for decoding.
            Must be present if not using `message`.
        **message (Message): The message codec to use for decoding.
            Must be present if notusing `messages`.
        **name (str): The unique name of the message in Messages. If not
            specified must set `direction` and any of `message_key`, `nim`,
            or `coap`.
        **direction (MessageDirection|str): The message direction is
            required if unique `name` is not specified.
        **message_key (int): May be supplied instead of `name`. Must be
            accompanied by `direction`.
        **nim (bool): Indicates the buffer begins with the 2-byte
            `message_key`.
        **coap (bool): Indicates the buffer includes CoAP header.
        **incl_dir (bool): If set, include `direction` in output.
        **incl_key (bool): If set, include `message_key` in output.
        **incl_desc (bool): If set, include `description` in output.
    
    Returns:
        dict: The decoded message structure.
    """
    if not isinstance(buffer, (bytes, bytearray)) or len(buffer) == 0:
        raise ValueError('Invalid data buffer.')
    messages = kwargs.get('messages')
    if messages and not isinstance(messages, Messages):
        raise ValueError('Invalid Messages codec list.')
    message = kwargs.get('message')
    if message and not isinstance(message, Message):
        raise ValueError('Invalid Message codec.')
    name = kwargs.get('name')
    direction = kwargs.get('direction')
    message_key = kwargs.get('message_key')
    nim = kwargs.get('nim') is True
    coap = kwargs.get('coap') is True
    offset = 0   # starting bit offset to read buffer from
    if not message:
        if name:
            message = messages[name]
        else:
            if isinstance(direction, str):
                try:
                    direction = MessageDirection(direction)
                except ValueError as exc:
                    raise ValueError('Invalid message direction') from exc
            if not direction:
                raise ValueError('direction required when name not provided')
            if message_key:
                if message_key not in range(0, 2**16):
                    raise ValueError('message_key must be 16-bit unsigned int')
                for m in messages:
                    if m.message_key == message_key and m.direction == direction:
                        message = m
                        break
        if nim and coap:
            raise ValueError('nim and coap flags mutually exclusive')
        if not message and not ((nim or coap) and direction):
            raise ValueError('Missing name or message_key/nim/coap and direction')
        if nim:
            message_key = int.from_bytes(buffer[0:2])
            offset = 16
        elif coap:
            coap_message = aiocoap.Message.decode(buffer)
            message_key = coap_message.mid
            buffer = coap_message.payload
        if not message:
            message = messages.by_key(message_key, direction)
    if message_key and message_key != message.message_key:
        raise ValueError('Mismatch between provided/derived message_key')
    decoded = { 'name': message.name }
    if kwargs.get('incl_dir') is True:
        decoded['direction'] = message.direction.value
    if kwargs.get('incl_key') is True:
        decoded['messageKey'] = message.message_key
    if message.description and kwargs.get('incl_desc') is True:
        decoded['description'] = message.description
    decoded['value'], _ = decode_fields(message, buffer, offset)
    return decoded


def encode_message(content: dict, **kwargs) -> 'bytes|aiocoap.Message':
    """Encodes message content using a message definition.
    
    The data bytes produced will be appended to either the first two bytes of
    Non-IP over-the-air data or as the CoAP MessageID (3rd-4th bytes).
    If using the `coap` flag, the output will be a `aiocoap.Message` allowing
    the caller to apply any necessary overhead before final encoding.
    
    Args:
        content (dict): The message content data structure.
        **messages (Messages): The messages codec list to use for encoding.
            Must be present if not using `message`.
        **message (Message): The message codec to use for encoding.
            Must be present if notusing `messages`.
        **nim (bool): Include the message_key as the first 2 bytes for transport.
        **coap (bool): Create a CoAP message using message_key as MessageID
    
    Returns:
        bytes: The data buffer for payload (without message_key header bytes)
    """
    req_keys = ['name', 'value']
    if not isinstance(content, dict) or not all(k in content for k in req_keys):
        raise ValueError(f'Content missing keys ({req_keys})')
    if not all(isinstance(f, dict) for f in content['value']):
        raise ValueError('Invalid content values.')
    messages = kwargs.get('messages')
    message = kwargs.get('message')
    nim = kwargs.get('nim') is True
    coap = kwargs.get('coap') is True
    if messages and not isinstance(messages, Messages):
        raise ValueError('Invalid Messages codec list.')
    if message and not isinstance(message, Message):
        raise ValueError('Invalid Message codec.')
    if not messages and not message:
        raise ValueError('Missing codec list or codec.')
    if not message:
        try:
            message = messages[content['name']]
        except ValueError as exc:
            raise ValueError(f'Codec not found for {content["name"]}') from exc
    if content['name'] != message.name:
        raise ValueError('Mismatch content name and Message name')
    buffer = bytearray()
    offset = 0
    if nim:
        if coap:
            raise ValueError('nim and coap are mutually exclusive flags')
        buffer = append_bytes_to_buffer(message.message_key.to_bytes(2, 'big'),
                                        buffer,
                                        offset)
        offset = 16
    buffer, offset = encode_fields(content, message, buffer, offset)
    if coap:
        return aiocoap.Message(mid=message.message_key, payload=bytes(buffer))
    return bytes(buffer)            
