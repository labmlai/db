.. image:: https://badge.fury.io/py/labml_db.svg
    :target: https://badge.fury.io/py/labml_db
.. image:: https://pepy.tech/badge/labml_db
    :target: https://pepy.tech/project/labml_db

LabML DB
========

LabML DB is a minimalistic ORM database that uses JSON, YAML or Pickle files.
It uses Python typehints as much as possible to help with static checking,
and IDE features like autocompletion.

You can install this package using PIP.

.. code-block:: console

    pip install labml_db


Example
^^^^^^^

.. code-block:: python

    from labml_db import Model, Index


    class Project(Model['Project']):
        name: str
        experiments: int

        @classmethod
        def defaults(cls):
            return dict(name='', experiments=0)


    class User(Model['User']):
        name: str
        projects: List[Key[Project]]
        # This is an optional property, will automatically default to None
        occupation: Optional[str]

        @classmethod
        def defaults(cls):
            # Name is not in defaults and not optional.
            # It will be considered a required property
            return dict(projects=[])


    class UsernameIndex(Index['User']):
        pass

You can configure it to use JSON/YAML/Pickle files

.. code-block:: python

    Model.set_db_drivers([
        FileDbDriver(PickleSerializer(), User, Path('./data/user')),
        FileDbDriver(YamlSerializer(), Project, Path('./data/project'))
    ])
    Index.set_db_drivers([
        FileIndexDbDriver(JsonSerializer(), UsernameIndex, Path('./data/UserNameIndex.yaml'))
    ])

You can user `get_all` and `Key.load` to retrieve models, and `save` to save models.

.. code-block:: python

    proj = Project(name='nlp')
    user = User(name='John')
    user.projects.append(proj.key)
    user.occupation = 'test'
    user.save()
    proj.save()

    keys = User.get_all()
    print([k.load() for k in keys])
    keys = Project.get_all()
    print([k.load() for k in keys])

And index is a hash-map between strings and keys.

.. code-block:: python

    user_key = UsernameIndex.get('John')
    if not user_key:
        user = User(name='John')
        user.save()
        UsernameIndex.set(user.name, user.key)
    else:
        print(user_key.load())
