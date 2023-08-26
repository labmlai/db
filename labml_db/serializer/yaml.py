from typing import Optional

from . import Serializer
from .utils import encode_keys, decode_keys
from ..types import ModelDict


class YamlSerializer(Serializer):
    file_extension = 'yaml'

    def to_string(self, data: ModelDict) -> str:
        import yaml
        assert data
        return yaml.dump(encode_keys(data), default_flow_style=False)

    def from_string(self, data: Optional[str]) -> Optional[ModelDict]:
        if data is None:
            return None
        import yaml
        return decode_keys(yaml.load(data, Loader=yaml.FullLoader))
