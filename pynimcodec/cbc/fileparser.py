"""File parsing utilities for Compact Binary Codec."""

import json
import logging
import os

_log = logging.getLogger(__name__)


def import_json(filepath: str):
    """Import a JSON CBC definition file."""
    raise NotImplementedError
    if not os.path.isfile(filepath):
        raise ValueError('Invalid file path.')
    with open(filepath) as f:
        try:
            codec_dict = json.load(f)
        except Exception as exc:
            _log.error(exc)

def export_json(filepath: str):
    """Export a JSON CBC definition file."""
    raise NotImplementedError
