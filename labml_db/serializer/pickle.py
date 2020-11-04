import pickle

from . import Serializer
from ..types import ModelDict


class PickleSerializer(Serializer):
    file_extension = 'pkl'
    is_bytes = True

    def to_string(self, data: ModelDict) -> bytes:
        return pickle.dumps(data)

    def from_string(self, data: bytes) -> ModelDict:
        return pickle.loads(data)
