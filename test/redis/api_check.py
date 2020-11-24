import redis

from labml.logger import inspect

r = redis.Redis(host='localhost', port=6379, db=0)
inspect(r.set('foo', 'bar'))
inspect(r.get('foo'))
