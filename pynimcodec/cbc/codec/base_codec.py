"""Base classes for Compact Binary Codec."""

from typing import TypeVar

T = TypeVar('T')


class CbcCodec:
    """The base class for all CBC codecs."""
    
    required_args = ['name']
    
    def __init__(self, name: str, description: str = None) -> None:
        if not isinstance(name, str) or name.strip() == '':
            raise ValueError('Invalid name must be non-empty string')
        self._name = None
        self.name = name
        self._description = None
        self.description = description   # validates value
    
    @property
    def name(self) -> str:
        return self._name
    
    @name.setter
    def name(self, value: str):
        if not isinstance(value, str) or not value:
            raise ValueError('Invalid name must be non-empty string.')
        self._name = value
    
    @property
    def description(self) -> str:
        return self._description
    
    @description.setter
    def description(self, value: str):
        if value is not None and not isinstance(value, str) and not value:
            raise ValueError('Description must be non-empty string or None')
        self._description = value

    def _attribute_equivalence(self,
                               other: object,
                               exclude: "list[str]" = None) -> bool:
        """Indicates attribute equivalence, with optional exceptions."""
        if not isinstance(other, self.__class__):
            return NotImplemented
        for attr, val in self.__dict__.items():
            if exclude is not None and attr in exclude:
                continue
            if not hasattr(other, attr) or val != other.__dict__[attr]:
                return False
        return True
    
    def __eq__(self, other: object) -> bool:
        return self._attribute_equivalence(other)


class CodecList(list[T]):
    """Base class for a specific object type list.
    
    Used for Fields, Messages, Services.

    Attributes:
        codec_class (class): The object type the list is comprised of.

    """
    def __init__(self, codec_cls: T, *args) -> None:
        if not issubclass(codec_cls, CbcCodec):
            raise ValueError('Invalid codec class.')
        super().__init__(*args)
        self._codec_class = codec_cls

    @property
    def codec_class_name(self) -> str:
        return self._codec_class.__name__
    
    def append(self, codec: T) -> bool:
        """Append uniquely named codec to the end of the list.

        Args:
            obj (object): A valid object according to the codec_class
        
        Raises:
            ValueError: if codec is not the correct type or has a duplicate name
        """
        if not isinstance(codec, self._codec_class):
            raise ValueError(f'Invalid {self.codec_class_name} definition')
        for o in self:
            if getattr(o, 'name') == codec.name:
                raise ValueError(f'Duplicate {self.codec_class_name}'
                                 f' name {codec.name} found')
        super().append(codec)
        return True

    def __getitem__(self, n: 'str|int') -> T:
        """Retrieves an object by name or index.
        
        Args:
            n: The object name or list index
        
        Returns:
            object

        """
        if isinstance(n, str):
            for o in self:
                if getattr(o, 'name') == n:
                    return o
            raise ValueError(f'{self.codec_class_name} name {n} not found')
        return super().__getitem__(n)

    def __setitem__(self, n: 'str|int', value):
        if not isinstance(value, self._codec_class):
            raise ValueError(f'Invalid {self.codec_class_name}')
        if isinstance(n, str):
            for i, o in enumerate(self):
                if getattr(o, 'name') == n:
                    n = i
                    break
        else:
            super().__setitem__(n, value)

    def remove(self, name: str) -> bool:
        """Remove the codec from the list by name.
        
        Args:
            name: The name of the object.

        Returns:
            boolean: success
        """
        for o in self:
            if getattr(o, 'name') == name:
                super().remove(o)
                return True
        return False
