import os
from dotenv import load_dotenv
from pymongo import MongoClient
import bson
import bson.json_util
from database.documents import CrosswordBuilder, PublishType

# TODO: clean this up!
from tests.test_grid import test_clues, test_grid_layout_generation

load_dotenv()

MONGODB_URI = os.getenv('MONGODB_URI')


def to_bson(obj):
    """Recursively converts this document to a dictionary representation.

    See https://stackoverflow.com/a/48413290 for implementation details.

    Args:
        obj: the object to be recursively represented as a dictionary

    Returns:
        A dictionary representation of this object.
    """
    return bson.json_util.loads(bson.json_util.dumps(obj, default=lambda o: o.__dict__))


def main():
    n = 15
    publish_type = PublishType.FAKE

    clue_processor = test_clues(verbose=False)
    grid = test_grid_layout_generation(n, verbose=False)
    grid.fill(clue_processor, num_attempts=10, num_sample_strings=10000, num_test_strings=5, time_limit=10,
              verbosity=0.001)  # TODO: find optimal num_test_strings, 10 seems good?
    print('Generated grid:')
    print(grid)
    print()

    if grid.is_filled():
        generated_crossword = CrosswordBuilder(grid, clue_processor, publish_type).build()
        with MongoClient(MONGODB_URI, tlsAllowInvalidCertificates=True) as client:
            db = client.puzzles
            all_collection = db.all
            all_collection.insert_one(to_bson(generated_crossword))
            print(f'Inserted {generated_crossword}')


if __name__ == '__main__':
    main()
