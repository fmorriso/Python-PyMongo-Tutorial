import sys
from importlib.metadata import version

import pymongo
from pymongo import MongoClient
from pymongo.synchronous.database import Database
from wtforms import StringField

from logging_utility import LoggingUtility as LU
from program_settings import ProgramSettings


def get_python_version() -> str:
    return f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"


def get_package_version(package_name: str) -> str:
    return version(package_name)


def get_connection_string() -> str:
    """
    Get a connection string for MongoDB using the key/values stored in the .env file.
    :return: a string containing the connection string.
    """
    template: str = ProgramSettings.get_setting('MONGODB_CONNECTION_TEMPLATE')
    uid: str = ProgramSettings.get_setting('MONGODB_UID')
    pwd: str = ProgramSettings.get_setting('MONGODB_PWD')

    conn_string = f'mongodb+srv://{uid}:{pwd}@{template}'
    msg = f'{conn_string=}'
    LU.debug(msg)
    return conn_string


def get_mongodb_client() -> MongoClient:
    """get a client connection to my personal MongoDB Atlas cluster using my personal userid and password"""
    connection_string: str = get_connection_string()
    connection: MongoClient = MongoClient(connection_string)
    return connection


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
        msg = f'{db_info=}'
        LU.info(msg)
        LU.debug(msg)

    LU.debug('DEBUG: bottom of verify_mongodb_database')


def get_pymongo_version() -> str:
    return pymongo.get_version_string()


def get_mongodb_version() -> str:
    """get a string containing the version of the MongoDB database we're using."""
    client: MongoClient = get_mongodb_client()
    db: Database = client['user_shopping_list']
    result: dict = db.command({'buildInfo': 1})
    key = 'version'
    version: str = 'unknown'
    if key in result.keys():
        version = result.get(key)
    # print(f'MongoDB {version=}')
    return version


def display_mongodb_collections():
    print('DEBUG: top of display_mongodb_collections')
    client = get_mongodb_client()
    # db = client['sample_mflix']
    databases = client.list_database_names()
    msg = f'{databases = }'
    LU.info(msg)
    LU.debug(msg)

    # print(f'{db.name=}')
    # List all the collections in 'sample_mflix':
    for db_info in client.list_database_names():
        msg = f'{db_info = }'
        LU.info(msg)
        LU.debug(msg)

    """
    collections = db.list_collection_names()
    print(f'{type(collections) = }')
    debug: bool = True
    for collection in collections:
        if debug:
            debug = False
            print(f'{type(collection) = }')
        print(f'\t{collection = }')
    """
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
        msg = f"{result['name']=}\n\t{result['cuisine']=}\n\t{result['borough']=}\n\t{result['address']['zipcode']=}"
        LU.debug(msg)


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
    display_mongodb_collections()
    LU.debug('DEBUG: end of program')


if __name__ == '__main__':
    LU.start_logging()

    msg = f'Python version: {get_python_version()}'
    LU.log_info_and_debug(msg)

    msg = f'loguru version: {get_package_version("loguru")}'
    LU.log_info_and_debug(msg)

    msg = f'PyMongo version: {get_package_version("PyMongo")}'
    LU.log_info_and_debug(msg)

    msg = f'MongoDB Atlas version: {get_mongodb_version()}'
    LU.log_info_and_debug(msg)

    main()
