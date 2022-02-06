from typing import List, Type, TYPE_CHECKING, Optional, Dict

from labml_db.serializer.utils import encode_keys, decode_keys

from . import DbDriver
from ..types import ModelDict

if TYPE_CHECKING:
    import pymongo
    from ..model import Model


class MongoDbDriver(DbDriver):
    def __init__(self, model_cls: Type['Model'], db: 'pymongo.mongo_client.database.Database'):
        super().__init__(None, model_cls)
        self._collection = db[self.model_name]

    def _to_obj_id(self, key: str):
        return str(key)
        # return ObjectId(key.split(':')[1])

    def _to_key(self, mongo_id: any):
        # self.model_name + ':' + str(d['_id']
        return mongo_id

    def _load_data(self, data: ModelDict):
        if data is None:
            return None
        del data['_id']
        return decode_keys(data)

    def _dump_data(self, key: str, data: ModelDict):
        d: Dict = data.copy()
        d = encode_keys(d)
        d['_id'] = self._to_obj_id(key)

        return d

    def mload_dict(self, key: List[str]) -> List[Optional[ModelDict]]:
        obj_keys = [self._to_obj_id(k) for k in key]
        cursor = self._collection.find({'_id': {'$in': obj_keys}})
        res = [None for _ in key]
        idx = {k: i for i, k in enumerate(obj_keys)}
        for d in cursor:
            i = idx[d['_id']]
            res[i] = self._load_data(d)

        return res

    def load_dict(self, key: str) -> Optional[ModelDict]:
        d = self._collection.find_one({'_id': self._to_obj_id(key)})
        return self._load_data(d)

    def msave_dict(self, key: List[str], data: List[ModelDict]):
        objs = [self._dump_data(k, d) for k, d in zip(key, data)]

        from pymongo import ReplaceOne
        replacements = [ReplaceOne({'_id': d['_id']}, d, True) for d in objs]
        self._collection.bulk_write(replacements, False)

    def save_dict(self, key: str, data: ModelDict):
        obj = self._dump_data(key, data)

        self._collection.replace_one({'_id': obj['_id']}, obj, True)

    def delete(self, key: str):
        self._collection.delete_one({'_id': self._to_obj_id(key)})

    def get_all(self) -> List[str]:
        cur = self._collection.find(projection=['_id'])
        keys = [self._to_key(d['_id']) for d in cur]
        return keys
