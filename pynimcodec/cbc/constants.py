"""Constants used for Compact Binary Codec."""

from enum import Enum, EnumMeta


class _MetaEnum(EnumMeta):
    """Enum that provides a contains (`in`) method for its subclasses."""
    def __contains__(cls, item) -> bool:
        try:
            cls(item)
        except ValueError:
            return False
        return True


class _CbcEnum(Enum, metaclass=_MetaEnum):
    """Base Enum class of `MetaEnum` intended exclusively for subclassing."""


class FieldType(_CbcEnum):
    """Field type mappings for Compact Binary Codec."""
    BOOL = 'bool'
    INT = 'int'
    UINT = 'uint'
    FLOAT = 'float'
    ENUM = 'enum'
    BITMASK = 'bitmask'
    STRING = 'string'
    DATA = 'data'
    ARRAY = 'array'
    STRUCT = 'struct'
    BITMASKARRAY = 'bitmaskarray'


class MessageDirection(_CbcEnum):
    """Direction type mappings for Compact Binary Codec."""
    MO = 'UPLINK'   # Mobile-Originated
    MT = 'DOWNLINK'   # Mobile-Terminated
