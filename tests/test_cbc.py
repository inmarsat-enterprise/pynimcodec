import pytest

from pynimcodec.bitman import extract_from_buffer
from pynimcodec.cbc import (
    BoolField,
    IntField,
    UintField,
    StringField,
    StructField,
    create_field,
    encode_field,
    decode_field,
)


@pytest.fixture
def int_field():
    return IntField(**{
        'name': 'testInt',
        'type': 'int',
        'size': 4,
    })


def test_create_field(int_field: IntField):
    """"""
    created = create_field({
        'name': 'testInt',
        'type': 'int',
        'size': 4,
    })
    assert isinstance(int_field, IntField)
    assert created == int_field


def test_int_field(int_field: IntField):
    """"""
    offsets = [0, 1]
    for offset in offsets:
        buffer = bytearray()
        test_vals = [-1, -5, 7, 0]
        for test_val in test_vals:
            buffer, new_offset = encode_field(int_field, test_val, buffer, offset)
            assert extract_from_buffer(buffer, offset, int_field.size, signed=True) == test_val
            assert new_offset == offset + int_field.size
    with pytest.raises(ValueError) as exc_info:
        buffer, _ = encode_field(int_field, 15, buffer, 0)
    assert 'too large' in exc_info.value.args[0]


def test_int_field_calc(int_field: IntField):
    """"""
    int_field.size = 6
    int_field.encalc = 'v*10'
    int_field.decalc = 'v/10'
    buffer = bytearray()
    offset = 0
    test_val = 2.2
    buffer, _ = encode_field(int_field, test_val, buffer, offset)
    assert extract_from_buffer(buffer, offset, int_field.size, signed=True) == test_val * 10
    decoded, _ = decode_field(int_field, buffer, offset)
    assert 'value' in decoded and decoded['value'] == test_val


def test_bool_field():
    bool_field = create_field({
        'name': 'testBool',
        'type': 'bool',
    })
    assert isinstance(bool_field, BoolField)
    buffer = bytearray()
    offset = 0
    buffer, new_offset = encode_field(bool_field, True, buffer, offset)
    assert new_offset == 1
    assert extract_from_buffer(buffer, 0, 1) == 1
    decoded, _ = decode_field(bool_field, buffer, offset)
    assert 'value' in decoded and decoded['value'] is True


def test_uint_field():
    test_field = create_field({
        'name': 'testUint',
        'type': 'uint',
        'size': 4,
    })
    assert isinstance(test_field, UintField)
    offsets = [0, 1]
    for offset in offsets:
        buffer = bytearray()
        test_vals = [1, 15, 0]
        for test_val in test_vals:
            buffer, new_offset = encode_field(test_field, test_val, buffer, offset)
            assert extract_from_buffer(buffer, offset, test_field.size) == test_val
            assert new_offset == offset + test_field.size
    with pytest.raises(ValueError) as exc_info:
        buffer, _ = encode_field(test_field, -1, buffer, 0)
    assert 'Invalid value' in exc_info.value.args[0]
    with pytest.raises(ValueError) as exc_info:
        buffer, _ = encode_field(test_field, 16, buffer, 0)
    assert 'too large' in exc_info.value.args[0]


def test_string_field():
    """"""
    test_field = create_field({
        'name': 'stringField',
        'type': 'string',
        'size': 250,
    })
    assert isinstance(test_field, StringField)
    test_val = 'test string'
    L_len = 1 if len(test_val) < 128 else 2
    offsets = [0, 1, 7]
    for offset in offsets:
        buffer = bytearray()
        buffer, new_offset = encode_field(test_field, test_val, buffer, offset)
        assert len(buffer) == L_len + len(test_val) + (1 if offset > 0 else 0)
        decoded, _ = decode_field(test_field, buffer, offset)
        assert 'value' in decoded and decoded['value'] == test_val


@pytest.mark.xfail
def test_codec_list():
    """TODO: ensure list methods enforce codec class"""
    assert False


def test_struct_field():
    test_field = create_field({
        'name': 'testStruct',
        'type': 'struct',
        'fields': [
            {
                'name': 'testNestedInt',
                'type': 'int',
                'size': 7,
            },
            {
                'name': 'testOptionalString',
                'type': 'string',
                'size': 50,
                'optional': True,
            }
        ]
    })
    assert isinstance(test_field, StructField)
    buffer = bytearray()
    offset = 0
    test_val = {
        'name': 'testStruct',
        'value': [
            {
                'testNestedInt': 42,
            }
        ]
    }
    buffer, new_offset = encode_field(test_field, test_val, buffer, offset)
    assert len(buffer) == 1
    decoded, _ = decode_field(test_field, buffer, offset)
    assert 'value' in decoded and decoded['value'] == test_val['value']
    test_val['value'].append({'testOptionalString': 'hello'})
    buffer, new_offset = encode_field(test_field, test_val, buffer, offset)
    assert len(buffer) == 7
    decoded, _ = decode_field(test_field, buffer, offset)
    assert 'value' in decoded and decoded['value'] == test_val['value']