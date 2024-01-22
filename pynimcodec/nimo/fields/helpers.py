import math
import re


def optimal_bits(value_range: 'tuple[int, int]') -> int:
    """Returns the optimal number of bits for encoding a specified range.
    
    Args:
        value_range: A tuple with the minimum and maximum values.
    
    Returns:
        The number of bits to optimally encode the value.
    
    Raises:
        ValueError if the 

    """
    if (not isinstance(value_range, tuple) or
        len(value_range) != 2 or
        not all(isinstance(x, int) for x in value_range) or
        value_range[0] >= value_range[1]):
        #: non-compliant
        raise ValueError('value_range must be of form (min, max)')
    total_range = value_range[1] - value_range[0]
    total_range += 1 if value_range[0] == 0 else 0
    return max(1, math.ceil(math.log2(total_range)))


def encode_field_length(length) -> str:
    if length < 128:
        return f'0{length:07b}'
    return f'1{length:015b}'


def decode_field_length(binstr: str) -> 'tuple[int, int]':
    if binstr[0] == '0':
        bit_index = 8
    else:
        bit_index = 16
    length = int(binstr[1:bit_index], 2)
    return (length, bit_index)


def camel_case(original: str,
               skip_caps: bool = False,
               skip_pascal: bool = False) -> str:
    """Converts a string to camelCase.
    
    Args:
        original: The string to convert.
        skip_caps: If `True` will return CAPITAL_CASE unchanged
        skip_pascal: If `True` will return PascalCase unchanged
    
    Returns:
        The input string in camelCase structure.
        
    """
    if not isinstance(original, str) or not original:
        raise ValueError('Invalid string input')
    if original.isupper() and skip_caps:
        return original
    words = original.split('_')
    if len(words) == 1:
        regex = '.+?(?:(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|$)'
        matches = re.finditer(regex, original)
        words = [m.group(0) for m in matches]
    if skip_pascal and all(word.title() == word for word in words):
        return original
    return words[0].lower() + ''.join(w.title() for w in words[1:])


def snake_case(original: str,
               skip_caps: bool = False,
               skip_pascal: bool = False) -> str:
    """Converts a string to snake_case.
    
    Args:
        original: The string to convert.
        skip_caps: A flag if `True` will return CAPITAL_CASE unchanged.
        skip_pascal: A flag if `True` will return PascalCase unchanged.
        
    Returns:
        The original string converted to snake_case format.
        
    Raises:
        `ValueError` if original is not a valid string.
        
    """
    if not isinstance(original, str) or not original:
        raise ValueError('Invalid string input')
    if original.isupper() and skip_caps:
        return original
    snake = re.compile(r'(?<!^)(?=[A-Z])').sub('_', original).lower()
    if '__' in snake:
        words = snake.split('__')
        snake = '_'.join(f'{word.replace("_", "")}' for word in words)
    words = snake.split('_')
    if original[0].isupper() and skip_pascal:
        if all(word.title() in original for word in words):
            return original
    return snake
