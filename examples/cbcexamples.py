import os

from pynimcodec.cbc import import_json, encode_message, decode_message


codec = import_json(os.path.join(os.getcwd(), 'examples/cbc_codec.json'))

decoded_examples = [
    {
        'name': 'assetLocation',
        'value': {
            'location': {
                'fixTime': 1760013305,
                'latitude': 45.282,
                'longitude': -75.848,
                'altitude': 100,
            }
        }
    },
    {
        'name': 'getConfiguration',
        'value': {}
    },
    {
        'name': 'getConfiguration',
        'value': {
            'properties': ['reportInterval']
        }
    },
    {
        'name': 'configuration',
        'value': {
            'properties': [
                { 'name': 'devUid', 'value': 'abcd-1234', 'dataType': 'string' },
                { 'name': 'reportInterval', 'value': '15', 'dataType': 'uint' },
            ]
        }
    },
    {
        'name': 'setConfiguration',
        'value': {
            'properties': [
                { 'name': 'reportInterval', 'value': '30' },
            ]
        }
    },
    {
        'name': 'telemetry',
        'value': {
            'accessPanelClosed': True,
            'valveControl': 'OPEN',
            'faultConditions': ['PUMP_MOTOR_OVERCURRENT'],
            'txMetrics': {
                'CON': [
                    { 'packetsOk': 10, 'packetsFailed': 0 },
                ]
            },
            'powerFactor': 0.97,
        }
    },
    {
        'name': 'highFidelityMeasurement',
        'value': {
            'sampleCount': 25,
            'samples': 'DAAZAC0AUAByAKAA0gAEAToBaAFpAcIB4AH0AfQBwgGQAXgAYABQABQAFgASAAUACgD2/w==',
            'crc': 14927,
        }
    }
]


def main():
    for example in decoded_examples:
        # if example['name'] not in ['highFidelityMeasurement']:
        #     continue
        encoded: bytes = encode_message(example, messages=codec.messages, nim=True) # type: ignore
        print(f'{example["name"]} encoded {len(encoded)} bytes: {encoded.hex()}')
        direction = next(v.direction for v in codec.messages if v.name == example['name'])
        decoded = decode_message(
            encoded,
            direction=direction,
            messages=codec.messages,
            nim=True,
        )
        assert decoded == example
        print(f'{example["name"]} decoded: {decoded}')


if __name__ == '__main__':
    main()
