import base64
import math
import os
import pytest

from aiocoap import Code, Type
from aiocoap.optiontypes import OpaqueOption

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
    Application,
    import_json,
    export_json,
)
from pynimcodec.cbc.field.calc import calc_decode, calc_encode


@pytest.fixture
def int_field():
    return IntField(name='testInt', size=4)


def test_create_field(int_field: IntField):
    """Test creating a field from a dict"""
    created = create_field({
        'name': 'testInt',
        'type': 'int',
        'size': 4,
    })
    assert isinstance(created, IntField)
    assert created == int_field


def test_int_field(int_field: IntField):
    """Test encoding and decoding of integer at different offsets."""
    offsets = [0, 1]
    for offset in offsets:
        buffer = bytearray()
        test_vals = [-1, -5, 7, 0]
        for test_val in test_vals:
            buffer, new_offset = encode_field(int_field, test_val, buffer, offset)
            assert extract_from_buffer(buffer, offset, int_field.size, signed=True) == test_val
            assert new_offset == offset + int_field.size


def test_int_field_out_of_range(int_field: IntField):
    """Test that values out of range raise ValueError with exception message."""
    buffer = bytearray()
    with pytest.raises(ValueError) as exc_info:
        buffer, _ = encode_field(int_field, 15, buffer, 0)
    assert '<=' in exc_info.value.args[0]
    with pytest.raises(ValueError) as exc_info:
        buffer, _ = encode_field(int_field, -16, buffer, 0)
    assert '>=' in exc_info.value.args[0]


def test_int_max_min(int_field: IntField):
    """Test int encoding uses min and max values."""
    int_field.min = -1
    int_field.max = 3
    buffer = bytearray()
    buffer, _ = encode_field(int_field, -3, buffer, 0)
    assert extract_from_buffer(buffer, 0, int_field.size, signed=True) == int_field.min
    buffer, _ = encode_field(int_field, 5, buffer, 0)
    assert extract_from_buffer(buffer, 0, int_field.size, signed=True) == int_field.max


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
    """Test various cases of parsing encalc strings to expressions."""
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
    """Test various cases of parsing decalc strings to expressions."""
    if 'v' not in test_expr:
        with pytest.raises(ValueError):
            calc_decode(test_expr, v)
    else:
        assert calc_decode(test_expr, v) == expected


def test_int_field_calc(int_field: IntField):
    """Test encalc and decalc used on an integer."""
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
    """Test boolean field manipulations"""
    bool_field = BoolField(name='testBool')
    test_field = create_field({
        'name': 'testBool',
        'type': 'bool',
    })
    assert isinstance(test_field, BoolField)
    assert test_field == bool_field
    buffer = bytearray()
    offset = 0
    buffer, new_offset = encode_field(test_field, True, buffer, offset)
    assert new_offset == 1
    assert extract_from_buffer(buffer, 0, 1) == 1
    decoded, _ = decode_field(test_field, buffer, offset)
    assert 'value' in decoded and decoded['value'] is True


@pytest.fixture
def uint_field():
    return UintField(name='testUint', size=4)


def test_uint_field(uint_field: UintField):
    """Test creation and basic operations on unsigned int."""
    test_field = create_field({
        'name': 'testUint',
        'type': 'uint',
        'size': 4,
    })
    assert isinstance(test_field, UintField)
    assert test_field == uint_field
    offsets = [0, 1]
    for offset in offsets:
        buffer = bytearray()
        test_vals = [1, 15, 0]
        for test_val in test_vals:
            buffer, new_offset = encode_field(test_field, test_val, buffer, offset)
            assert extract_from_buffer(buffer, offset, test_field.size) == test_val
            assert new_offset == offset + test_field.size


def test_uint_out_of_range(uint_field: UintField):
    """Test unsigned values out of size range."""
    buffer = bytearray()
    with pytest.raises(ValueError) as exc_info:
        buffer, _ = encode_field(uint_field, -1, buffer, 0)
    assert 'Invalid' in exc_info.value.args[0]
    with pytest.raises(ValueError) as exc_info:
        buffer, _ = encode_field(uint_field, 16, buffer, 0)
    assert '<=' in exc_info.value.args[0]


def test_uint_max_min(uint_field: UintField):
    """Test unsigned int uses max and min."""
    uint_field.min = 1
    uint_field.max = 4
    buffer = bytearray()
    buffer, _ = encode_field(uint_field, 0, buffer, 0)
    assert extract_from_buffer(buffer, 0, uint_field.size) == uint_field.min
    buffer, _ = encode_field(uint_field, 16, buffer, 0)
    assert extract_from_buffer(buffer, 0, uint_field.size) == uint_field.max


def test_string_field():
    """"""
    str_field = StringField(name='stringField', size=250)
    test_field = create_field({
        'name': 'stringField',
        'type': 'string',
        'size': 250,
    })
    assert isinstance(test_field, StringField)
    assert test_field == str_field
    test_val = 'test string'
    L_len = 1 if len(test_val) < 128 else 2
    offsets = [0, 1, 7]
    for offset in offsets:
        buffer = bytearray()
        buffer, _ = encode_field(test_field, test_val, buffer, offset)
        assert len(buffer) == L_len + len(test_val) + (1 if offset > 0 else 0)
        decoded, _ = decode_field(test_field, buffer, offset)
        assert 'value' in decoded and decoded['value'] == test_val


@pytest.mark.xfail
def test_codec_list():
    """TODO: ensure list methods enforce codec class"""
    assert False


def test_struct_field():
    """Test basic struct field operations."""
    struct_field = StructField(name='testStruct',
                               fields=Fields(
                                   (IntField(name='testNestedInt', size=7),
                                    StringField(name='testOptionalString',
                                                optional=True,
                                                size=50),
                                    )))
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
    assert struct_field == test_field
    buffer = bytearray()
    offset = 0
    test_val = {
        'testNestedInt': 42,
    }
    buffer, _ = encode_field(test_field, test_val, buffer, offset)
    assert len(buffer) == 1
    decoded, _ = decode_field(test_field, buffer, offset)
    assert 'value' in decoded and decoded['value'] == test_val
    test_val['testOptionalString'] = 'hello'
    buffer, _ = encode_field(test_field, test_val, buffer, offset)
    assert len(buffer) == 7
    decoded, _ = decode_field(test_field, buffer, offset)
    assert 'value' in decoded and decoded['value'] == test_val

@pytest.fixture
def array_field():
    return ArrayField(name='testArray',
                      size=10,
                      fields=Fields((
                          StringField(name='propName', size=20),
                          UintField(name='propValue', size=32),
                          StringField(name='propDesc',
                                      size=50,
                                      optional=True),
                          )))

def test_array_field(array_field: ArrayField):
    """Test basic array field operations."""
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
    assert test_field == array_field
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
    test_val.append({
        'propName': 'property3',
        'propValue': 3, 
        'propDesc': 'A property description',
    })
    buffer = bytearray()
    buffer, _ = encode_field(test_field, test_val, buffer, offset)
    decoded, _ = decode_field(test_field, buffer, 0)
    assert decoded['value'] == test_val


@pytest.fixture
def enum_field():
    return EnumField(name='testEnum',
                     size=5,
                     enum={0: 'zero', 1: 'one'})


def test_enum_field(enum_field: EnumField):
    """Test basic enum field operations."""
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
    assert test_field == enum_field
    test_val = 'one'
    buffer = bytearray()
    offset = 0
    encoded, _ = encode_field(test_field, test_val, buffer, offset)
    assert len(encoded) == 1
    assert encoded[0] == 1 << (8 - test_field.size)
    decoded, _ = decode_field(test_field, encoded, 0)
    assert decoded['value'] == test_val


def test_enum_invalid():
    """Test invalid enum scenarios."""
    with pytest.raises(ValueError) as exc_info:
        _ = EnumField(name='invalidEnum',
                      size=4,
                      enum={0: 'VALID', 16: 'INVALID'})
    assert exc_info.value.args[0].startswith('Key 16')


@pytest.fixture
def bitmask_field():
    return BitmaskField(name='testBitmask',
                        size=12,
                        enum={ '0': 'LSB', '11': 'MSB'})


def test_bitmask_field(bitmask_field: BitmaskField):
    """Tests main bitmask field operations."""
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
    assert test_field == bitmask_field
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


def test_bitmask_invalid():
    """Test that keys are validated."""
    with pytest.raises(ValueError) as exc_info:
        _ = BitmaskField(name='invalidBitmask',
                         size=12,
                         enum={'zero': 'LSB', 'eleven': 'MSB'})
    assert 'Invalid key' in exc_info.value.args[0]
    with pytest.raises(ValueError) as exc_info:
        _ = BitmaskField(name='invalidBitmask',
                         size=12,
                         enum={0: 'LSB', 12: 'MSB'})
    assert exc_info.value.args[0].startswith('Key 12')


@pytest.fixture
def bitmaskarray_field():
    return BitmaskArrayField(name='testBitmaskArray',
                             size=3,
                             enum={
                                 0: 'case1',
                                 1: 'case2',
                                 2: 'case3',
                             },
                             fields=Fields((
                                 UintField(name='successes', size=4),
                                 UintField(name='failures', size=4),
                             )))


def test_bitmaskarray_field(bitmaskarray_field: BitmaskArrayField):
    """Test basic operations on bitmask array field."""
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
    assert test_field == bitmaskarray_field
    test_val = {
        'case1': [{'successes': 3, 'failures': 1}]
    }
    buffer = bytearray()
    offset = 0
    buffer, _ = encode_field(test_field, test_val, buffer, offset)
    assert len(buffer) == math.ceil((3 + 4 + 4)/ 8)
    decoded, _ = decode_field(test_field, buffer, 0)
    assert decoded['value'] == test_val


@pytest.fixture
def data_field():
    return DataField(name='testData',
                     size=100)

def test_data_field(data_field: DataField):
    """"""
    test_field = create_field({
        'name': 'testData',
        'type': 'data',
        'size': 100,
    })
    assert isinstance(test_field, DataField)
    assert test_field == data_field
    test_data = bytes([0,1,2,3])
    test_val = base64.b64encode(test_data).decode('utf-8')
    buffer = bytearray()
    offset = 0
    buffer, _ = encode_field(test_field, test_val, buffer, offset)
    assert len(buffer) == len(test_data) + 1 if len(test_data) < 128 else 2
    decoded, _ = decode_field(test_field, buffer, 0)
    assert decoded['value'] == test_val


@pytest.fixture
def float_field():
    return FloatField(name='testFloat', precision=3)


@pytest.fixture
def double_field():
    return FloatField(name='testDouble', size=64)


def test_float_field(float_field: FloatField):
    """Test basic float operations."""
    test_field = create_field({
        'name': 'testFloat',
        'type': 'float',
        'size': 32,
        'precision': 3,
    })
    assert isinstance(test_field, FloatField)
    assert test_field == float_field
    test_val = 42.123
    buffer = bytearray()
    offset = 0
    encoded, _ = encode_field(test_field, test_val, buffer, offset)
    assert len(encoded) == 4
    decoded, _ = decode_field(test_field, encoded, offset)
    assert decoded['value'] == test_val


@pytest.fixture
def message_codec():
    return Message(name='testMoMessage',
                   direction=MessageDirection.MO,
                   message_key=49152,
                   fields=Fields((
                       UintField(name='testUintField', size=4),
                       StringField(name='testString', size=50, optional=True),
                       StructField(name='testStruct',
                                   fields=Fields((
                                       IntField(name='value1', size=16),
                                   )))
                   )))


def test_message(message_codec: Message):
    """Test message codec operations."""
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
    assert test_message == message_codec
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


def test_coap_message_options(message_codec: Message):
    """"""
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
    coap_message = encode_message(test_val, message=message_codec, coap=True)
    assert coap_message.mid == message_codec.message_key
    assert len(coap_message.payload) == 7 if len(test_val['value'].keys()) == 2 else 1
    coap_message.code = Code.POST
    coap_message.mtype = Type.NON
    coap_encoded = coap_message.encode()
    decoded = decode_message(coap_encoded,
                             direction=MessageDirection.MO,
                             message=message_codec,
                             coap=True)
    assert 'coapOptions' not in decoded
    test_imsi = '123456789012345'
    imsi_opt = 65000
    coap_message.opt.add_option(OpaqueOption(imsi_opt, test_imsi.encode()))
    coap_encoded = coap_message.encode()
    decoded = decode_message(coap_encoded,
                             direction=MessageDirection.MO,
                             message=message_codec,
                             coap=True)
    assert 'coapOptions' in decoded
    coap_options = decoded.pop('coapOptions', None)
    assert isinstance(coap_options, dict)
    assert coap_options.get(imsi_opt).decode() == test_imsi
    assert decoded == test_val


def test_file_import():
    """Test importing from a JSON file set of message codecs."""
    test_path = os.path.join(os.getcwd(), 'tests/examples/cbcimport.json')
    app_codec = import_json(test_path)
    assert isinstance(app_codec, Application)
    test_val = {
        'name': 'TestMessage',
        'value': {
            'exampleField': 42,
        }
    }
    encoded = app_codec.encode(test_val)
    assert len(encoded) == 4   # <message_key><uint><opt_bit><pad>
    decoded = app_codec.decode(encoded, direction=MessageDirection.MO)
    assert decoded == test_val


def test_file_export():
    """Test exporting a set of message codecs."""
    test_path = os.path.join(os.getcwd(), 'tests/examples/cbcexport.json')
    codec_list = Messages()
    try:
        test_message = Message(name='testMessage',
                            direction=MessageDirection.MO,
                            message_key=49152,
                            fields=Fields((
                                BoolField(name='testBoolField'),
                                IntField(name='testIntField',
                                            size=6,
                                            optional=True),
                                UintField(name='testUintField', size=4),
                                FloatField(name='testFloatField'),
                                StringField(name='testStringField',
                                            size=32),
                                DataField(name='testDataField',
                                            size=8,
                                            fixed=True),
                                EnumField(name='testEnumField',
                                            size=4,
                                            enum={
                                                '0': 'ZERO',
                                                '1': 'ONE',
                                            }),
                                StructField(name='testStructField',
                                            fields=Fields((IntField(name='testIntInStruct', 
                                                                    size=8),))),
                                ArrayField(name='testArrayField', 
                                            size=10,
                                            fields=Fields((IntField(name='testInInArray', 
                                                                    size=4),
                                                            UintField(name='testUintInArray', 
                                                                    size=4)))),
                                BitmaskArrayField(name='testBmaField', size=8,
                                                    enum={"0": "NON", "1": "CON"},
                                                    fields=Fields((
                                                        UintField(name='success', size=32),
                                                        UintField(name='failed', size=32),
                                                    ))),
                            )))
        codec_list.append(test_message)
        export_json(test_path, codec_list, indent=2)
        assert os.path.isfile(test_path)
        imported = import_json(test_path)
        assert isinstance(imported, Application)
        assert imported.messages == codec_list
    finally:
        if os.path.isfile(test_path):
            os.remove(test_path)    
