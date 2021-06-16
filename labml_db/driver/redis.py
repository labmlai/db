from typing import List, Type, TYPE_CHECKING, Optional

from . import DbDriver
from ..types import ModelDict

if TYPE_CHECKING:
    import redis
    from .. import Serializer
    from ..model import Model


class RedisDbDriver(DbDriver):
    def __init__(self, serializer: 'Serializer', model_cls: Type['Model'], db: 'redis.Redis'):
        super().__init__(serializer, model_cls)
        self._db = db

    @property
    def _keys_list_key(self):
        return f'_keys:{self.model_name}'

    def mload_dict(self, key: List[str]) -> List[Optional[ModelDict]]:
        data = self._db.mget(key)
        return [self._serializer.from_string(d) for d in data]

    def load_dict(self, key: str) -> Optional[ModelDict]:
        return self._serializer.from_string(self._db.get(key))

    def save_dict(self, key: str, data: ModelDict):
        self._db.sadd(self._keys_list_key, key)
        self._db.set(key, self._serializer.to_string(data))

    def delete(self, key: str):
        self._db.srem(self._keys_list_key, key)
        self._db.delete(key)

    def get_all(self) -> List[str]:
        keys = self._db.smembers(self._keys_list_key)
        return [k.decode('utf-8') for k in keys]
