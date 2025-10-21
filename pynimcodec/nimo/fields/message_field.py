from warnings import warn

from .. import ET
from .base_field import FieldCodec
from .helpers import decode_field_length, encode_field_length


class MessageField(FieldCodec):
    """A character string sent over-the-air."""
    def __init__(self, name: str, **kwargs):
        """Instantiates a MessageField.
        
        Args:
            name (str): The field name must be unique within a Message.
        
        Keyword Args:
            description (str): An optional description/purpose for the string.
            optional (bool): Indicates if the string is optional in the Message.
            value (str): Optional value to set during initialization.

        """
        super().__init__(name=name,
                         data_type='msg',
                         description=kwargs.get('description', None),
                         optional=kwargs.get('optional', None))
        self._value = None
        supported_kwargs = ['value']
        for k, v in kwargs.items():
            if k in supported_kwargs and hasattr(self, k):
                setattr(self, k, v)
    
    def _validate_message(self, s: str) -> str:
        #TODO
        if s is not None:
            if not isinstance(s, str):
                raise ValueError(f'Invalid string {s}')
        return s

    @property
    def value(self) -> str:
        return self._value
    
    @value.setter
    def value(self, v: str):
        self._value = self._validate_message(v)

    @property
    def bits(self) -> int:
        """The size of the field in bits."""
        if self._value is None:
            bits = 0
        else:
            L = 8 if len(self._value) < 128 else 16
            bits = L + len(self._value) * 8
        return bits + (1 if self.optional else 0)
    
    def encode(self) -> str:
        #TODO
        """Returns the binary string of the field value."""
        # if self.value is None and not self.optional:
        #     raise ValueError(f'No value defined for MessageField {self.name}')
        # binstr = ''.join(format(ord(c), '08b') for c in self.value)
        # binstr = encode_field_length(len(self.value)) + binstr
        # return binstr
        return None

    def decode(self, binary_str: str) -> int:
        #TODO
        """Populates the field value from binary and returns the next offset.
        
        Args:
            binary_str (str): The binary string to decode
        
        Returns:
            The bit offset after parsing
        """

        # (length, bit_index) = decode_field_length(binary_str)
        # n = int(binary_str[bit_index:bit_index + length * 8], 2)
        # char_bytes = n.to_bytes((n.bit_length() + 7) // 8, 'big')
        # for i, byte in enumerate(char_bytes):
        #     if byte == 0:
        #         warn('Truncating after 0 byte in string')
        #         char_bytes = char_bytes[:i]
        #         break
        # self.value = char_bytes.decode('utf-8', 'surrogatepass') or '\0'
        # return bit_index + length * 8
        return None

    def xml(self) -> ET.Element:
        """The MessageField XML definition."""
        return super().xml()
    
    def json(self) -> dict:
        """The MessageField JSON definition."""
        return super().json()
