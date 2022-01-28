from typing import Type, TYPE_CHECKING, List

if TYPE_CHECKING:
    from . import Index


class IndexDbDriver:
    def __init__(self, index_cls: Type['Index']):
        self.index_name = index_cls.__name__

    def delete(self, index_key: str):
        raise NotImplementedError

    def get(self, index_key: str) -> str:
        raise NotImplementedError

    def mget(self, index_key: List[str]) -> List[str]:
        raise NotImplementedError

    def set(self, index_key: str, model_key: str):
        raise NotImplementedError

    def get_all(self) -> List[str]:
        raise NotImplementedError
