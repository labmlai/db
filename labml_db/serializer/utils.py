from labml_db import Key
from labml_db.types import Primitive


def encode_keys(data: Primitive):
    if isinstance(data, Key):
        return {'__key__': str(data)}
    elif isinstance(data, list):
        return [encode_keys(d) for d in data]
    elif isinstance(data, dict):
        return {k: encode_keys(v) for k, v in data.items()}
    else:
        return data


def decode_keys(data: Primitive):
    if isinstance(data, dict) and '__key__' in data:
        return Key(data['__key__'])
    elif isinstance(data, list):
        return [decode_keys(d) for d in data]
    elif isinstance(data, dict):
        return {k: decode_keys(v) for k, v in data.items()}
    else:
        return data
