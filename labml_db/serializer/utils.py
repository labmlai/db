from typing import Dict

from .. import Key
from ..types import Primitive


def encode_key(key: Key) -> Dict[str, str]:
    return {'__key__': str(key)}


def decode_key(key_dict: Dict) -> Key:
    return Key(key_dict['__key__'])


def encode_keys(data: Primitive):
    if isinstance(data, Key):
        return encode_key(data)
    elif isinstance(data, list):
        return [encode_keys(d) for d in data]
    elif isinstance(data, dict):
        return {k: encode_keys(v) for k, v in data.items()}
    else:
        return data


def decode_keys(data: Primitive):
    if isinstance(data, dict) and '__key__' in data:
        return decode_key(data)
    elif isinstance(data, list):
        return [decode_keys(d) for d in data]
    elif isinstance(data, dict):
        return {k: decode_keys(v) for k, v in data.items()}
    else:
        return data
