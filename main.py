import os
import sys

import pymongo

from pymongo import MongoClient

from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired

from program_settings import ProgramSettings


def get_python_version() -> str:
    return f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"


def get_connection_string() -> str:
    template: str = ProgramSettings.get_setting('mongodb_connection_template')
    uid: str = ProgramSettings.get_setting('mongodb_uid')
    pwd: str = ProgramSettings.get_setting('mongodb_pwd')

    conn_string = f'mongodb+srv://{uid}:{pwd}@{template}'
    print(f'{conn_string=}')
    return conn_string


def get_mongodb_client() -> MongoClient:
    # print(f'{get_connection_string()=}')
    return MongoClient(get_connection_string())


def verify_mongodb_connection_works():
    client: MongoClient = get_mongodb_client()
    print(f'{client=}')


def verify_mongodb_database():
    print('DEBUG: top of verify_mongodb_database')
    client: MongoClient = get_mongodb_client()
    print(f'{client=}')
    # print('Trying to look at a specific database')
    db = client['sample_restaurants']
    print(f'{db=}')
    print('looping through all client database names')
    for db_info in client.list_database_names():
        print(f'{db_info=}')

    print('DEBUG: bottom of verify_mongodb_database')


def get_pymongo_version() -> str:
    return pymongo.get_version_string()


def get_mongodb_version() -> str:
    client: MongoClient = get_mongodb_client()
    db = client['user_shopping_list']
    result = db.command( {'buildInfo': 1 } )
    # print(f'db.command("buildInfo") {result=}')
    version: str = result.get('version')
    # print(f'{version=}')
    return version


def display_mongodb_collections():
    print('DEBUG: top of display_mongodb_collections')
    client = get_mongodb_client()
    # db = client['sample_mflix']
    databases = client.list_database_names()
    print(f'{databases=}')
    # print(f'{db.name=}')
    # List all the collections in 'sample_mflix':
    collections = db.list_collection_names()
    print(f'{type(collections)=}')
    debug: bool = True
    for collection in collections:
        if debug:
            debug = False
            print(f'{type(collection)=}')
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
    print(f'{user_properties=}')

    for doc in documents:
        for field_name, value in doc.items():
            # Some smart recognition can be here
            field_definition = StringField()
            user_properties[field_name] = field_definition

    '''
    # Your new class for MongoEngine:
    User = type("User", (Document,), user_properties)

    users = User.objects(email__endswith='.com')
    print(users)
    '''


def display_american_cuisine_restaurants():
    client = get_mongodb_client()
    # fetch a list of restaurants that specialize in American cuisine,
    # sorted by restaurant name.
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


def main():
    verify_mongodb_connection_works()
    # FAILS as of 2025-01-09    display_mongodb_collections()
    # FAILS as of 2025-01-09    display_american_cuisine_restaurants()
    verify_mongodb_database()
    # create_schema()
    get_mongodb_version()

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


if __name__ == '__main__':
    print(f'Python version: {get_python_version()}')
    print(f'MongoDB Atlas version: {get_mongodb_version()}')
    main()
