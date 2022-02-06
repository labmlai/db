from pymongo import MongoClient

from labml_db import Model, Index
from labml_db.driver.mongo import MongoDbDriver
from labml_db.index_driver.mongo import MongoIndexDbDriver
from test.simple import User, Project, UsernameIndex


def test_setup():
    db = MongoClient("mongodb://localhost:27017/")['testdb']
    Model.set_db_drivers([
        MongoDbDriver(User, db),
        MongoDbDriver(Project, db)
    ])
    Index.set_db_drivers([
        MongoIndexDbDriver(UsernameIndex, db)
    ])


def test():
    proj = Project(name='nlp')
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
    print([k.load().name for k in keys])


def test_index():
    user_key = UsernameIndex.get('John')
    if user_key:
        print('index', user_key.load())
        user_key.delete()

    user = User(name='John')
    user.save()
    UsernameIndex.set(user.name, user.key)

    print(user.key, user.name, user.projects)


if __name__ == '__main__':
    test_setup()
    test()
    test_load()
    test_index()
