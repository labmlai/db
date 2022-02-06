from labml import monit
from labml.logger import inspect
from pymongo import MongoClient

CONNECTION_STRING = "mongodb://localhost:27017/"


def get_database():
    client = MongoClient(CONNECTION_STRING)

    inspect(client)
    # inspect(client.server_info())
    inspect(client.list_database_names())

    # client.drop_database('papers')

    return client['papers']


def test():
    db = get_database()
    inspect(db)
    collection = db['papers']
    inspect(collection)

    with monit.section('Insert'):
        paper_1 = {
            "_id": "abcd",
            "title": "Attention is all you need",
            "abstract": "abstract"
        }

        collection.insert_many([paper_1])

    with monit.section('Find'):
        item_details = collection.find()
        for item in item_details:
            inspect(type(item))
            inspect(item)


if __name__ == "__main__":
    test()
