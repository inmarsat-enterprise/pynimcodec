"""Helper utilities for pynimcodec."""

import re


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
