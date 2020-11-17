import fcntl
from pathlib import Path
from typing import List, Type, TYPE_CHECKING, Optional

from . import DbDriver
from ..types import ModelDict

if TYPE_CHECKING:
    from .. import Serializer
    from ..model import Model


class FileDbDriver(DbDriver):
    def __init__(self, serializer: 'Serializer', model_cls: Type['Model'], db_path: Path):
        super().__init__(serializer, model_cls)
        self._db_path = db_path
        if not db_path.exists():
            db_path.mkdir(parents=True)

    def load_dict(self, key: str) -> Optional[ModelDict]:
        path = self._db_path / f'{key}.{self._serializer.file_extension}'
        if not path.exists():
            return None

        if self._serializer.is_bytes:
            with open(str(path), 'rb') as f:
                fcntl.lockf(f, fcntl.LOCK_SH)
                return self._serializer.from_string(f.read())
        else:
            with open(str(path), 'r') as f:
                fcntl.lockf(f, fcntl.LOCK_SH)
                return self._serializer.from_string(f.read())

    def save_dict(self, key: str, data: ModelDict):
        path = self._db_path / f'{key}.{self._serializer.file_extension}'
        if self._serializer.is_bytes:
            with open(str(path), 'wb') as f:
                fcntl.lockf(f, fcntl.LOCK_EX)
                return f.write(self._serializer.to_string(data))
        else:
            with open(str(path), 'w') as f:
                fcntl.lockf(f, fcntl.LOCK_EX)
                return f.write(self._serializer.to_string(data))

    def delete(self, key: str):
        path = self._db_path / f'{key}.{self._serializer.file_extension}'
        path.unlink()

    def get_all(self) -> List[str]:
        keys = []
        for file in self._db_path.iterdir():
            name = file.stem
            if name.split(':')[0] != self.model_name:
                continue
            keys.append(name)

        return keys
