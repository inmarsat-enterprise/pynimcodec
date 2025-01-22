import math
import os
import pytest

from pynimcodec.bitman import extract_from_buffer
from pynimcodec.cbc import (
    ArrayField,
    BitmaskArrayField,
    BitmaskField,
    BoolField,
    DataField,
    EnumField,
    FloatField,
    IntField,
    StringField,
    StructField,
    UintField,
    create_field,
    encode_field,
    decode_field,
    Message,
    Messages,
    MessageDirection,
    Fields,
    create_message,
    decode_message,
    encode_message,
    import_json,
    export_json,
)
from pynimcodec.cbc.field.calc import calc_decode, calc_encode


@pytest.fixture
def int_field():
    return IntField(**{
        'name': 'testInt',
        'type': 'int',
        'size': 4,
    })


def test_create_field(int_field):
    """"""
    created = create_field({
        'name': 'testInt',
        'type': 'int',
        'size': 4,
    })
    assert isinstance(created, IntField)
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
    assert 'exceeds' in exc_info.value.args[0]


@pytest.mark.parametrize('test_expr,v,expected', [
    ('v*10', 42.2, 422),
    ('v*10', -42.2, -422),
    ('v*10', 42.26, 422),
    ('round(v*10,0)', 42.26, 423),
    ('v*1', 42.2, 42),
    ('v/10', 422, 42),
    ('v/2', 10, 5),
    ('1+1', 3, None),
    ('eval(open("/etc/password"))', 0, None),
])
def test_calc_encode(test_expr, v, expected):
    """"""
    if 'v' not in test_expr:
        with pytest.raises(ValueError):
            calc_encode(test_expr, v)
    elif 'eval' in test_expr:
        with pytest.raises(ValueError):
            calc_encode(test_expr, v)
    else:
        assert calc_encode(test_expr, v) == expected


@pytest.mark.parametrize('test_expr,v,expected', [
    ('v+1', 1, 2),
    ('v**3', 2, 8),
    ('2**v-1', 3, 7),
    ('v/10', 422, 42.2),
    ('round(v/10**6,3)', 42123456, 42.123),
    ('-v', 1, -1),
    ('~v', -1, 1),
    ('1+1', 3, None),
])
def test_calc_decode(test_expr, v, expected):
    """"""
    if 'v' not in test_expr:
        with pytest.raises(ValueError):
            calc_decode(test_expr, v)
    else:
        assert calc_decode(test_expr, v) == expected


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
    assert 'Invalid' in exc_info.value.args[0]
    with pytest.raises(ValueError) as exc_info:
        buffer, _ = encode_field(test_field, 16, buffer, 0)
    assert 'exceeds' in exc_info.value.args[0]
    test_field.clip = True
    buffer, _ = encode_field(test_field, 16, buffer, 0)
    assert extract_from_buffer(buffer, 0, test_field.size) == 2**(test_field.size) - 1


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
        'testNestedInt': 42,
    }
    buffer, new_offset = encode_field(test_field, test_val, buffer, offset)
    assert len(buffer) == 1
    decoded, _ = decode_field(test_field, buffer, offset)
    assert 'value' in decoded and decoded['value'] == test_val
    test_val['testOptionalString'] = 'hello'
    buffer, new_offset = encode_field(test_field, test_val, buffer, offset)
    assert len(buffer) == 7
    decoded, _ = decode_field(test_field, buffer, offset)
    assert 'value' in decoded and decoded['value'] == test_val


def test_array_field():
    """"""
    test_field = create_field({
        'name': 'testArray',
        'type': 'array',
        'size': 10,
        'fields': [
            {
                'name': 'propName',
                'type': 'string',
                'size': 20
            },
            {
                'name': 'propValue',
                'type': 'uint',
                'size': 32
            },
            {
                'name': 'propDesc',
                'type': 'string',
                'size': 50,
                'optional': True,
            },
        ]
    })
    assert isinstance(test_field, ArrayField)
    test_val = [
        { 'propName': 'property1', 'propValue': 1 },
        { 'propName': 'property2', 'propValue': 2 },
    ]
    buffer = bytearray()
    offset = 0
    buffer, _ = encode_field(test_field, test_val, buffer, offset)
    assert len(buffer) == 30
    decoded, _ = decode_field(test_field, buffer, 0)
    assert decoded['name'] == test_field.name
    assert decoded['value'] == test_val
    test_val.append({ 'propName': 'property3', 'propValue': 3, 'propDesc': 'A property description' })
    buffer = bytearray()
    buffer, _ = encode_field(test_field, test_val, buffer, offset)
    decoded, _ = decode_field(test_field, buffer, 0)
    assert decoded['value'] == test_val


def test_bitmask_field():
    """"""
    test_field = create_field({
        'name': 'testBitmask',
        'type': 'bitmask',
        'size': 12,
        'enum': {
            '0': 'LSB',
            '11': 'MSB',
        },
    })
    assert isinstance(test_field, BitmaskField)
    test_val = ['LSB', 'MSB']
    buffer = bytearray()
    offset = 0
    buffer, _ = encode_field(test_field, test_val, buffer, offset)
    assert len(buffer) == 2
    assert int.from_bytes(buffer, 'big') == 0x0801 << (16 - 12)
    decoded, _ = decode_field(test_field, buffer, 0)
    assert decoded['name'] == test_field.name
    assert decoded['value'] == test_val
    test_val_2 = 0x801
    buffer, _ = encode_field(test_field, test_val_2, buffer, offset)
    assert int.from_bytes(buffer, 'big') == 0x801 << (16 - 12)
    decoded2, _ = decode_field(test_field, buffer, 0)
    assert decoded2['value'] == test_val


def test_bitmaskarray_field():
    """"""
    test_field = create_field({
        'name': 'testBitmaskArray',
        'type': 'bitmaskarray',
        'size': 3,
        'enum': {
            '0': 'case1',
            '1': 'case2',
            '2': 'case3',
        },
        'fields': [
            {
                'name': 'successes',
                'type': 'uint',
                'size': 4
            },
            {
                'name': 'failures',
                'type': 'uint',
                'size': 4
            }
        ]
    })
    assert isinstance(test_field, BitmaskArrayField)
    test_val = {
        'case1': [{'successes': 3, 'failures': 1}]
    }
    buffer = bytearray()
    offset = 0
    buffer, _ = encode_field(test_field, test_val, buffer, offset)
    assert len(buffer) == math.ceil((3 + 4 + 4)/ 8)
    decoded, _ = decode_field(test_field, buffer, 0)
    assert decoded['value'] == test_val


def test_data_field():
    """"""
    test_field = create_field({
        'name': 'testData',
        'type': 'data',
        'size': 100,
    })
    assert isinstance(test_field, DataField)
    test_val = bytes([0,1,2,3])
    buffer = bytearray()
    offset = 0
    buffer, _ = encode_field(test_field, test_val, buffer, offset)
    assert len(buffer) == len(test_val) + 1 if len(test_val) < 128 else 2
    decoded, _ = decode_field(test_field, buffer, 0)
    assert decoded['value'] == test_val


def test_enum_field():
    """"""
    test_field = create_field({
        'name': 'testEnum',
        'type': 'enum',
        'size': 5,
        'enum': {
            '0': 'zero',
            '1': 'one',
        }
    })
    assert isinstance(test_field, EnumField)
    test_val = 'one'
    buffer = bytearray()
    offset = 0
    encoded, _ = encode_field(test_field, test_val, buffer, offset)
    assert len(encoded) == 1
    assert encoded[0] == 1 << (8 - test_field.size)
    decoded, _ = decode_field(test_field, buffer, 0)
    assert decoded['value'] == test_val


def test_float_field():
    """"""
    test_field = create_field({
        'name': 'testFloat',
        'type': 'float',
        'size': 32,
        'precision': 3,
    })
    assert isinstance(test_field, FloatField)
    test_val = 42.123
    buffer = bytearray()
    offset = 0
    encoded, _ = encode_field(test_field, test_val, buffer, offset)
    assert len(encoded) == 4
    decoded, _ = decode_field(test_field, buffer, offset)
    assert decoded['value'] == test_val


def test_message():
    """"""
    test_message = create_message({
        'name': 'testMoMessage',
        'direction': 'UPLINK',
        'messageKey': 49152,
        'fields': [
            { 'name': 'testUintField', 'type': 'uint', 'size': 4 },
            { 'name': 'testString', 'type': 'string', 'size': 50, 'optional': True},
            {
                'name': 'testStruct',
                'type': 'struct',
                'fields': [
                    {
                        'name': 'value1',
                        'type': 'int',
                        'size': 16
                    }
                ],
            }
        ]
    })
    assert isinstance(test_message, Message)
    test_val = {
        'name': 'testMoMessage',
        'value': {
            'testUintField': 3,
            'testString': 'hello',
            'testStruct': {
                'value1': 1,
            }
        }
    }
    encoded = encode_message(test_val, message=test_message)
    assert len(encoded) == 7 if len(test_val['value'].keys()) == 2 else 1
    decoded = decode_message(encoded, message=test_message)
    assert decoded == test_val
    encoded = encode_message(test_val, message=test_message, nim=True)
    assert len(encoded) == 9 if len(test_val['value'].keys()) == 2 else 3
    decoded = decode_message(encoded, message=test_message, nim=True)
    assert decoded == test_val
    coap_message = encode_message(test_val, message=test_message, coap=True)
    assert coap_message.mid == test_message.message_key
    assert len(coap_message.payload) == 7 if len(test_val['value'].keys()) == 2 else 1
    # coap_encoded = coap_message.encode()
    # decoded = decode_message(coap_encoded, message=test_message, coap=True)
    assert decoded == test_val


def test_file_import():
    """"""
    test_path = os.path.join(os.getcwd(), 'tests/examples/cbcimport.json')
    app_codec = import_json(test_path)
    assert isinstance(app_codec, Messages)
    test_val = {
        'name': 'TestMessage',
        # 'direction': 'UPLINK',
        # 'messageKey': 49152,
        'value': {
            'exampleField': 42,
        }
    }
    encoded = app_codec.encode(test_val)
    assert len(encoded) == 1
    decoded = app_codec.decode(encoded, name=test_val['name'])
    assert decoded == test_val


def test_file_export():
    """"""
    test_path = os.path.join(os.getcwd(), 'tests/examples/cbcexport.json')
    codec_list = Messages()
    test_message = Message(name='testMessage',
                           direction=MessageDirection.MO,
                           message_key=49152,
                           fields=Fields([
                               IntField(name='testIntField', size=4,),
                            ]))
    codec_list.append(test_message)
    export_json(test_path, codec_list)
    assert os.path.isfile(test_path)
    imported = import_json(test_path)
    assert imported == codec_list
