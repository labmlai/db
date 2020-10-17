from pathlib import Path
from typing import List

from labml_db import Model, Key, Index, FileDbDriver, JsonSerializer, YamlSerializer, FileIndexDbDriver


class Project(Model['Project']):
    name: str
    experiments: int

    @classmethod
    def defaults(cls):
        return dict(name='', experiments=0)


class User(Model['User']):
    name: str
    projects: List[Key[Project]]

    @classmethod
    def defaults(cls):
        return dict(name='', projects=[])


class UsernameIndex(Index['User']):
    pass


def test_setup():
    Model.set_db_drivers([
        FileDbDriver(JsonSerializer(), User, Path('./data/user')),
        FileDbDriver(YamlSerializer(), Project, Path('./data/project'))
    ])
    Index.set_db_drivers([
        FileIndexDbDriver(YamlSerializer(), UsernameIndex, Path('./data/UserNameIndex.yaml'))
    ])


def test():
    proj = Project(name='nlp')
    user = User(name='Varuna')
    user.name = 'Varuna'
    user.projects.append(proj.key)
    user2 = User(name='X')
    print(user.projects, user2.projects)
    user.save()
    proj.save()

    print(user.projects[0].load().name)


def test_load():
    keys = User.get_all()
    print([k.load() for k in keys])
    keys = Project.get_all()
    print([k.load().name for k in keys])


def test_index():
    user_key = UsernameIndex.get('Varuna')
    if user_key:
        user_key.delete()

    user = User()
    user.name = 'Varuna'
    user.save()
    UsernameIndex.set(user.name, user.key)

    print(user.key, user.name, user.projects)


if __name__ == '__main__':
    test_setup()
    test()
    test_load()
    test_index()
