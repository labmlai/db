from typing import Union, Optional

from ..types import ModelDict


class Serializer:
    file_extension = 'data'
    is_bytes = False

    def to_string(self, data: ModelDict) -> Union[str, bytes]:
        raise NotImplementedError

    def from_string(self, data: Union[str, bytes, None]) -> Optional[ModelDict]:
        raise NotImplementedError
