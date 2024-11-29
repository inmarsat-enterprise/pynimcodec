from .. import ET
from .base_field import FieldCodec
from .helpers import optimal_bits


class EnumField(FieldCodec):
    """An enumerated field sends an index over-the-air representing a string."""
    def __init__(self, name: str, items: 'list[str]', size: int, **kwargs):
        """Instantiates a EnumField.
        
        Args:
            name (str): The field name must be unique within a Message.
            items (list): A list of strings (indexed from 0).
            size (int): The number of *bits* used to encode over-the-air.
        
        Keyword Args:
            description (str): An optional description/purpose for the field.
            optional (bool): Indicates if the field is optional in the Message.
            default (str): A default value for the enum.
            value (str): Optional value to set during initialization.

        Raises:
            ValueError if items is not a valid list of strings or if the size
                specified is insufficient for the number of items.
            
        """
        if (not isinstance(items, list) or not items or
            not all(isinstance(item, str) for item in items)):
            raise ValueError('Items must a non-empty list of strings')
        min_size = 1 if len(items) <= 1 else optimal_bits((0, len(items) - 1))
        if not isinstance(size, int) or size < min_size:
            raise ValueError(f'Size must be integer greater than {min_size}')
        super().__init__(name=name,
                         data_type='enum',
                         description=kwargs.get('description', None),
                         optional=kwargs.get('optional', None))
        self._items = items
        self._size = size
        self._default = None
        self._value = None
        supported_kwargs = ['default', 'value']
        for k, v in kwargs.items():
            if k in supported_kwargs and hasattr(self, k):
                setattr(self, k, v)
    
    def _validate_enum(self, v: 'int|str') -> 'int|None':
        if v is not None:
            if isinstance(v, str):
                if v not in self.items:
                    raise ValueError(f'Invalid value {v} not in items')
                for index, item in enumerate(self.items):
                    if item == v:
                        return index
            elif isinstance(v, int):
                if v < 0 or v >= len(self.items):
                    raise ValueError(f'Invalid enum index {v}')
            else:
                raise ValueError(f'Invalid value {v}')
        return v

    @property
    def items(self):
        return self._items
    
    @items.setter
    def items(self, items: list):
        if (not isinstance(items, list) or
            not all(isinstance(x, str) for x in items)):
            raise ValueError('Items must be a list of strings')
        self._items = items

    @property
    def default(self) -> str:
        if self._default is None:
            return None
        return self.items[self._default]
    
    @default.setter
    def default(self, v: 'int|str'):
        self._default = self._validate_enum(v)

    @property
    def value(self) -> str:
        if self._value is None:
            if self.default is not None:
                return self.default
            return None
        return self.items[self._value]
    
    @value.setter
    def value(self, v: 'int|str'):
        self._value = self._validate_enum(v)

    @property
    def size(self) -> int:
        """The size of the field in bits."""
        return self._size
    
    @size.setter
    def size(self, v: int):
        if not isinstance(v, int) or v < 1:
            raise ValueError('Size must be integer greater than zero')
        minimum_bits = optimal_bits((0, len(self.items)))
        if v < minimum_bits:
            raise ValueError(f'Size must be at least {minimum_bits}'
                             ' to support item count')
        self._size = v

    @property
    def bits(self) -> int:
        """The size of the field in bits."""
        bits = self.size if self._value is not None else 0
        return bits + (1 if self.optional else 0)
    
    def encode(self) -> str:
        """Returns the binary string of the field value."""
        if self.value is None:
            raise ValueError(f'No value configured in EnumField {self.name}')
        _format = f'0{self.size}b'
        binstr = format(self.items.index(self.value), _format)
        return binstr

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
        """The EnumField XML definition."""
        # Size must come after Items for Inmarsat V1 parser
        xmlfield = super().xml()
        items = ET.SubElement(xmlfield, 'Items')
        for string in self.items:
            item = ET.SubElement(items, 'string')
            item.text = str(string)
        return super()._xml_flex_tags(['Size', 'Default'], xmlfield)
    
    def json(self) -> dict:
        """The EnumField JSON definition."""
        field = super().json(['size', 'default'])
        field['items'] = [str(i) for i in self.items]
        return field      
