from typing import Dict, Type, Optional, TYPE_CHECKING, List

from . import IndexDbDriver

if TYPE_CHECKING:
    import pymongo
    from .. import Index


class MongoIndexDbDriver(IndexDbDriver):
    _cache: Optional[Dict[str, str]]

    def __init__(self, index_cls: Type['Index'], db: 'pymongo.mongo_client.database.Database'):
        super().__init__(index_cls)
        self._index = db[f'_index_{self.index_name}']

    def delete(self, index_key: str):
        self._index.delete_one({'_id': index_key})

    def get(self, index_key: str) -> Optional[str]:
        d = self._index.find_one({'_id': index_key})
        if d is None:
            return None
        return d['value']

    def mget(self, index_key: List[str]) -> List[Optional[str]]:
        cursor = self._index.find({'_id': {'$in': index_key}})
        res = [None for _ in index_key]
        idx = {k: i for i, k in enumerate(index_key)}
        for d in cursor:
            i = idx[d['_id']]
            res[i] = d['value']

        return res

    def set(self, index_key: str, model_key: str):
        self._index.replace_one({'_id': index_key}, {'_id': index_key, 'value': model_key}, True)

    def get_all(self):
        cur = self._index.find()
        return [d['value'] for d in cur]
