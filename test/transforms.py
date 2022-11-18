from pathlib import Path
from typing import List, Optional, Set, Dict, Any

from labml_db import Model, Key
from labml_db.driver.file import FileDbDriver
from labml_db.serializer.pickle import PickleSerializer
from labml_db.serializer.yaml import YamlSerializer
from labml_db.types import ModelDict


class Project(Model['Project']):
    name: str
    experiments: Set[str]

    @classmethod
    def defaults(cls):
        return dict(name='', experiments=set())

    def to_dict_transform(self, data: Dict[str, Any]) -> ModelDict:
        print('Project to dict', self.__class__.__name__)
        data['experiments'] = list(data['experiments'])
        return data

    @classmethod
    def from_dict_transform(cls, data: ModelDict) -> Dict[str, Any]:
        print('Project from dict', cls.__name__)
        data: Dict[str, Any]
        if 'experiments' in data:
            val = data['experiments']
            assert type(val) == list
            data['experiments'] = set(val)
        return data


class User(Model['User']):
    name: str
    projects: List[Key[Project]]
    occupation: Optional[str]

    @classmethod
    def defaults(cls):
        return dict(projects=[])


def test_setup():
    Model.set_db_drivers([
        FileDbDriver(YamlSerializer(), User, Path('./data/user')),
        FileDbDriver(YamlSerializer(), Project, Path('./data/project'))
    ])


def test():
    proj = Project(name='nlp', experiments={'p1', 'p2'})
    user = User(name='John')
    user.projects.append(proj.key)
    user.occupation = 'test'
    user2 = User(name='X')
    print(user.projects, user2.projects)
    user.save()
    proj.save()

    print(user.projects[0].load().name)


def test_load():
    keys = User.get_all()
    print([k.load() for k in keys])
    keys = Project.get_all()
    print([k.load() for k in keys])


if __name__ == '__main__':
    test_setup()
    test()
    test_load()
