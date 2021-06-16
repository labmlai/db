from typing import Optional, List

from .index import Index
from .model import Model, Key, KeyList
from .serializer import Serializer


def load_key(key: Optional[Key]):
    return key.load() if key else None


def load_keys(keys: List[Optional[Key]]):
    _keys = []
    idx = []
    res: List[Optional[Model]] = [None for _ in keys]

    for i, k in enumerate(keys):
        if k:
            _keys.append(k)
            idx.append(i)

    key_list = KeyList(_keys)
    values = key_list.load()

    for i, v in zip(idx, values):
        res[i] = v

    return res


__all__ = [Serializer, Model, Key, KeyList, Index, load_key, load_keys]
