from .. import ET
from .base_field import FieldCodec


class BooleanField(FieldCodec):
    """A Boolean field."""
    def __init__(self, name: str, **kwargs):
        """Instantiates a BooleanField.
        
        Args:
            name: The field name must be unique within a Message.
            description: An optional description/purpose for the field.
            optional: Indicates if the field is optional in the Message.
            default: A default value for the boolean.
            value: Optional value to set during initialization.

        """
        super().__init__(name=name,
                         data_type='bool',
                         description=kwargs.pop('description', None),
                         optional=kwargs.pop('optional', None))
        self._default = None
        self._value = None
        supported_kwargs = ['default', 'value']
        for k, v in kwargs.items():
            if k in supported_kwargs and hasattr(self, k):
                setattr(self, k, v)
    
    @property
    def default(self):
        return self._default

    @default.setter
    def default(self, v: bool):
        if v is not None and not isinstance(v, bool):
            raise ValueError(f'Invalid boolean value {v}')
        self._default = v

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, v: bool):
        if v is not None and not isinstance(v, bool):
            raise ValueError(f'Invalid boolean value {v}')
        self._value = v

    @property
    def bits(self):
        bits = 0 if self._value is None else 1
        return bits + (1 if self.optional else 0)
    
    def encode(self) -> str:
        """Returns the binary string of the field value."""
        if self.value is None and self.default is not None:
            return '1' if self.default else '0'
        elif self.value is None and not self.optional:
            raise ValueError('No value assigned to field')
        return '1' if self.value else '0'

    def decode(self, binary_str: str) -> int:
        """Populates the field value from binary and returns the next offset.
        
        Args:
            binary_str (str): The binary string to decode
        
        Returns:
            The bit offset after parsing
        """
        self.value = True if binary_str[0] == '1' else False
        return 1

    def xml(self) -> ET.Element:
        """The BooleanField XML definition."""
        return super().xml(['Default'])
    
    def json(self) -> dict:
        """The BooleanField JSON definition."""
        return super().json(['default'])
