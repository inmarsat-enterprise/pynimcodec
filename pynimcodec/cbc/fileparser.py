"""File parsing utilities for Compact Binary Codec."""

import json
import logging
import os

from .application import Application
from .message import Messages, create_message

__all__ = [ 'export_json', 'import_json' ]

_log = logging.getLogger(__name__)


required_keys = ['application', 'messages']

def import_json(filepath: str) -> Messages:
    """Import a JSON CBC definition file."""
    if not os.path.isfile(filepath):
        raise ValueError('Invalid file path.')
    with open(filepath) as f:
        try:
            codec_dict = json.load(f)
            if not all(k in codec_dict for k in required_keys):
                raise ValueError(f'Missing required keys ({required_keys})')
            messages = codec_dict.get('messages')
            if (not isinstance(messages, list) or
                not all(isinstance(msg, dict) for msg in messages)):
                raise ValueError('messages must be a list')
            message_codec = Messages()
            for message in messages:
                message_codec.append(create_message(message))
            return message_codec
        except Exception as exc:
            _log.error(exc)

def export_json(filepath: str, messages: Messages, **kwargs) -> None:
    """Export a JSON CBC definition file.
    
    Args:
        filepath (str): The output path of the JSON file.
        messages (Messages): The codec list of messages to export.
        **name (str): The application name (default: `cbcApplication`)
        **version (str): Semver-style version string (default `1.0`)
        **description (str): Optional description for the intended use.
        **indent (int): Pretty print JSON export with indentation
    """
    if not os.path.exists(os.path.dirname(os.path.abspath(filepath))):
        raise ValueError('Invalid target directory.')
    if not isinstance(messages, Messages):
        raise ValueError('Invalid Messages codec list.')
    app = Application(messages=messages, **kwargs)
    indent = kwargs.get('indent')
    if indent is not None and (not isinstance(indent, int) or indent < 2):
        raise ValueError('Invalid indent setting')
    sep = None if indent else (',', ':')
    with open(filepath, 'w') as f:
        f.write(json.dumps(app.to_json(), indent=indent, separators=sep))
