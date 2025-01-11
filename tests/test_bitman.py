import math

import pytest

from pynimcodec.bitman import BitArray, is_int, extract_from_buffer, append_bits_to_buffer, append_bytes_to_buffer


def test_is_int():
    """"""
    assert is_int(1) is True
    assert is_int(-1) is True
    assert is_int(2**64) is True
    assert is_int('1') is False
    assert is_int('1', True) is True
    assert is_int('one', True) is False


def test_extract_from_buffer():
    """"""
    test_buffer = bytes.fromhex('010203')
    assert extract_from_buffer(test_buffer, 0, 8) == test_buffer[0]
    assert extract_from_buffer(test_buffer, 8, 8, as_buffer=True) == test_buffer[1:2]
    assert extract_from_buffer(test_buffer, 7, 2) == int('10', 2)


def test_append_bits_to_buffer():
    """"""
    test_buffer = bytes.fromhex('01')
    extended = append_bits_to_buffer(BitArray(1), test_buffer, len(test_buffer) * 8)
    assert len(extended) == len(test_buffer) + 1
    assert extended[len(extended) - 1] == 0b10000000


def test_append_bytes_to_buffer():
    """"""
    test_buffer = bytes.fromhex('01')
    new_bytes = bytes.fromhex('01')
    extended = append_bytes_to_buffer(new_bytes, test_buffer, len(test_buffer) * 8)
    assert len(extended) == len(test_buffer) + len(new_bytes)
    with_offset = append_bytes_to_buffer(new_bytes, test_buffer, 1)
    assert len(with_offset) == len(test_buffer) + 1
    assert extract_from_buffer(with_offset, 1, 8) == int.from_bytes(new_bytes, 'big')


def test_bitarray_create():
    """"""
    bit_array = BitArray()
    assert isinstance(bit_array, BitArray)
    bit_array = BitArray(1,0,1)
    assert isinstance(bit_array, BitArray)
    with pytest.raises(ValueError):
        bit_array = BitArray(2)


def test_bitarray_append():
    """"""
    bit_array = BitArray()
    assert len(bit_array) == 0
    bit_array.append(1)
    assert len(bit_array) == 1
    with pytest.raises(ValueError):
        bit_array.append(2)


def test_bitarray_extend():
    """"""
    bit_array = BitArray()
    bit_array.extend([1,0,1])
    assert len(bit_array) == 3
    with pytest.raises(ValueError):
        bit_array.extend([2,3,4])


def test_bitarray_insert():
    """"""
    bit_array = BitArray(0,1)
    bit_array.insert(0,1)
    assert len(bit_array) == 3
    assert bit_array[0] == 1


def test_bitarray_setitem_getitem():
    """"""
    bit_array = BitArray(1,0)
    bit_array[1] = 1
    assert bit_array[1] == 1
    with pytest.raises(ValueError):
        bit_array[0] = 2


def test_bitarray_delitem():
    """"""
    bit_array = BitArray(1,1,1)
    del bit_array[0]
    assert len(bit_array) == 2


def test_bitarray_repr():
    """"""
    bit_array = BitArray(1,0,1)
    assert repr(bit_array) == 'BitArray([1, 0, 1])'


def test_bitarray_str():
    """"""
    bit_array = BitArray(1,0,1)
    assert str(bit_array) == '0b101'


def test_bitarray_from_int():
    """"""
    test_val = 5
    bit_array = BitArray.from_int(test_val)
    assert isinstance(bit_array, BitArray)
    assert len(bit_array) == math.ceil(math.log2(test_val))


def test_bitarray_from_bytes():
    """"""
    test_val = bytes.fromhex('010203')
    bit_array = BitArray.from_bytes(test_val)
    assert isinstance(bit_array, BitArray)
    assert len(bit_array) == len(test_val) * 8


def test_bitarray_read_int():
    """"""
    test_val = 101
    bit_array = BitArray.from_int(test_val)
    assert bit_array.read_int() == test_val
    assert bit_array.read_int(start=1) == 37
    test_val = -test_val
    bit_array = BitArray.from_int(test_val)
    assert bit_array.read_int(True) == test_val


def test_bitarray_read_bytes():
    """"""
    test_val = bytes.fromhex('010203')
    bit_array = BitArray.from_bytes(test_val)
    assert bit_array.read_bytes() == test_val
    assert bit_array.read_bytes(8) == test_val[1:]
    assert bit_array.read_bytes(8, 16) == test_val[1:2]
    assert bit_array.read_bytes(1) == (int.from_bytes(test_val, 'big') << 1).to_bytes(len(test_val), 'big')


def test_bitarray_lshift():
    """"""
    test_val = 15
    bit_array = BitArray.from_int(test_val)
    bit_array.lshift(1)
    assert bit_array.read_int() == test_val << 1


def test_bitarray_rshift():
    """"""
    test_val = 15
    bit_array = BitArray.from_int(test_val)
    bit_array.rshift(1)
    assert bit_array.read_int() == test_val >> 1
