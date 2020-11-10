from typing import List, Type, TYPE_CHECKING, Optional

from ..types import ModelDict

if TYPE_CHECKING:
    from .. import Serializer, Model


class DbDriver:
    def __init__(self, serializer: 'Serializer', model_cls: Type['Model']):
        self.model_name = model_cls.__name__
        self._serializer = serializer

    def load_dict(self, key: str) -> Optional[ModelDict]:
        raise NotImplementedError

    def delete(self, key: str):
        raise NotImplementedError

    def save_dict(self, key: str, data: ModelDict):
        raise NotImplementedError

    def get_all(self) -> List[str]:
        raise NotImplementedError
