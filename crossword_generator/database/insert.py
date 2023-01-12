import os
import argparse
from dotenv import load_dotenv
from pymongo import MongoClient
import bson
import bson.json_util
import math
import numpy as np

from database.documents import CrosswordBuilder, PublishType
import generation.constants as const
from generation.clue_processor import CollectiveClueProcessor
from generation.grid import Grid

load_dotenv()
MONGODB_URI = os.getenv('MONGODB_URI')
DBNAME = os.getenv('DBNAME')
COLLECTION = os.getenv('COLLECTION')
client = MongoClient(MONGODB_URI, tlsAllowInvalidCertificates=True)
collection = client[DBNAME][COLLECTION]


def to_bson(obj):
    """Recursively converts this document to a dictionary representation.

    See https://stackoverflow.com/a/48413290 for implementation details.

    Args:
        obj: the object to be recursively represented as a dictionary

    Returns:
        A dictionary representation of this object.
    """
    return bson.json_util.loads(bson.json_util.dumps(obj, default=lambda o: o.__dict__))


def main(sizes, num_grids, publish_type, select_props=lambda _: 1):
    props = np.array([select_props(n) for n in sizes])
    props = props / np.sum(props)
    for source in const.CLUE_SOURCES:
        source['path'] = os.path.join(const.DATA_PATH, source['file_name'])
    clue_processor = CollectiveClueProcessor(const.CLUE_SOURCES)

    for _ in range(num_grids):
        n = int(np.random.choice(sizes, p=props))
        grid = Grid(n)
        grid.fill(clue_processor, num_attempts=10, num_sample_strings=10000, num_test_strings=5, time_limit=10,
                  verbosity=0.001)  # TODO: find optimal num_test_strings, 10 seems good?
        print('Generated grid:')
        print(grid)
        print()

        if grid.is_filled():
            crossword = CrosswordBuilder(grid, clue_processor, publish_type).build()
            collection.insert_one(to_bson(crossword))
            print(f'Inserted above crossword; size {n}.\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--sizes', nargs='+', type=int)
    parser.add_argument('-g', '--num-grids', nargs='?', type=int, default=1)
    parser.add_argument('-t', '--type', nargs='?', type=str, default='fake')
    args = parser.parse_args()

    if not args.sizes:
        raise Exception('Provide at least one grid size to generate.')
    if args.type.lower() == 'daily':
        publish_type = PublishType.DAILY
    elif args.type.lower() == 'free':
        publish_type = PublishType.FREE
    elif args.type.lower() == 'fake':
        publish_type = PublishType.FAKE
    else:
        raise Exception('Invalid --type.')

    main(args.sizes, args.num_grids, publish_type, select_props=lambda n: 1/math.sqrt(n))
