from warnings import warn

from .. import ET, DATA_TYPES
from .base_field import FieldCodec


class UnsignedIntField(FieldCodec):
    """An unsigned integer value using a defined number of bits over-the-air."""
    # SUPPORTED_UINT_TYPES = ['uint_8', 'uint_16', 'uint_32']
    def __init__(self, name: str, size: int, **kwargs):
        """Instantiates a UnsignedIntField.
        
        Args:
            name (str): The field name must be unique within a Message.
            size (int): The number of *bits* used to encode over-the-air
                (maximum 32).
        
        Keyword Args:
            description (str): An optional description/purpose for the string.
            optional (bool): Indicates if the string is optional in the Message.
            default (int): A default value for the string.
            value (int): Optional value to set during initialization.
            data_type (str): The integer type represented (default uint_32).

        """
        data_type = kwargs.pop('data_type', 'uint_32')
        # if data_type is None or data_type not in self.SUPPORTED_UINT_TYPES:
        if not UnsignedIntField._is_valid_type(data_type):
            raise ValueError(f'Invalid unsignedint type {data_type}')
        if not isinstance(size, int) or size < 1:
            raise ValueError('Size must be int greater than zero')
        super().__init__(name=name,
                         data_type=data_type,
                         description=kwargs.pop('description', None),
                         optional=kwargs.pop('optional', None))
        self._size = size
        self._default = None
        self._value = None
        supported_kwargs = ['default', 'value']
        for k, v in kwargs.items():
            if k in supported_kwargs and hasattr(self, k):
                setattr(self, k, v)
    
    @property
    def size(self):
        """The size of the field in bits."""
        return self._size

    @size.setter
    def size(self, value: int):
        if not isinstance(value, int) or value < 1:
            raise ValueError('Size must be integer greater than 0 bits')
        data_type_size = int(self.data_type.split('_')[1])
        if value > data_type_size:
            warn(f'Size {value} larger than required by {self.data_type}')
        self._size = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, v: int):
        clip = False
        if v is not None:
            if not isinstance(v, int) or v < 0:
                raise ValueError('Unsignedint must be non-negative integer')
            if v > 2**self.size - 1:
                self._value = 2**self.size - 1
                warn(f'Clipping unsignedint at max value {self._value}')
                clip = True
        if not clip:
            self._value = v
    
    @property
    def default(self):
        """The default value."""
        return self._default
    
    @default.setter
    def default(self, v: int):
        if v is not None:
            if v > 2**self.size - 1 or v < 0:
                raise ValueError(F'Invalid unsignedint default {v}')
        self._default = v
    
    @property
    def bits(self):
        """The size of the field in bits."""
        bits = self.size if self._value is not None else 0
        return bits + (1 if self.optional else 0)
    
    def encode(self) -> str:
        """Returns the binary string of the field value."""
        if self.value is None:
            raise ValueError(f'No value defined in UnsignedIntField {self.name}')
        _format = f'0{self.size}b'
        return format(self.value, _format)

    def decode(self, binary_str: str) -> int:
        """Populates the field value from binary and returns the next offset.
        
        Args:
            binary_str (str): The binary string to decode
        
        Returns:
            The bit offset after parsing
        """
        self.value = int(binary_str[:self.size], 2)
        return self.size

    def xml(self) -> ET.Element:
        """The UnsignedIntField XML definition."""
        return super().xml(['Size', 'Default'])
    
    def json(self) -> dict:
        """The UnsignedIntField JSON definition."""
        return super().json(['size', 'default'])


class SignedIntField(FieldCodec):
    """A signed integer value using a defined number of bits over-the-air."""
    # SUPPORTED_INT_TYPES = ['int_8', 'int_16', 'int_32']
    def __init__(self, name: str, size: int, **kwargs):
        """Instantiates a SignedIntField.
        
        Args:
            name: The field name must be unique within a Message.
            size: The number of *bits* used to encode the integer over-the-air
                (maximum 32).
            data_type: The integer type represented (for decoding).
            description: An optional description/purpose for the string.
            optional: Indicates if the string is optional in the Message.
            default: A default value for the string.
            value: Optional value to set during initialization.

        """
        data_type = kwargs.pop('data_type', 'int_32')
        # if data_type is None or data_type not in self.SUPPORTED_INT_TYPES:
        if not SignedIntField._is_valid_type(data_type):
            raise ValueError(f'Invalid unsignedint type {data_type}')
        if not isinstance(size, int) or size < 1:
            raise ValueError('Size must be int greater than zero')
        super().__init__(name=name,
                         data_type=data_type,
                         description=kwargs.pop('description', None),
                         optional=kwargs.pop('optional', None))
        self._size = size
        self._default = None
        self._value = None
        supported_kwargs = ['default', 'value']
        for k, v in kwargs.items():
            if k in supported_kwargs and hasattr(self, k):
                setattr(self, k, v)
    
    @property
    def size(self):
        """The size of the field in bits."""
        return self._size

    @size.setter
    def size(self, value: int):
        if not isinstance(value, int) or value < 1:
            raise ValueError('Size must be integer greater than 0 bits')
        self._size = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, v: int):
        clip = False
        if v is not None:
            if not isinstance(v, int):
                raise ValueError('Unsignedint must be non-negative integer')
            if v > (2**self.size / 2) - 1:
                self._value = int(2**self.size / 2) - 1
                warn(f'Clipping signedint at max value {self._value}')
                clip = True
            if v < -(2**self.size / 2):
                self._value = -1 * int(2**self.size / 2)
                warn(f'Clipping signedint at min value {self._value}')
                clip = True
        if not clip:
            self._value = v
    
    @property
    def default(self):
        """The default value."""
        return self._default
    
    @default.setter
    def default(self, v: int):
        if v is not None:
            if not isinstance(v, int):
                raise ValueError(f'Invalid signed integer {v}')
            if v > (2**self.size / 2) - 1 or v < -(2**self.size / 2):
                raise ValueError(f'Invalid default {v}')
        self._default = v
    
    @property
    def bits(self):
        """The size of the field in bits."""
        bits = self.size if self._value is not None else 0
        return bits + (1 if self.optional else 0)
    
    def encode(self) -> str:
        """Returns the binary string of the field value."""
        if self.value is None:
            raise ValueError(f'No value defined in UnsignedIntField {self.name}')
        _format = f'0{self.size}b'
        if self.value < 0:
            invertedbin = format(self.value * -1, _format)
            twocomplementbin = ''
            i = 0
            while len(twocomplementbin) < len(invertedbin):
                twocomplementbin += '1' if invertedbin[i] == '0' else '0'
                i += 1
            binstr = format(int(twocomplementbin, 2) + 1, _format)
        else:
            binstr = format(self.value, _format)
        return binstr

    def decode(self, binary_str: str) -> int:
        """Populates the field value from binary and returns the next offset.
        
        Args:
            binary_str (str): The binary string to decode
        
        Returns:
            The bit offset after parsing
        """
        value = int(binary_str[:self.size], 2)
        if (value & (1 << (self.size - 1))) != 0:   #:sign bit set e.g. 8bit: 128-255
            value = value - (1 << self.size)        #:compute negative value
        self.value = value
        return self.size

    def xml(self) -> ET.Element:
        """The SignedIntField XML definition."""
        return super().xml(['Size', 'Default'])
    
    def json(self) -> dict:
        """The SignedIntField JSON definition."""
        return super().json(['size', 'default'])
