from typing import Dict, Type, Optional, TYPE_CHECKING, List

from . import IndexDbDriver

if TYPE_CHECKING:
    import redis
    from .. import Index


class RedisIndexDbDriver(IndexDbDriver):
    _cache: Optional[Dict[str, str]]

    def __init__(self, index_cls: Type['Index'], db: 'redis.Redis'):
        super().__init__(index_cls)
        self._db = db

    @property
    def _index_key(self):
        return f'_index:{self.index_name}'

    def delete(self, index_key: str):
        self._db.hdel(self._index_key, index_key)

    def get(self, index_key: str) -> str:
        return self._db.hget(self._index_key, index_key)

    def mget(self, index_key: List[str]) -> List[str]:
        return self._db.hmget(self._index_key, index_key)


    def set(self, index_key: str, model_key: str):
        self._db.hset(self._index_key, index_key, model_key)
