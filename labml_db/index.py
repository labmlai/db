from typing import Generic, List, Dict, Optional, TypeVar, TYPE_CHECKING

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

    @classmethod
    def get(cls, index_key: str) -> Optional[Key[_KT]]:
        db_driver = Index.__db_drivers[cls.__name__]
        key = db_driver.get(index_key)
        if key is None:
            return None
        else:
            return Key(key)

    @classmethod
    def set(cls, index_key: str, model_key: Key[_KT]):
        db_driver = Index.__db_drivers[cls.__name__]
        db_driver.set(index_key, str(model_key))
