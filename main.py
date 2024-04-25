import os, sys
from pymongo import MongoClient
from dotenv import load_dotenv


def get_python_version() -> str:
    return f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"


def get_connection_string() -> str:
    load_dotenv()
    pwd: str = os.environ.get('mongodb_pwd')
    # WARNING: need to add authSource=admin for other useful commands to work
    return f'mongodb+srv://frederickmorrison1953:{pwd}@pymongocluster.6sstkik.mongodb.net/?retryWrites=true&w=majority&appName=pymongoCluster&authSource=admin'


def get_mongodb_connection() -> MongoClient:
    return MongoClient(get_connection_string())


def verify_mongodb_connection_works():
    client: MongoClient = get_mongodb_connection()
    print(f'{client=}')


def verify_mongodb_database():
    client: MongoClient = get_mongodb_connection()
    print(f'{client=}')
    # FAILS with bad auth error - not sure why: db = client.list_databases()
    db = client['user_shopping_list']
    print(f'{db=}')


if __name__ == '__main__':
    print(f"Python version: {get_python_version()}")
    verify_mongodb_connection_works()
    verify_mongodb_database()
