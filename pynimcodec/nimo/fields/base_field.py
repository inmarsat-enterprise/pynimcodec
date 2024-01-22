from .. import DATA_TYPES, XML_NAMESPACE, ET, FIELD_TYPES_JSON
from ..base import BaseCodec, CodecList


class FieldCodec(BaseCodec):
    """The base class for a Field.
    
    Attributes:
        data_type (str): The data type from a supported list.
        name (str): The unique Field name.
        description (str): Optional description.
        optional (bool): Optional indication the field is optional.

    """
    def __init__(self, name: str, data_type: str, **kwargs):
        """Instantiates the base field.
        
        Args:
            name: The field name must be unique within a Message.
            data_type: The data type represented within the field.
        
        Keyword Args:
            description: (Optional) Description/purpose of the field.
            optional: (Optional) Indicates if the field is mandatory.
            
        """
        if data_type not in DATA_TYPES:
            raise ValueError(f'Invalid data type {data_type}')
        super().__init__(name, kwargs.get('description', None))
        self._data_type = data_type
        self._optional = None
        self.optional = kwargs.get('optional', None)
    
    @classmethod
    def _is_valid_type(cls, data_type: str) -> bool:
        """"""
        return data_type in DATA_TYPES and DATA_TYPES[data_type] == cls.__name__
    
    @property
    def data_type(self) -> str:
        return self._data_type

    @property
    def optional(self) -> bool:
        return self._optional
    
    @optional.setter
    def optional(self, value: bool):
        if value is not None and not isinstance(value, bool):
            raise ValueError('Invalid optional value must be bool or None')
        self._optional = value

    @property
    def bits(self) -> int:
        """Must be subclassed."""
        raise NotImplementedError('Subclass must define bits')

    def __repr__(self) -> str:
        rep = {}
        for name in dir(self):
            if name.startswith(('__', '_')):
                continue
            attr = getattr(self, name)
            if not callable(attr):
                rep[name] = attr
        return repr(rep)
    
    def _xml_flex_tags(self, tags: 'list[str]', xmlfield: ET.Element):
        """Adds XML tags to a field if present."""
        for tag in tags:
            attr = tag.lower()
            if hasattr(self, attr) and getattr(self, attr) is not None:
                sub = ET.SubElement(xmlfield, tag)
                sub.text = str(getattr(self, attr))
                if isinstance(getattr(self, attr), bool):
                    sub.text = sub.text.lower()
        return xmlfield
    
    def xml(self, tags: 'list[str]' = []) -> ET.Element:
        """The default XML template for a Field."""
        xsi_type = DATA_TYPES[self.data_type]
        attrib = { f'{{{XML_NAMESPACE["xsi"]}}}type': xsi_type}
        xmlfield = ET.Element('Field', attrib)
        common_tags = ['Name', 'Description', 'Optional']
        tags = common_tags + list(set(tags) - set(common_tags))
        return self._xml_flex_tags(tags, xmlfield)
    
    def _json_flex_tags(self, tags: 'list[str]', json_field: dict) -> dict:
        """Adds JSON tags to a field if present."""
        for tag in tags:
            tag = tag.lower()
            if hasattr(self, tag) and getattr(self, tag) is not None:
                json_field[tag] = getattr(self, tag)
        return json_field
    
    def json(self, tags: 'list[str]' = []) -> dict:
        """The default JSON template for a Field."""
        field_json = { 'type': FIELD_TYPES_JSON[self.__class__.__name__] }
        common_tags = ['name', 'description', 'optional']
        tags = common_tags + list(set(tags) - set(common_tags))
        return self._json_flex_tags(tags, field_json)
    
    def decode(self, *args, **kwargs):
        """Must be subclassed."""
        raise NotImplementedError('Subclass must define decode')
    
    def encode(self, *args, **kwargs):
        """Must be subclassed."""
        raise NotImplementedError('Subclass must define encode')


class Fields(CodecList):
    """The list of Fields defining a Message or ArrayElement."""
    def __init__(self, fields: 'list[FieldCodec]' = None) -> 'list[FieldCodec]':
        super().__init__(codec_cls=FieldCodec)
        if fields is not None:
            for field in fields:
                self.add(field)
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Fields):
            return NotImplemented
        if len(self) != len(other):
            return False
        for i, field in enumerate(self):
            if field != other[i]:
                return False
        return True
