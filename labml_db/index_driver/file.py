from pathlib import Path
from typing import Dict, Type, Optional, TYPE_CHECKING

from . import IndexDbDriver

if TYPE_CHECKING:
    from .. import Index
    from .. import Serializer


class FileIndexDbDriver(IndexDbDriver):
    _cache: Optional[Dict[str, str]]

    def __init__(self, serializer: 'Serializer', index_cls: Type['Index'], index_path: Path):
        super().__init__(index_cls)
        self._serializer = serializer
        self._index_path = index_path
        self._cache = None
        if not index_path.parent.exists():
            index_path.parent.mkdir(parents=True)

    def _load_cache(self):
        if self._cache is not None:
            return

        try:
            with open(str(self._index_path), 'r') as f:
                self._cache = self._serializer.from_string(f.read())
        except FileNotFoundError:
            self._cache = {}

    def _save_cache(self):
        with open(str(self._index_path), 'w') as f:
            f.write(self._serializer.to_string(self._cache))

    def delete(self, index_key: str):
        self._load_cache()
        if index_key in self._cache:
            del self._cache[index_key]
            self._save_cache()

    def get(self, index_key: str) -> str:
        self._load_cache()
        return self._cache.get(index_key, None)

    def set(self, index_key: str, model_key: str):
        self._load_cache()
        self._cache[index_key] = model_key
        self._save_cache()
