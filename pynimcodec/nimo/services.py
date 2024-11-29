"""Utilities for processing Services as collections of Messages."""
from warnings import warn

from . import ET
from .base import BaseCodec, CodecList
from .messages import MessageCodec, Messages


class ServiceCodec(BaseCodec):
    """A data structure holding a set of related Forward and Return Messages.
    
    Attributes:
        name (str): The service name
        sin (int): Service Identification Number or codec service id (16..255)
        description (str): A description of the service (unsupported)
        messages_forward (list): A list of mobile-terminated Message definitions
        messages_return (list): A list of mobile-originated Message definitions

    """
    def __init__(self,
                 name: str,
                 sin: int,
                 **kwargs) -> None:
        """Instantiates a Service made up of Messages.
        
        Args:
            name: The service name should be unique within a MessageDefinitions
            sin: The Service Identification Number (16..255)
        
        Keyword Args:
            description: (Optional)
            messages_forward (Messages): List for mobile-terminated
            messages_return (Messages): List for mobile-originated
        
        """
        if not isinstance(name, str) or name == '':
            raise ValueError(f'Invalid service name {name}')
        if sin not in range(16, 256):
            if not(sin == 0 and kwargs.get('override_sin', True)):
                raise ValueError('Invalid SIN must be 16..255')
        description = kwargs.get('description', None)
        if description is not None:
            warn('Service Description not currently supported')
        super().__init__(name, description)
        self._sin = sin
        for kwarg in ['messages_forward', 'messages_return']:
            attr = f'_{kwarg}'
            is_forward = 'forward' in kwarg
            messages = kwargs.get(kwarg, None)
            if messages and isinstance(messages, Messages):
                setattr(self, attr, messages)
            else:
                setattr(self, attr, Messages(self.sin, is_forward))
    
    @property
    def sin(self) -> int:
        return self._sin
    
    @property
    def messages_forward(self) -> 'list[MessageCodec]':
        return self._messages_forward
    
    @messages_forward.setter
    def messages_forward(self, messages: Messages):
        if not isinstance(messages, Messages):
            raise ValueError('Invalid messages list')
        for message in messages:
            assert isinstance(message, MessageCodec)
            if not message.is_forward:
                raise ValueError(f'Message {message.name} is_forward is False')
        self._messages_forward = messages

    @property
    def messages_return(self) -> 'list[MessageCodec]':
        return self._messages_return
    
    @messages_return.setter
    def messages_return(self, messages: Messages):
        if not isinstance(messages, Messages):
            raise ValueError('Invalid messages list')
        for message in messages:
            assert isinstance(message, MessageCodec)
            if message.is_forward:
                raise ValueError(f'Message {message.name} is_forward is True')
        self._messages_return = messages
        
    def xml(self) -> ET.Element:
        """Returns the Service XML definition for a Message Definition File."""
        if len(self.messages_forward) == 0 and len(self.messages_return) == 0:
            raise ValueError(f'No messages defined for service {self.sin}')
        xservice = ET.Element('Service')
        name = ET.SubElement(xservice, 'Name')
        name.text = str(self.name)
        sin = ET.SubElement(xservice, 'SIN')
        sin.text = str(self.sin)
        if self.description:
            desc = ET.SubElement(xservice, 'Description')
            desc.text = str(self.description)
        if len(self.messages_forward) > 0:
            forward_messages = ET.SubElement(xservice, 'ForwardMessages')
            for m in self.messages_forward:
                forward_messages.append(m.xml())
        if len(self.messages_return) > 0:
            return_messages = ET.SubElement(xservice, 'ReturnMessages')
            for m in self.messages_return:
                return_messages.append(m.xml())
        return xservice
    
    def json(self) -> dict:
        """Returns the service JSON definition."""
        svc = { 'name': self.name, 'codecServiceId': self.sin }
        optional_tags = ['description']
        for tag in optional_tags:
            if hasattr(self, tag) and getattr(self, tag):
                svc[tag] = getattr(self, tag)
        for messages in [self.messages_forward, self.messages_return]:
            if len(messages) > 0:
                json_messages = [m.json() for m in messages]
                tag = 'mobileTerminatedMessages'
                if messages == self.messages_return:
                    tag = tag.replace('Terminated', 'Originated')
                svc[tag] = json_messages
        return svc


class Services(CodecList):
    """The list of Service(s) within a MessageDefinitions."""
    def __init__(self, services: 'list[ServiceCodec]' = None):
        super().__init__(codec_cls=ServiceCodec)
        if services is not None:
            for service in services:
                if not isinstance(service, ServiceCodec):
                    raise ValueError(f'Invalid Service {service}')
                self.add(service)
    
    def add(self, service: ServiceCodec) -> None:
        """Adds a Service to the list of Services."""
        if not isinstance(service, ServiceCodec):
            raise ValueError(f'{service} is not a valid Service')
        if service.name in self:
            raise ValueError(f'Duplicate Service {service.name}')
        for existing_service in self:
            if existing_service.sin == service.sin:
                raise ValueError(f'Duplicate SIN {service.sin}')
        self.append(service)
