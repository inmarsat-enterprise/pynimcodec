"""Constants used for Compact Binary Codec."""

from enum import Enum, EnumMeta
from typing import Any


class CbcEnumMeta(EnumMeta):
    """EnumMeta that allows membership testing with values."""
    def __contains__(cls, item: Any) -> bool:
        try:
            cls(item)
            return True
        except ValueError:
            return False


class CbcEnum(Enum, metaclass=CbcEnumMeta):
    """Base Enum class for Compact Binary Codec. Only for subclassing."""


class FieldType(CbcEnum):
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


class MessageDirection(CbcEnum):
    """Direction type mappings for Compact Binary Codec."""
    MO = 'UPLINK'     # Mobile-Originated
    MT = 'DOWNLINK'   # Mobile-Terminated
