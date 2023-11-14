from collections import OrderedDict
from typing import List, Type, TYPE_CHECKING, Optional, Dict, Tuple, OrderedDict

import pymongo

from ..serializer.utils import encode_keys, decode_keys
from . import DbDriver
from ..types import ModelDict, QueryDict, SortDict

if TYPE_CHECKING:
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

    def search(self, text_query: Optional[str], filters: Optional[QueryDict], sort: Optional[SortDict],
               randomize: bool = False, limit: Optional[int] = None, sort_by_text_score: bool = False) -> Tuple[
        List[Tuple[str, ModelDict]], int]:
        pipeline = []

        match = dict()
        if filters:
            for property_name, item in filters.items():
                value, equal = item
                if equal:
                    match[property_name] = value
                else:
                    match[property_name] = {'$ne': value}
        if text_query:
            match['$text'] = {'$search': text_query}
        if len(match) > 0:
            pipeline.append({'$match': match})

        if randomize:
            pipeline.append({'$facet': {'data': [{'$sample': {'size': limit}}], 'count': [{'$count': 'count'}]}})
        else:
            sort_query = OrderedDict()
            if sort_by_text_score:
                sort_query['score'] = {'$meta': 'textScore'}
            if sort is not None and len(sort) > 0:
                for k, v in sort:
                    sort_query[k] = pymongo.ASCENDING if v else pymongo.DESCENDING
            
            if len(sort_query) > 0:
                pipeline.append({'$sort': sort_query})

            if limit:
                pipeline.append({'$facet': {'data': [{'$limit': limit}], 'count': [{'$count': 'count'}]}})

        cursor = self._collection.aggregate(pipeline)
        res = []
        count = 0
        if limit:
            for item in cursor:
                for c in item['count']:
                    count += c['count']
                for d in item['data']:
                    res.append((d['_id'], self._load_data(d)))
        else:
            for d in cursor:
                res.append((d['_id'], self._load_data(d)))

            count = len(res)

        return res, count
