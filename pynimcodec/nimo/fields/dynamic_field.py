from warnings import warn

from .. import ET
from .base_field import FieldCodec
from .helpers import decode_field_length, encode_field_length
from enum import IntEnum

class DynamicType(IntEnum):
    ENUM = 0
    BOOLEAN = 1
    VARUINT = 2
    VARINT = 3
    VARSTR = 4
    VARDATA = 5

class VariableSize(IntEnum):
    """In MDF, 2 bits are used to encode variable Unsigned or Signed Int size"""
    EIGHT = 0
    SIXTEEN = 1
    THIRTYTWO = 2
    RESERVED = 3
    
    def to_size(self) -> int:
        """Convert enum value to its actual size in bits."""
        mapping = {
            VariableSize.EIGHT: 8,
            VariableSize.SIXTEEN: 16,
            VariableSize.THIRTYTWO: 32,
            VariableSize.RESERVED: None
        }
        return mapping[self]

class DynamicField(FieldCodec):
    """A dynamic field sent over-the-air."""
    def __init__(self, name: str, **kwargs):
        """Instantiates a DynamicField.
        
        Args:
            name (str): The field name must be unique within a Message.
        
        Keyword Args:
            description (str): An optional description/purpose for the string.
            optional (bool): Indicates if the string is optional in the Message.
            value (str): Optional value to set during initialization.

        """
        super().__init__(name=name,
                         data_type='dynamic',
                         description=kwargs.get('description', None),
                         optional=kwargs.get('optional', None))
        self._value = None
        self._type = None
        supported_kwargs = ['value']
        for k, v in kwargs.items():
            if k in supported_kwargs and hasattr(self, k):
                setattr(self, k, v)
    
    def _validate(self, s):
        #TODO
        if s is None:
            raise ValueError(f'Invalid value {s}')
        return s

    def _validate_type(self, t: int) -> DynamicType:
        if t not in DynamicType._value2member_map_:
            raise ValueError(f'Invalid DynamicType {t}')
        return t

    @property
    def value(self):
        return self._value
    
    @value.setter
    def value(self, v):
        self._value = self._validate(v)
        
    @property
    def type(self):
        return self._type
    
    @type.setter
    def type(self, v):
        self._type = self._validate_type(v)

    @property
    def bits(self) -> int:
        """The size of the field in bits."""
        if self._value is None:
            bits = 0
        else:
            # L = 8 if len(self._value) < 128 else 16
            # bits = L + len(self._value) * 8
            if self._type == DynamicType.ENUM:
                bits = 0
            else:
                raise ValueError(f'Unknown DynamicField Type: {self._type}')
            
        return bits + (1 if self.optional else 0) + 3
    
    def encode(self) -> str:
        """Returns the binary string of the field value."""
        if self.value is None and not self.optional:
            raise ValueError(f'No value defined for DynamicField {self.name}')
        binstr = ''.join(format(ord(c), '08b') for c in self.value)
        binstr = encode_field_length(len(self.value)) + binstr
        return binstr

    def decode(self, binary_str: str) -> int:
        """Populates the field value from binary and returns the next offset.
        
        Args:
            binary_str (str): The binary string to decode
        
        Returns:
            The bit offset after parsing
        """
        dType = DynamicType(int(binary_str[:3],2))
        
        # if(dType == DynamicType.ENUM):
            
        # elif (dType == DynamicType.BOOLEAN):
            
        # else:
        #     raise ValueError(f'Unknown DynamicField Type: {self._type}')
        
        (length, bit_index) = decode_field_length(binary_str[3:])
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
        """The DynamicField XML definition."""
        return super().xml()
    
    def json(self) -> dict:
        """The DynamicField JSON definition."""
        return super().json()
