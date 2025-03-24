"""Application class provides a file-level container for a Messages codec."""

from enum import Enum

import aiocoap

from pynimcodec.utils import camel_case

from pynimcodec.bitman import extract_from_buffer
from .constants import MessageDirection
from .message import Messages, create_message


class Application:
    """A wrapper for Messages providing JSON file context/metadata."""
    
    def __init__(self, messages: Messages, **kwargs) -> None:
        """Create a new Application.
        
        Args:
            messages (Messages): The messages for the application
            **application (str): The application name
            **version (str): A version intended to use semver
            **description (str): Optional description of intent/overview
        """
        self._application: str = 'cbcApplication'
        self._version: str = '1.0'
        self._description: 'str|None' = None
        self._messages: Messages = None
        self.application = kwargs.pop('application', self._application)
        self.version = kwargs.pop('version', self._version)
        self.description = kwargs.pop('description', None)
        self.messages = messages
    
    @property
    def application(self) -> str:
        return self._application
    
    @application.setter
    def application(self, value: str):
        if not isinstance(value, str) or not value:
            raise ValueError('Invalid name must be non-empty string.')
        self._application = value
    
    @property
    def version(self) -> str:
        return self._version
    
    @version.setter
    def version(self, value: str):
        def valid_int(v) -> bool:
            try:
                _ = int(v)
                return True
            except ValueError:
                return False
        # main function below
        if not isinstance(value, str):
            raise ValueError('Invalid name must be semver string.')
        parts = value.split('.')
        if len(parts) > 4 or not all(valid_int(p) for p in parts):
            raise ValueError('Invalid semver string.')
        self._version = value
    
    @property
    def description(self) -> 'str|None':
        return self._description
    
    @description.setter
    def description(self, value: str):
        if not isinstance(value, str) and value is not None:
            raise ValueError('Invalid description must be string or None.')
        if value == '':
            value = None
        self._description = value
    
    @property
    def messages(self) -> Messages:
        return self._messages
    
    @messages.setter
    def messages(self, value: Messages):
        if not isinstance(value, Messages):
            raise ValueError('Invalid Messages codec list.')
        self._messages = value
    
    def to_json(self):
        key_order = ['application', 'version', 'description', 'messages']
        raw = {}
        for attr_name in dir(self.__class__):
            if (not isinstance(getattr(self.__class__, attr_name), property) or
                attr_name.startswith('_') or
                getattr(self, attr_name) is None or
                getattr(self, attr_name) in ['']):
                # skip
                continue
            elif isinstance(getattr(self, attr_name), Messages):
                raw[attr_name] = []
                for msg in getattr(self, attr_name):
                    raw[attr_name].append(msg.to_json())
            elif (issubclass(getattr(self, attr_name).__class__, Enum)):
                raw[attr_name] = getattr(self, attr_name).value
            else:
                raw[attr_name] = getattr(self, attr_name)
        reordered = { camel_case(k): raw[k] for k in key_order if k in raw }
        remaining = { camel_case(k): raw[k] for k in raw if k not in key_order }
        reordered.update(remaining)
        return reordered
    
    def encode(self, content: dict, **kwargs) -> 'bytes|aiocoap.Message':
        """Encode the message content.
        
        Args:
            content (dict): Must include `name` and a `value` dict.
            **coap (bool): If True, returns an aiocoap Message. If not present
                the encoded header will be the 2-byte message_id.
        """
        if (not isinstance(content, dict) or
            not all(k in content for k in ['name', 'value'])):
            raise ValueError('Invalid content must be dict with name, value')
        name = content.get('name')
        message_codec = self.messages[name]
        if 'coap' not in kwargs or kwargs.get('coap') is False:
            kwargs['nim'] = True
        return message_codec.encode(content, **kwargs)
    
    def decode(self, buffer: bytes, direction: MessageDirection, **kwargs) -> dict:
        """Decode a message buffer into a dictionary value.
        
        The message buffer should include overhead either 2-bytes message_key
        or 5+ bytes CoAP using message_key as the CoAP Message ID.
        
        Args:
            buffer (bytes): The message buffer to decode.
            **direction (MessageDirection): The direction of communication.
            **message_key (int): May be supplied instead of `name`. Must be
                accompanied by `direction`.
            **coap (bool): Optional indicates the buffer includes CoAP header.
        """
        if not isinstance(buffer, (bytes, bytearray)) or len(buffer) < 2:
            raise ValueError('Invalid data buffer must be at least 2 bytes')
        if isinstance(direction, str):
            direction = MessageDirection[direction]
        if not isinstance(direction, MessageDirection):
            raise ValueError('Invalid message direction')
        coap = kwargs.pop('coap', None)
        if coap is True and len(buffer) < 5:
            raise ValueError('Invalid data buffer for CoAP must be >= 5 bytes')
        if coap is None:
            coap = (len(buffer) >= 5 and
                    buffer[0] >> 6 == 1 and 
                    0xFF in buffer)
        message_key_offset = 16 if coap else 0
        message_key = extract_from_buffer(buffer, message_key_offset, 16)
        for message_codec in self.messages:
            if (message_codec.direction == direction and 
                message_codec.message_key == message_key):
                if coap is True:
                    kwargs['coap'] = True
                else:
                    kwargs['nim'] = True
                return message_codec.decode(buffer, **kwargs)
        raise ValueError(f'No message codec found for {direction.name}' +
                         f' message key {message_key}')


def create_application(obj: dict) -> Application:
    """Creates a Message from a dictionary definition."""
    if not isinstance(obj, dict):
        raise ValueError('Invalid object to create Application.')
    if not isinstance(obj['messages'], list):
        raise ValueError('Invalid messages list')
    for i, msg in enumerate(obj['message']):
        obj['messages'][i] = create_message(msg)
    obj['messages'] = Messages(obj['fields'])
    return Application(**obj)
