"""Validations for enum types."""


def valid_enum(size: int,
               keys_values: 'dict[str|int, str]',
               bitmask: bool = False) -> 'dict[str, str]':
    """Validate an enum definition to have numeric keys and string values.
    
    Args:
        size (int): The bit size of the enumeration field.
        keys_values (dict): The candidate to validate or convert.
        bitmask (bool): If True, key validation will be for a bitmask range
    
    Raises:
        ValueError if the candidate is empty, keys are non-numeric or duplicate
            or values are not strings
    """
    if not isinstance(size, int) or size < 1:
        raise ValueError('Invalid size must be > 0')
    if not isinstance(keys_values, dict) or not keys_values:
        raise ValueError('Invalid enumeration dictionary.')
    max_value = 2**size - 1
    if bitmask is True:
        max_value = size - 1
    for k in keys_values:
        try:
            key_int = int(k)
            if key_int < 0 or key_int > max_value:
                raise ValueError(f'Key {k} must be in range 0..{max_value}.')
        except ValueError as exc:
            if str(exc).startswith(f'Key {k}'):
                errmsg = str(exc)
            else:
                errmsg = f'Invalid key {k} must be integer parsable.'
            raise ValueError(errmsg) from exc
    seen = set()
    for v in keys_values.values():
        if not isinstance(v, str):
            raise ValueError('Invalid enumeration value must be string.')
        if v in seen:
            raise ValueError('Duplicate value found in list')
        seen.add(v)
    return { str(k): v for k, v in keys_values.items() }
    