from typing import Generic, List, Dict, Optional, TypeVar

from .index_driver import IndexDbDriver
from .model import Key

_KT = TypeVar('_KT')


class Index(Generic[_KT]):
    __db_drivers: Dict[str, IndexDbDriver]

    @staticmethod
    def set_db_drivers(db_drivers: List[IndexDbDriver]):
        Index.__db_drivers = {d.index_name: d for d in db_drivers}

    @classmethod
    def delete(cls, index_key: str):
        db_driver = Index.__db_drivers[cls.__name__]
        db_driver.delete(index_key)

    @staticmethod
    def _to_key(key: str):
        if key is None:
            return None
        else:
            return Key(key)

    @classmethod
    def get(cls, index_key: str) -> Optional[Key[_KT]]:
        db_driver = Index.__db_drivers[cls.__name__]
        return Index._to_key(db_driver.get(index_key))

    @classmethod
    def mget(cls, index_key: List[str]) -> List[Optional[Key[_KT]]]:
        if not index_key:
            return []
        db_driver = Index.__db_drivers[cls.__name__]
        return [Index._to_key(k) for k in db_driver.mget(index_key)]

    @classmethod
    def set(cls, index_key: str, model_key: Key[_KT]):
        db_driver = Index.__db_drivers[cls.__name__]
        db_driver.set(index_key, str(model_key))
