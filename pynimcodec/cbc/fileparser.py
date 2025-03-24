"""File parsing utilities for Compact Binary Codec."""

import json
import logging
import os

from .application import Application
from .message import Messages, create_message

__all__ = [ 'export_json', 'import_json' ]

_log = logging.getLogger(__name__)


required_keys = ['application', 'messages']

def import_json(filepath: str) -> Application:
    """Import a JSON CBC definition file."""
    if not os.path.isfile(filepath):
        raise ValueError('Invalid file path.')
    with open(filepath) as f:
        try:
            codec_dict: dict = json.load(f)
            if not all(k in codec_dict for k in required_keys):
                raise ValueError(f'Missing required keys ({required_keys})')
            message_list = codec_dict.get('messages')
            if (not isinstance(message_list, list) or
                not all(isinstance(msg, dict) for msg in message_list)):
                raise ValueError('messages must be a list')
            messages = Messages()
            for message in message_list:
                messages.append(create_message(message))
            return Application(application=codec_dict.get('application'),
                               version=codec_dict.get('version'),
                               description=codec_dict.get('description'),
                               messages=messages)
        except Exception as exc:
            _log.error(exc)

def export_json(filepath: str, messages: Messages, **kwargs) -> None:
    """Export a JSON CBC definition file.
    
    Args:
        filepath (str): The output path of the JSON file.
        messages (Messages): The codec list of messages to export.
        **application (str): The application name (default: `cbcApplication`)
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
