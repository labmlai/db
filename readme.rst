.. image:: https://badge.fury.io/py/labml_db.svg
    :target: https://badge.fury.io/py/labml_db
.. image:: https://pepy.tech/badge/labml_db
    :target: https://pepy.tech/project/labml_db

LabML DB
========

LabML DB is a simple ORM database that uses JSON and YAML files.

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

        @classmethod
        def defaults(cls):
            return dict(name='', projects=[])


    class UsernameIndex(Index['User']):
        pass

You can configure it to use JSON/YAML files

.. code-block:: python

    Model.set_db_drivers([
        FileDbDriver(JsonSerializer(), 'User', Path('./data/user')),
        FileDbDriver(YamlSerializer(), 'Project', Path('./data/project'))
    ])
    Index.set_db_drivers([
        FileIndexDbDriver(YamlSerializer(), 'UsernameIndex', Path('./data/UserNameIndex.yaml'))
    ])
