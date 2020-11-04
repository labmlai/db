from pathlib import Path
from typing import List

from labml import monit, logger

from labml_db import Model
from labml_db.driver.file import FileDbDriver
from labml_db.serializer.json import JsonSerializer
from labml_db.serializer.pickle import PickleSerializer
from labml_db.serializer.yaml import YamlSerializer


class YamlModel(Model['YamlModel']):
    data: List[float]

    @classmethod
    def defaults(cls):
        return dict(data=[])


class JsonModel(Model['JsonModel']):
    data: List[float]

    @classmethod
    def defaults(cls):
        return dict(data=[])


class PickleModel(Model['PickleModel']):
    data: List[float]

    @classmethod
    def defaults(cls):
        return dict(data=[])


class BsonModel(Model['BsonModel']):
    data: List[float]

    @classmethod
    def defaults(cls):
        return dict(data=[])


def test_setup():
    Model.set_db_drivers([
        FileDbDriver(PickleSerializer(), PickleModel, Path('./data/pickle')),
        FileDbDriver(JsonSerializer(), JsonModel, Path('./data/json')),
        FileDbDriver(YamlSerializer(), YamlModel, Path('./data/yaml')),
    ])


def test(is_yaml, is_json, is_pickle, length, n):
    data = [i * 0.5 - 1e-7 for i in range(length)]
    if is_yaml:
        with monit.section('YAML save'):
            for i in range(n):
                m = YamlModel(data=data)
                m.save()
    if is_pickle:
        with monit.section('Pickle save'):
            for i in range(n):
                m = PickleModel(data=data)
                m.save()
    if is_json:
        with monit.section('JSON save'):
            for i in range(n):
                m = JsonModel(data=data)
                m.save()

    if is_yaml:
        with monit.section('YAML Load'):
            keys = YamlModel.get_all()
            m = [k.load() for k in keys]
            logger.log(f'{len(m)}')
    if is_json:
        with monit.section('JSON Load'):
            keys = JsonModel.get_all()
            m = [k.load() for k in keys]
            logger.log(f'{len(m)}')
    if is_pickle:
        with monit.section('Pickle Load'):
            keys = PickleModel.get_all()
            m = [k.load() for k in keys]
            logger.log(f'{len(m)}')


if __name__ == '__main__':
    test_setup()
    # test(True, True, True, 1000, 100)
    test(False, True, True, 1000_000, 10)
    # test(False, True, True, 100_000, 100)
    # test(False, True, True, 10_000, 1000)
