from warnings import warn

from .. import ET
from .base_field import FieldCodec
from .helpers import decode_field_length, encode_field_length


class StringField(FieldCodec):
    """A character string sent over-the-air."""
    def __init__(self, name: str, size: int, **kwargs):
        """Instantiates a StringField.
        
        Args:
            name (str): The field name must be unique within a Message.
            size (int): The maximum number of characters in the string.
        
        Keyword Args:
            description (str): An optional description/purpose for the string.
            optional (bool): Indicates if the string is optional in the Message.
            fixed (bool): Indicates if the string is always fixed length `size`.
            default (str): A default value for the string.
            value (str): Optional value to set during initialization.

        """
        if not isinstance(size, int) or size < 1:
            raise ValueError('Invalid string size')
        super().__init__(name=name,
                         data_type='string',
                         description=kwargs.get('description', None),
                         optional=kwargs.get('optional', None))
        self._size = size
        self._fixed = None
        self._default = None
        self._value = None
        supported_kwargs = ['fixed', 'default', 'value']
        for k, v in kwargs.items():
            if k in supported_kwargs and hasattr(self, k):
                setattr(self, k, v)
    
    def _validate_string(self, s: str) -> str:
        if s is not None:
            if not isinstance(s, str):
                raise ValueError(f'Invalid string {s}')
            if len(s) > self.size:
                warn(f'Clipping string at max {self.size} characters')
                return s[:self.size]
        return s
                
    @property
    def size(self) -> int:
        """The maximum size of the string in characters."""
        return self._size
    
    @size.setter
    def size(self, value: int):
        if not isinstance(value, int) or value < 1:
            raise ValueError('Size must be integer greater than 0 characters')
        self._size = value
    
    @property
    def default(self) -> str:
        """The default value."""
        return self._default
    
    @default.setter
    def default(self, v: str):
        self._default = self._validate_string(v)

    @property
    def value(self) -> str:
        return self._value
    
    @value.setter
    def value(self, v: str):
        self._value = self._validate_string(v)

    @property
    def fixed(self) -> bool:
        """Indicates whether the string length is fixed (padded/truncated)."""
        return self._fixed
    
    @fixed.setter
    def fixed(self, value: bool):
        if value is not None and not isinstance(value, bool):
            raise ValueError('Invalid fixed value must be boolean or None')
        self._fixed = value

    @property
    def bits(self) -> int:
        """The size of the field in bits."""
        if self._value is None:
            bits = 0
        elif self.fixed:
            bits = self.size * 8
        else:
            L = 8 if len(self._value) < 128 else 16
            bits = L + len(self._value) * 8
        return bits + (1 if self.optional else 0)
    
    def encode(self) -> str:
        """Returns the binary string of the field value."""
        if self.value is None and not self.optional:
            raise ValueError(f'No value defined for StringField {self.name}')
        binstr = ''.join(format(ord(c), '08b') for c in self.value)
        if self.fixed:
            binstr += ''.join('0' for bit in range(len(binstr), self.bits))
        else:
            binstr = encode_field_length(len(self.value)) + binstr
        return binstr

    def decode(self, binary_str: str) -> int:
        """Populates the field value from binary and returns the next offset.
        
        Args:
            binary_str (str): The binary string to decode
        
        Returns:
            The bit offset after parsing
        """
        if self.fixed:
            length = self.size
            bit_index = 0
        else:
            (length, bit_index) = decode_field_length(binary_str)
        n = int(binary_str[bit_index:bit_index + length * 8], 2)
        char_bytes = n.to_bytes((n.bit_length() + 7) // 8, 'big')
        for i, byte in enumerate(char_bytes):
            if byte == 0:
                warn('Truncating after 0 byte in string')
                char_bytes = char_bytes[:i]
                break
        self.value = char_bytes.decode('utf-8', 'surrogatepass') or '\0'
        return bit_index + length * 8

    def xml(self) -> ET.Element:
        """The StringField XML definition."""
        return super().xml(['Size', 'Fixed', 'Default'])
    
    def json(self) -> dict:
        """The StringField JSON definition."""
        return super().json(['size', 'fixed', 'default'])
