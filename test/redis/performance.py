import redis

from labml_db import Model
from labml_db.driver.redis import RedisDbDriver
from labml_db.serializer.json import JsonSerializer
from labml_db.serializer.pickle import PickleSerializer
from labml_db.serializer.yaml import YamlSerializer
from test.performance import PickleModel, JsonModel, YamlModel, test


def test_setup():
    db = redis.Redis(host='localhost', port=6379, db=0)
    Model.set_db_drivers([
        RedisDbDriver(PickleSerializer(), PickleModel, db),
        RedisDbDriver(JsonSerializer(), JsonModel, db),
        RedisDbDriver(YamlSerializer(), YamlModel, db),
    ])


if __name__ == '__main__':
    test_setup()
    # test(True, True, True, 1000, 100)
    test(False, True, True, 1000_000, 10)
    # test(False, True, True, 100_000, 100)
    # test(False, True, True, 10_000, 1000)
