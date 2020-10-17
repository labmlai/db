import copy
import json
import warnings
from pathlib import Path
from typing import Generic, TypeVar, List, Dict, Union, Type, Set, Optional

Primitive = Union[Dict[str, 'Primitive'], List['Primitive'], int, str, float, bool, None]
ModelDict = Dict[str, Primitive]


def generate_uuid() -> str:
    from uuid import uuid1
    return uuid1().hex


class Serializer:
    file_extension = 'data'

    def to_string(self, data: ModelDict) -> str:
        raise NotImplementedError

    def from_string(self, data: str) -> ModelDict:
        raise NotImplementedError


class DbDriver:
    def __init__(self, serializer: Serializer, model_cls: Type['Model']):
        self.model_name = model_cls.__name__
        self._serializer = serializer

    def load_dict(self, key: str):
        raise NotImplementedError

    def delete(self, key: str):
        raise NotImplementedError

    def save_dict(self, key: str, data: ModelDict):
        raise NotImplementedError

    def get_all(self) -> List[str]:
        raise NotImplementedError


def _encode_keys(data: Primitive):
    if isinstance(data, Key):
        return {'__key__': str(data)}
    elif isinstance(data, list):
        return [_encode_keys(d) for d in data]
    elif isinstance(data, dict):
        return {k: _encode_keys(v) for k, v in data.items()}
    else:
        return data


def _decode_keys(data: Primitive):
    if isinstance(data, dict) and '__key__' in data:
        return Key(data['__key__'])
    elif isinstance(data, list):
        return [_decode_keys(d) for d in data]
    elif isinstance(data, dict):
        return {k: _decode_keys(v) for k, v in data.items()}
    else:
        return data


class JsonSerializer(Serializer):
    file_extension = 'json'

    def to_string(self, data: ModelDict) -> str:
        return json.dumps(_encode_keys(data))

    def from_string(self, data: str) -> ModelDict:
        return _decode_keys(json.loads(data))


class YamlSerializer(Serializer):
    file_extension = 'yaml'

    def to_string(self, data: ModelDict) -> str:
        import yaml
        return yaml.dump(_encode_keys(data), default_flow_style=False)

    def from_string(self, data: str) -> ModelDict:
        import yaml
        return _decode_keys(yaml.load(data, Loader=yaml.FullLoader))


class FileDbDriver(DbDriver):
    def __init__(self, serializer: Serializer, model_cls: Type['Model'], db_path: Path):
        super().__init__(serializer, model_cls)
        self._db_path = db_path
        if not db_path.exists():
            db_path.mkdir(parents=True)

    def load_dict(self, key: str) -> ModelDict:
        path = self._db_path / f'{key}.{self._serializer.file_extension}'
        with open(str(path), 'r') as f:
            return self._serializer.from_string(f.read())

    def save_dict(self, key: str, data: ModelDict):
        path = self._db_path / f'{key}.{self._serializer.file_extension}'
        with open(str(path), 'w') as f:
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


_KT = TypeVar('_KT')


def _get_base_classes(class_: Type['Model']) -> List[Type['Model']]:
    classes = [class_]
    level = [class_]
    next_level = []

    while len(level) > 0:
        for c in level:
            for b in c.__bases__:
                if b == object:
                    continue
                if b == Generic:
                    continue
                next_level.append(b)
        classes += next_level
        level = next_level
        next_level = []

    classes.reverse()

    unique_classes = []
    hashes: Set[int] = set()
    for c in classes:
        if hash(c) not in hashes:
            unique_classes.append(c)
        hashes.add(hash(c))

    return unique_classes


DB_CONFIGS = {
    'User': 'redis'
}


class ModelSpec:
    def __init__(self, model_cls: Type['Model']):
        classes = _get_base_classes(model_cls)
        self.annotations = {}
        self._defaults = []
        self.model_cls = model_cls
        self.name = model_cls.__name__
        for c in classes:
            for k, v in c.__annotations__.items():
                self.annotations[k] = v

            if 'defaults' in c.__dict__:
                self._defaults.append(c)

    def defaults(self) -> Dict[str, Primitive]:
        defaults = {}
        for d in self._defaults:
            defaults.update(d.defaults())

        for k in self.annotations:
            if k[0] == '_':
                continue
            if k not in defaults:
                raise ValueError(f'Missing default {self.model_cls.__name__}:{k}')

        return defaults


class Model(Generic[_KT]):
    __models: Dict[str, ModelSpec] = {}
    __db_drivers: Dict[str, DbDriver]
    _defaults = Dict[str, Primitive]
    _values = Dict[str, Primitive]

    def __init__(self, key: Optional[str] = None, **kwargs):
        model_cls: ModelSpec = Model.__models[self.__class__.__name__]

        if key is None:
            key = f'{model_cls.name}:{generate_uuid()}'
        else:
            if key.split(':')[0] != model_cls.name:
                raise RuntimeError(f'{key} does not match {self.__class__}')

        self._key = key
        self._values = {}
        self._defaults = model_cls.defaults()

        for k, v in kwargs.items():
            setattr(self, k, v)

    def __init_subclass__(cls, **kwargs):
        if cls.__name__ in Model.__models:
            warnings.warn(f"{cls.__name__} already used")

        Model.__models[cls.__name__] = ModelSpec(cls)

    @classmethod
    def get_all(cls) -> List['Key[_KT]']:
        db_driver = Model.__db_drivers[cls.__name__]
        keys = db_driver.get_all()
        return [Key(k) for k in keys]

    def __setattr__(self, key: str, value: Primitive):
        if key[0] == '_':
            self.__dict__[key] = value
            return

        model_cls: ModelSpec = Model.__models[self.__class__.__name__]
        if key not in model_cls.annotations:
            raise ValueError(f'Unknown property {key}')

        self._values[key] = value

    def update(self, data: ModelDict):
        for k, v in data.items():
            setattr(self, k, v)

    def __getattr__(self, key: str):
        model_cls: ModelSpec = Model.__models[self.__class__.__name__]
        if key not in model_cls.annotations:
            raise ValueError(f'Unknown property {key}')

        if key not in self._values:
            self._values[key] = copy.deepcopy(self._defaults[key])

        return self._values[key]

    @classmethod
    def defaults(cls):
        return {}

    @property
    def key(self) -> 'Key[_KT]':
        return Key(self._key)

    @staticmethod
    def set_db_drivers(db_drivers: List[DbDriver]):
        Model.__db_drivers = {d.model_name: d for d in db_drivers}

    @classmethod
    def load(cls, key: str) -> _KT:
        model_name = key.split(':')[0]
        db_driver = Model.__db_drivers[model_name]
        data = db_driver.load_dict(key)
        return Model.from_dict(key, data)

    @staticmethod
    def delete_by_key(key: str):
        model_name = key.split(':')[0]
        db_driver = Model.__db_drivers[model_name]
        db_driver.delete(key)

    def to_dict(self) -> ModelDict:
        return self._values

    @classmethod
    def from_dict(cls, key: str, data: ModelDict) -> _KT:
        model_name = key.split(':')[0]
        model = Model.__models[model_name].model_cls(key)
        model.update(data)
        return model

    def save(self):
        db_driver = Model.__db_drivers[self.__class__.__name__]
        db_driver.save_dict(self._key, self.to_dict())

    def delete(self):
        db_driver = Model.__db_drivers[self.__class__.__name__]
        db_driver.delete(self._key)

    def __repr__(self):
        kv = [f'{k}={repr(v)}' for k, v in self._values.items()]
        kv = ', '.join(kv)
        return f'{self.__class__.__name__}({kv})'


class IndexDbDriver:
    def __init__(self, index_cls: Type['Index']):
        self.index_name = index_cls.__name__

    def delete(self, index_key: str):
        raise NotImplementedError

    def get(self, index_key: str) -> str:
        raise NotImplementedError

    def set(self, index_key: str, model_key: str):
        raise NotImplementedError


class FileIndexDbDriver(IndexDbDriver):
    _cache: Optional[Dict[str, str]]

    def __init__(self, serializer: Serializer, index_cls: Type['Index'], index_path: Path):
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


class Index(Generic[_KT]):
    __db_drivers: Dict[str, IndexDbDriver]

    @staticmethod
    def set_db_drivers(db_drivers: List[IndexDbDriver]):
        Index.__db_drivers = {d.index_name: d for d in db_drivers}

    @classmethod
    def delete(cls, index_key: str):
        db_driver = Index.__db_drivers[cls.__name__]
        db_driver.delete(index_key)

    @classmethod
    def get(cls, index_key: str) -> Optional['Key[_KT]']:
        db_driver = Index.__db_drivers[cls.__name__]
        key = db_driver.get(index_key)
        if key is None:
            return None
        else:
            return Key(key)

    @classmethod
    def set(cls, index_key: str, model_key: 'Key[_KT]'):
        db_driver = Index.__db_drivers[cls.__name__]
        db_driver.set(index_key, str(model_key))


class Key(Generic[_KT]):
    _key: str

    def __init__(self, key: str):
        self._key = key

    def __str__(self):
        return self._key

    def load(self) -> _KT:
        return Model.load(self._key)

    def delete(self):
        return Model.delete_by_key(self._key)

    def __repr__(self):
        return f'Key({self._key})'
