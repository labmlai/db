import copy
import warnings
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


from typing import Generic


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
    __db_drivers: Dict[str, 'DbDriver']
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
        Model.__db_drivers = {d.model_name: d for d in db_drivers}

    @classmethod
    def load(cls, key: str) -> Optional[_KT]:
        model_name = key.split(':')[0]
        db_driver = Model.__db_drivers[model_name]
        data = db_driver.load_dict(key)
        if data is None:
            return None
        return Model.from_dict(key, data)

    @staticmethod
    def delete_by_key(key: str):
        model_name = key.split(':')[0]
        db_driver = Model.__db_drivers[model_name]
        db_driver.delete(key)

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

    def delete(self):
        db_driver = Model.__db_drivers[self.__class__.__name__]
        db_driver.delete(self._key)

    def __repr__(self):
        kv = [f'{k}={repr(v)}' for k, v in self._values.items()]
        kv = ', '.join(kv)
        return f'{self.__class__.__name__}({kv})'
