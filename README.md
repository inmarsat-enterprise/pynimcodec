# pynimcodec

A set of message codecs for use with satellite IoT products implemented
in Python.

## nimo

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