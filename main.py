import os
import sys

import pymongo
from dotenv import load_dotenv
from pymongo import MongoClient


def get_python_version() -> str:
    return f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"


def get_connection_string() -> str:
    load_dotenv()
    uid: str = os.environ.get('mongodb_uid')
    pwd: str = os.environ.get('mongodb_pwd')
    # WARNING: need to add authSource=admin for other useful commands to work
    return f'mongodb+srv://{uid}:{pwd}@pymongocluster.6sstkik.mongodb.net/?retryWrites=true&w=majority&appName=pymongoCluster&authSource=admin'


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


if __name__ == '__main__':
    print(f"Python version: {get_python_version()}")
    verify_mongodb_connection_works()
    display_mongodb_collections()
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
