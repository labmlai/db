import json

from . import Serializer
from .utils import encode_keys, decode_keys
from ..types import ModelDict


class JsonSerializer(Serializer):
    file_extension = 'json'

    def to_string(self, data: ModelDict) -> str:
        return json.dumps(encode_keys(data))

    def from_string(self, data: str) -> ModelDict:
        return decode_keys(json.loads(data))
