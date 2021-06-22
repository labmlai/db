import json
from typing import Optional

from . import Serializer
from .utils import encode_keys, decode_keys
from ..types import ModelDict


class JsonSerializer(Serializer):
    file_extension = 'json'

    def to_string(self, data: ModelDict) -> str:
        return json.dumps(encode_keys(data))

    def from_string(self, data: Optional[str]) -> Optional[ModelDict]:
        if data is None:
            return None
        return decode_keys(json.loads(data))
