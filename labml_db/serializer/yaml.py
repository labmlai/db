
from . import Serializer
from .utils import encode_keys, decode_keys
from ..types import ModelDict


class YamlSerializer(Serializer):
    file_extension = 'yaml'

    def to_string(self, data: ModelDict) -> str:
        import yaml
        return yaml.dump(encode_keys(data), default_flow_style=False)

    def from_string(self, data: str) -> ModelDict:
        import yaml
        return decode_keys(yaml.load(data, Loader=yaml.FullLoader))
