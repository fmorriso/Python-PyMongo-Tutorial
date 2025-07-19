import sys
from collections import defaultdict
from importlib.metadata import version

#
import pymongo
from pymongo import MongoClient
from pymongo.synchronous.database import Database
#
from shapely.geometry import shape, Point
from wtforms import StringField

#
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
    # msg = f'{conn_string=}'
    # LU.debug(msg)
    return conn_string


def get_mongodb_client() -> MongoClient:
    """get a client connection to my personal MongoDB Atlas cluster using my personal userid and password"""
    connection_string: str = get_connection_string()
    connection: MongoClient = MongoClient(connection_string)
    return connection


def verify_mongodb_connection_works():
    client: MongoClient = get_mongodb_client()
    LU.debug(f'{client=}')


def verify_mongodb_database():
    LU.debug('top of verify_mongodb_database')
    client: MongoClient = get_mongodb_client()
    LU.debug(f'{client=}')
    # print('Trying to look at a specific database')
    db = client['sample_restaurants']
    LU.debug(f'{db=}')
    LU.debug('looping through all client database names')
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
    version_number: str = 'unknown'
    if key in result.keys():
        version_number = result.get(key)
    return version_number


def display_mongodb_collections():
    LU.debug('top of display_mongodb_collections')
    client = get_mongodb_client()
    # db = client['sample_mflix']
    databases = client.list_database_names()
    msg = f'{databases = }'
    LU.info(msg)
    LU.debug(msg)

    # List all the collections
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
    LU.debug('bottom of display_mongodb_collections')


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
    LU.debug(f'{user_properties=}')

    for doc in documents:
        for field_name, value in doc.items():
            # Some smart recognition can be here
            field_definition = StringField()
            user_properties[field_name] = field_definition


def display_american_cuisine_restaurants():
    LU.log_info_and_debug('top of display_american_cuisine_restaurants')
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
        result_msg = f"\nName: {result['name']}\n\tCuisine: {result['cuisine']}\n\tBorough: {result['borough']}\n\tZip: {result['address']['zipcode']}"
        LU.log_info_and_debug(result_msg)


def display_restaurants_with_neighborhood_name() -> None:
    LU.debug('top of display_restaurants_with_neighborhood_name')
    client = get_mongodb_client()

    db = client.sample_restaurants

    # 2. Load neighborhoods and build polygons list
    neighborhoods = list(db.neighborhoods.find())
    neighborhood_polygons = []
    for n in neighborhoods:
        if "geometry" not in n or "name" not in n:
            continue
        polygon = shape(n["geometry"])
        name = n["name"]
        neighborhood_polygons.append((name, polygon))

    # 3. Dictionary: neighborhood_name -> list of restaurants
    matches = defaultdict(list)

    for restaurant in db.restaurants.find({}, {"name": 1, "cuisine": 1, "address.coord": 1}):
        coords = restaurant.get("address", {}).get("coord", [])
        if not coords or len(coords) != 2:
            continue

        point = Point(coords)
        matched_neighborhood = None

        for name, polygon in neighborhood_polygons:
            if polygon.contains(point):
                matched_neighborhood = name
                break

        if matched_neighborhood:
            matches[matched_neighborhood].append({
                "name": restaurant['name'],
                "cuisine": restaurant['cuisine']
            })

    # 4. Sort neighborhoods alphabetically
    sorted_neighborhoods = sorted(matches.items(), key = lambda x: x[0])  # Sort by neighborhood name

    # for neighborhood, restaurants in sorted_neighborhoods:
    #     LU.debug(f"Neighborhood: {neighborhood} ({len(restaurants)} restaurants)")
    #     for r in restaurants:
    #         LU.debug(f"\t{r['name']} ({r['cuisine']})")

    for neighborhood, restaurants in sorted_neighborhoods:
        # Sort restaurants alphabetically by name
        sorted_restaurants = sorted(restaurants, key=lambda r: r["name"])

        LU.debug(f"Neighborhood: {neighborhood} ({len(sorted_restaurants)} restaurants)")
        for r in sorted_restaurants:
            LU.debug(f"\t{r['name']} ({r['cuisine']})")


def get_required_package_names() -> list[str]:
    """
    read the requirements.txt file and return a sorted list of package names.
    :return: sorted list of package names
    :rtype: list[str
    """
    packages: list[str] = []
    with open('requirements.txt') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue  # skip blank lines and comments
            package = line.split('~')[0].strip()  # works for ~=, >=, ==, etc.
            packages.append(package)

    packages.sort(key = str.lower)
    return packages


def main():
    verify_mongodb_connection_works()
    verify_mongodb_database()
    # display_american_cuisine_restaurants()
    # create_schema()
    display_mongodb_collections()
    display_restaurants_with_neighborhood_name()
    LU.debug('DEBUG: end of program')


if __name__ == '__main__':
    LU.start_logging('log.txt')

    msg = f'Python version: {get_python_version()}'
    LU.log_info_and_debug(msg)

    package_names = get_required_package_names()

    for pkg in package_names:
        package_name = f'{pkg}'.ljust(16)
        try:
            LU.log_info_and_debug(f'{package_name}{get_package_version(pkg)}')
        except Exception as e:
            print(e)

    msg = f'MongoDB Atlas version: {get_mongodb_version()}'
    LU.log_info_and_debug(msg)

    main()
