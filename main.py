import os
import sys

import pymongo
from dotenv import load_dotenv
from pymongo import MongoClient

from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired


def get_python_version() -> str:
    return f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"


def get_connection_string() -> str:
    load_dotenv()
    template: str = os.environ.get('mongodb_connection_template')
    uid: str = os.environ.get('mongodb_uid')
    pwd: str = os.environ.get('mongodb_pwd')

    return f'mongodb+srv://{uid}:{pwd}@{template}'


def get_mongodb_client() -> MongoClient:
    print(f'{get_connection_string()=}')
    return MongoClient(get_connection_string())


def verify_mongodb_connection_works():
    client: MongoClient = get_mongodb_client()
    print(f'{client=}')


def verify_mongodb_database():
    client: MongoClient = get_mongodb_client()
    print(f'{client=}')
    db = client['user_shopping_list']
    print(f'{db=}')

    # FAILS with bad auth error - not sure why: db = client.list_databases()
    for db_info in client.list_database_names():
        print(db_info)


def get_pymongo_version() -> str:
    return pymongo.get_version_string()


def get_mongodb_version() -> str:
    client: MongoClient = get_mongodb_client()
    db = client['user_shopping_list']
    # FAILS: result = db.command('new Document("buildInfo', 1)
    result = db.command("dbstats")
    print(f'{result=}')
    return 'pass'


def display_mongodb_collections():
    print('DEBUG: top of display_mongodb_collections')
    client = get_mongodb_client()
    db = client['sample_mflix']
    print(f'{db.name=}')
    # List all the collections in 'sample_mflix':
    collections = db.list_collection_names()
    for collection in collections:
        print(f'\t{collection=}')
    print('DEBUG: bottom of display_mongodb_collections')

def create_schema():
    client = get_mongodb_client()
    # ['sample_restaurants']
    db = client['sample_restaurants']
    documents = db['restaurants'].find()

    user_properties = {
        # Example of structure:
        # '_id': StringField(required=False),
        # 'name': StringField(required=False),
        # 'email': StringField(required=False),
    }
    for doc in documents:
        for field_name, value in doc.items():
            # Some smart recognition can be here
            field_definition = StringField(required=False)

            user_properties[field_name] = field_definition
    print(f'{user_properties}')
    '''
    # Your new class for MongoEngine:
    User = type("User", (Document,), user_properties)

    users = User.objects(email__endswith='.com')
    print(users)
    '''

def display_american_cuisine_restaurants():
    #from pymongo import MongoClient

    # Requires the PyMongo package.
    # https://api.mongodb.com/python/current

    client = get_mongodb_client()
    results = client['sample_restaurants']['restaurants'].aggregate([
        {
            '$match': {
                'cuisine': 'American'
            }
        }, {
            '$sort': {
                'name': 1
            }
        }, {
            '$project': {
                '_id': 0,
                'name': 1,
                'address.zipcode': 1,
                'borough': 1,
                'cuisine': 1
            }
        }
    ])
    # examine the results
    for result in results:
        # print(r)
        print(f"{result['name']=}\n\t{result['cuisine']=}\n\t{result['borough']=}\n\t{result['address']['zipcode']=}")


if __name__ == '__main__':
    print(f"Python version: {get_python_version()}")
    # verify_mongodb_connection_works()
    # display_mongodb_collections()
    display_american_cuisine_restaurants()
    create_schema()
    # get_mongodb_version()
    # HANGS: verify_mongodb_database()
    # FAILURES START HERE:
    # client = get_mongodb_client()
    # try to get MongoDB version number at runtime
    # FAILS print(f'{client.server_info()=}')
    # FAILS: print(f'{client.version()=}')
    # FAILS: version = client.server_info()["version"]
    # version = client.command({'buildInfo': 1})['version']
    # print(f'{version=}')
    # print(f'{get_pymongo_version()=}')

    print('DEBUG: end of program')
