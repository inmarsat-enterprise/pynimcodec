"""Application class provides a file-level container for a Messages codec."""

from enum import Enum

from pynimcodec.utils import camel_case
from .message import Messages, create_message


class Application:
    """A wrapper for Messages providing JSON file context/metadata."""
    
    def __init__(self, **kwargs) -> None:
        self._application = 'cbcApplication'
        self.application = kwargs.get('name', self._application)
        self._version = '1.0'
        self.version = kwargs.get('version', self._version)
        self._description = None
        self.description = kwargs.get('description', None)
        self._messages: Messages = None
        if kwargs.get('messages'):
            self.messages = kwargs.get('messages')
    
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
