import copy
import warnings
from typing import Generic, Union
from typing import TypeVar, List, Dict, Type, Set, Optional, _GenericAlias, TYPE_CHECKING

from .types import Primitive, ModelDict

if TYPE_CHECKING:
    from .driver import DbDriver

_KT = TypeVar('_KT')


def generate_uuid() -> str:
    from uuid import uuid1
    return uuid1().hex


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


class Key(Generic[_KT]):
    _key: str

    def __init__(self, key: str):
        if type(key) == bytes:
            key = key.decode('utf-8')
        self._key = key

    def __str__(self):
        return self._key

    def __hash__(self):
        return hash(self._key)

    def __eq__(self, other: 'Key'):
        return str(self) == str(other)

    def load(self, db_driver: Optional['DbDriver'] = None) -> _KT:
        return Model.load(self._key, db_driver)

    def delete(self):
        return Model.delete_by_key(self._key)

    def save(self, data: ModelDict):
        return Model.save_by_key(self._key, data)

    def read(self, db_driver: Optional['DbDriver'] = None) -> ModelDict:
        return Model.read_dict(self._key, db_driver)

    def __repr__(self):
        return f'Key({self._key})'


class KeyList(Generic[_KT]):
    _keys: List[str]

    def __init__(self, key_list: Optional[List[Union[str, Key[_KT]]]] = None):
        if key_list is None:
            key_list = []
        self._keys = []
        for k in key_list:
            self.append(k)

    def append(self, key: Union[str, Key[_KT]]):
        if type(key) == bytes:
            self._keys.append(key.decode('utf-8'))
        elif type(key) == str:
            self._keys.append(key)
        else:
            self._keys.append(str(key))

    def __str__(self):
        return ', '.join(self._keys)

    # TODO: Implement these for multiple gets/sets on driver
    def load(self, db_driver: Optional['DbDriver'] = None) -> List[_KT]:
        return Model.mload(self._keys, db_driver)

    #
    # def delete(self):
    #     return [Model.delete_by_key(k) for k in self._keys]
    #
    # def save(self, data: List[ModelDict]):
    #     assert len(data) == len(self._keys)
    #     return [Model.save_by_key(k, d) for k, d in zip(self._keys, data)]
    #
    def read(self, db_driver: Optional['DbDriver'] = None) -> List[ModelDict]:
        return [Model.read_dict(k, db_driver) for k in self._keys]

    def __repr__(self):
        s = ', '.join(self._keys)
        return f'KeyList({s})'


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

        self.required = set()
        self.nones = set()
        self.check_defaults()

    def check_defaults(self):
        defaults = {}
        for d in self._defaults:
            defaults.update(d.defaults())

        for k, v in self.annotations.items():
            if k[0] == '_':
                continue
            if k not in defaults:
                # check for optional
                if isinstance(v, _GenericAlias):
                    if v._name is None and type(None) in v.__args__:
                        defaults[k] = None
                        self.nones.add(k)
            if k not in defaults:
                self.required.add(k)

        for k in defaults:
            if k not in self.annotations:
                raise ValueError(f'Unknown default {self.model_cls.__name__}:{k} = {defaults[k]}')

    def defaults(self) -> Dict[str, Primitive]:
        defaults = {k: None for k in self.nones}
        for d in self._defaults:
            defaults.update(d.defaults())

        return defaults


class Model(Generic[_KT]):
    __models: Dict[str, ModelSpec] = {}
    __db_drivers: Dict[str, 'DbDriver'] = {}
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

        for k in model_cls.required:
            if k not in kwargs:
                raise ValueError(f'Missing required value {self.__class__.__name__}:{k}')

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
    def set_db_drivers(db_drivers: List['DbDriver']):
        for d in db_drivers:
            Model.__db_drivers[d.model_name] = d

    @classmethod
    def mread_dict(cls, key: List[str], db_driver: Optional['DbDriver'] = None) -> List[ModelDict]:
        if not key:
            return []
        model_name = key[0].split(':')[0]
        if db_driver is None:
            db_driver = Model.__db_drivers[model_name]
        data = db_driver.mload_dict(key)

        return data

    @classmethod
    def read_dict(cls, key: str, db_driver: Optional['DbDriver'] = None) -> ModelDict:
        model_name = key.split(':')[0]
        if db_driver is None:
            db_driver = Model.__db_drivers[model_name]
        data = db_driver.load_dict(key)

        return data

    @staticmethod
    def _to_model(key: str, data: Optional[ModelDict]):
        return Model.from_dict(key, data) if data is not None else None

    @classmethod
    def load(cls, key: str, db_driver: Optional['DbDriver'] = None) -> Optional[_KT]:
        return Model._to_model(key, cls.read_dict(key, db_driver))

    @classmethod
    def mload(cls, key: List[str], db_driver: Optional['DbDriver'] = None) -> List[Optional[_KT]]:
        data = cls.mread_dict(key, db_driver)
        return [Model._to_model(k, d) for k, d in zip(key, data)]

    @staticmethod
    def delete_by_key(key: str):
        model_name = key.split(':')[0]
        db_driver = Model.__db_drivers[model_name]
        db_driver.delete(key)

    @staticmethod
    def save_by_key(key: str, data: ModelDict):
        model_name = key.split(':')[0]
        db_driver = Model.__db_drivers[model_name]
        db_driver.save_dict(key, data)

    def to_dict(self) -> ModelDict:
        values = {}
        for k, v in self._values.items():
            if k not in self._defaults or self._defaults[k] != v:
                values[k] = v
        return values

    @classmethod
    def from_dict(cls, key: str, data: ModelDict) -> _KT:
        model_name = key.split(':')[0]
        model = Model.__models[model_name].model_cls(key, **data)
        return model

    def save(self):
        db_driver = Model.__db_drivers[self.__class__.__name__]
        db_driver.save_dict(self._key, self.to_dict())

    @classmethod
    def msave(cls, models: List[_KT]):
        db_driver = Model.__db_drivers[cls.__name__]
        keys = [m._key for m in models]
        dicts = [m.to_dict() for m in models]
        db_driver.msave_dict(keys, dicts)

    def delete(self):
        db_driver = Model.__db_drivers[self.__class__.__name__]
        db_driver.delete(self._key)

    def __repr__(self):
        kv = [f'{k}={repr(v)}' for k, v in self._values.items()]
        kv = ', '.join(kv)
        return f'{self.__class__.__name__}({kv})'
