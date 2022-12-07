from typing import List, Type, TYPE_CHECKING, Optional, Tuple

from ..types import ModelDict, QueryDict, SortDict

if TYPE_CHECKING:
    from .. import Serializer, Model


class DbDriver:
    def __init__(self, serializer: Optional['Serializer'], model_cls: Type['Model']):
        self.model_name = model_cls.__name__
        self._serializer = serializer

    def load_dict(self, key: str) -> Optional[ModelDict]:
        raise NotImplementedError

    def mload_dict(self, key: List[str]) -> List[Optional[ModelDict]]:
        raise NotImplementedError

    def delete(self, key: str):
        raise NotImplementedError

    def save_dict(self, key: str, data: ModelDict):
        raise NotImplementedError

    def msave_dict(self, key: List[str], data: List[ModelDict]):
        raise NotImplementedError

    def get_all(self) -> List[str]:
        raise NotImplementedError

    def search(self, text_query: Optional[str], filters: Optional[QueryDict], sort: Optional[SortDict],
               randomize: bool = False, limit: Optional[int] = None, sort_by_text_score: bool = False) -> Tuple[
        List[Tuple[str, ModelDict]], int]:
        raise NotImplementedError
