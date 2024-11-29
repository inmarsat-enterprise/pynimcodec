from copy import deepcopy

from .. import ET
from .base_field import FieldCodec, Fields
from .helpers import optimal_bits


class BitmaskListField(FieldCodec):
    """A bit-indexed field of arrays.
    
    Attributes:
        name (str): The name of the field instance.
        size (int): The maximum number of elements allowed.
        fields (Fields): A list of Field types comprising each ArrayElement
        description (str): An optional description of the array/use.
        optional (bool): Indicates if the array is optional in the Message
        value (int): The value of the bitmask
        elements (list): The enumerated list of ArrayElements

    """
    def __init__(self, name: str, items: 'list[str]', size: int, fields: Fields, **kwargs):
        """Initializes an ArrayField instance.
        
        Args:
            name (str): The unique field name within the Message.
            items (list): List of strings indexed from bit 0
            size (int): The maximum number of bits (array rows)
            fields (list): The FieldCodec (columns) comprising each element.
        
        Keyword Args:
            description (str): An optional description/purpose of the array.
            optional (bool): Indicates if the array is optional in the Message.
            fixed (bool): Indicates if the array is always the fixed `size`.
            value (int): The value of the bitmask
            elements (list): Optional elements to populate during instantiation.

        Raises:
            ValueError if fields or array size is invalid.
            
        """
        if (not isinstance(items, list) or not items or
            not all(isinstance(item, str) for item in items)):
            raise ValueError('Items must a non-empty list of strings')
        min_size = max(1, optimal_bits((0, len(items) - 1)))
        if not isinstance(size, int) or size < min_size:
            raise ValueError(f'Size must be integer greater than {min_size}')
        if (not isinstance(fields, Fields) or
            not (isinstance(fields, list) and
                 all(isinstance(x, FieldCodec) for x in fields))):
            raise ValueError('Invalid fields')
        super().__init__(name=name,
                         data_type='array',
                         description=kwargs.pop('description', None),
                         optional=kwargs.pop('optional', None))
        self._items = items
        self._size = size
        self._fields = None
        self.fields = fields or Fields()
        self._value = 0
        self._elements = []
        if 'elements' in kwargs:
            self.elements = kwargs.pop('elements')
    
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
    def value(self) -> int:
        return self._value
    
    @value.setter
    def value(self, value: int):
        max_value = self.size**2 - 1
        if not isinstance(value, int) or value < 0 or value > max_value:
            raise ValueError('Invalid bitmask value')
        self._value = value
    
    @property
    def size(self) -> int:
        """The maximum number of array elements."""
        return self._size
    
    @size.setter
    def size(self, size: int):
        min_size = max(1, optimal_bits((0, len(self.items) - 1)))
        if not isinstance(size, int) or size < min_size:
            raise ValueError('Invalid size for length of items')
        self._size = size
    
    @property
    def fields(self) -> 'list[FieldCodec]':
        """The set of `FieldCodec` that make up each array element."""
        return self._fields

    @fields.setter
    def fields(self, fields: Fields):
        if (not isinstance(fields, Fields) or
            not (isinstance(fields, list) and
                 all(isinstance(x, FieldCodec) for x in fields))):
            raise ValueError('Invalid Fields definition for ArrayField')
        self._fields = fields

    @property
    def elements(self) -> 'list[Fields]':
        """The list of elements (field sets) in the array."""
        return self._elements
    
    @elements.setter
    def elements(self, elements: 'list[Fields]'):
        if (not isinstance(elements, list) or 
            not all(isinstance(item, Fields) for item in elements)):
            raise ValueError('Elements must be a list of grouped Fields')
        for fields in elements:
            # assert isinstance(fields, Fields)
            for index, field in enumerate(fields):
                assert isinstance(field, FieldCodec)
                if (field.name != self.fields[index].name):
                    raise ValueError(f'fields[{index}].name'
                                     f' expected {self.fields[index].name}'
                                     f' got {field.name}')
                if (field.data_type != self.fields[index].data_type):
                    raise ValueError(f'fields[{index}].data_type'
                                     f' expected {self.fields[index].data_type}'
                                     f' got {field.data_type}')
                #TODO: validate non-optional fields have value/elements
                if (field.value is None):
                    raise ValueError(f'fields[{index}].value missing')
                try:
                    self._elements[index] = fields
                except IndexError:
                    self._elements.append(fields)

    @property
    def bits(self) -> int:
        """The size of the bitmasklist in bits."""
        bits = 0
        for field in self.fields:
            assert isinstance(field, FieldCodec)
            bits += field.bits
        bits *= len(self.elements)
        return bits + self.size + (1 if self.optional else 0)
    
    def _valid_element(self, element: Fields) -> bool:
        for i, field in enumerate(self.fields):
            assert isinstance(field, FieldCodec)
            e_field = element[i]
            assert isinstance(e_field, FieldCodec)
            if e_field.name != field.name:
                raise ValueError(f'element field name {e_field.name}'
                                 f' does not match {field.name}')
            if e_field.data_type != field.data_type:
                raise ValueError(f'element field data_type {e_field.data_type}'
                                 f' does not match {field.data_type}')
            if e_field.optional != field.optional:
                raise ValueError(f'element optional {e_field.optional}'
                                 f' does not match {field.optional}')
            if (hasattr(field, 'fixed') and
                hasattr(e_field, 'fixed') and
                e_field.fixed != field.fixed):
                raise ValueError(f'element fixed {e_field.fixed}'
                                 f' does not match {field.fixed}')
            if (hasattr(field, 'size') and
                hasattr(e_field, 'size') and
                e_field.size != field.size):
                raise ValueError(f'element size {e_field.size}'
                                 f' does not match {field.size}')
        return True

    def append(self, element: Fields):
        """Adds the array element to the list of elements."""
        if not isinstance(element, Fields):
            raise ValueError('Invalid element definition must be Fields')
        if not self._valid_element(element):
            raise ValueError('Invalid element definition'
                             f' - requires {self.fields}')
        for i, field in enumerate(element):
            assert isinstance(field, FieldCodec)
            if (hasattr(field, 'description') and
                field.description != self.fields[i].description):
                element[i].description = self.fields[i].description
            if hasattr(field, 'value') and field.value is None:
                element[i].value = self.fields[i].default
        self._elements.append(element)

    def new_element(self) -> Fields:
        """Returns an empty element at the end of the elements list."""
        new_index = len(self._elements)
        new_fields = deepcopy(self.fields)
        self.append(Fields(new_fields))
        return self.elements[new_index]

    def encode(self) -> str:
        """Returns the binary string of the field value."""
        bfmt = f'0{self.size}b'
        binstr = f'{self.value:{bfmt}}'
        for element in self.elements:
            for field in element:
                binstr += field.encode()
        return binstr

    def decode(self, binary_str: str) -> int:
        """Populates the field value from binary and returns the next offset.
        
        Args:
            binary_str (str): The binary string to decode
        
        Returns:
            The bit offset after parsing
        """
        self._value = int(binary_str[0:self.size], 2)
        bit_index = self.size
        element_count = bin(self.value).count('1')
        for index in range(0, element_count):
            fields = Fields(self.fields)
            for field in fields:
                bit_index += field.decode(binary_str[bit_index:])
            try:
                self._elements[index] = fields
            except IndexError:
                self._elements.append(fields)
        return bit_index

    def xml(self) -> ET.Element:
        """Returns the Array XML definition for a Message Definition File."""
        # Size must come after Fields for Inmarsat V1 parser
        xmlfield = super().xml()
        items = ET.SubElement(xmlfield, 'Items')
        for string in self.items:
            item = ET.SubElement(items, 'string')
            item.text = str(string)
        fields = ET.SubElement(xmlfield, 'Fields')
        for field in self.fields:
            fields.append(field.xml())
        return xmlfield
    
    def json(self) -> dict:
        """Get the array field JSON definition."""
        field = super().json()
        field['items'] = [str(i) for i in self.items]
        field['fields'] = [f.json() for f in self.fields]
        return field
