# pynimcodec

A set of message codecs for use with satellite IoT products implemented
in Python.

## NIMO

The NIMO message codec was designed by ORBCOMM and represents an efficient
binary data packing for various data types at a bit-level.

This module also provides facilities to build a XML file compliant with the
ORBCOMM and/or Viasat *Message Definition File* concept to apply to messages
sent over the IsatData Pro service.

The principles of the NIMO *Common Message Format* are:

* First byte of payload is *Service Identification Number* (**SIN**)
representing a microservice running on an IoT device.
Each `<Service>` consists of `<ForwardMessages>` (e.g. commands) and/or
`<ReturnMessages>` (e.g. reports or responses from the IoT device).
SIN must be in a range 16..255.
    
> [!WARNING]
> SIN range 16..127 may *conflict* with certain ORBCOMM-reserved messages
> when using the ORBCOMM IDP service.

* Second byte of payload is *Message Identification Number* (**MIN**)
representing a remote operation such as a data report or a command.
The combination of **SIN** and **MIN** and direction (Forward/Return) enables
decoding of subsequent `<Fields>` containing data.

* Subsequent bytes of data are defined by `<Fields>` where each `<Field>` has
a data type such as `<SignedIntField>`, `<EnumField>`, etc.
These fields can be defined on individual bitwise boundaries, for example a
5-bit unsigned integer with maximum value 31, or a boolean single bit.

> [!WARNING]
> Fields types currently not supported by this library include:
> PropertyField, DynamicField, MessageField, ArrayField

### Running Tests

Several example test cases have been included as an example of encoding and
decoding messages using different types of codecs. The primary test cases include:

* test_nimo_encode_decode
* test_nimo_decode_properties
* test_nimo_decode_lua_terminals
* test_nimo_sc1000

These tests can be run using `pytest`.

Each test case includes a `exclude` which can be toggled to include the
test case when running the full decode or encode suite of test cases.

Certain test cases include codecs which can not be shared publicly. If
you require these codecs, please contact mark.dabrowski@viasat.com.


