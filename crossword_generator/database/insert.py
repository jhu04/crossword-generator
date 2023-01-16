import os
import argparse
import bson
import bson.json_util
import datetime
import math
import numpy as np
import pymongo
import random
import warnings

import database.constants as db_const
import generation.constants as gen_const
from database.documents import CrosswordBuilder, PublishType
from generation.clue_processor import CollectiveClueProcessor
from generation.grid import Grid



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
    for source in gen_const.CLUE_SOURCES:
        source['path'] = os.path.join(gen_const.DATA_PATH, source['file_name'])
    clue_processor = CollectiveClueProcessor(gen_const.CLUE_SOURCES)

    def helper(n, daily_date):
        """Helper method for grid generation and insertion."""
        grid = Grid(n)
        grid.fill(clue_processor, num_attempts=10, num_sample_strings=10,
                  num_test_strings=5, time_limit=10, verbosity=0.001)
        print(f'Generated grid:\n{str(grid)}\n')

        if grid.is_filled():
            crossword = CrosswordBuilder(grid, clue_processor, publish_type, daily_date).build()
            db_const.COLLECTION.insert_one(to_bson(crossword))
            print(f'Inserted above crossword; size {n}.\n')

    if publish_type is PublishType.DAILY:
        docs = db_const.COLLECTION.find({'puzzle_meta.publishType': PublishType.DAILY.value}) \
                                  .sort('_id', pymongo.DESCENDING) \
                                  .limit(2)
        latest_dates = [datetime.datetime.strptime(
            doc['puzzle_meta']['dailyDate'], db_const.DATE_FORMAT) for doc in docs]
        assert len(latest_dates) <= 2

        daily_date: datetime.datetime
        if len(latest_dates) == 0:
            daily_date = datetime.datetime.utcnow()
        elif len(latest_dates) == 1:
            daily_date = latest_dates[0]
        else:  # if len(latest_dates) == 2
            daily_date = latest_dates[1] + datetime.timedelta(days=1)
        for _ in range((num_grids + 1)//2):
            for sizes in (gen_const.DAILY_MINI_SIZES, gen_const.DAILY_MAXI_SIZES):
                n = int(np.random.choice(sizes))
                helper(n, daily_date)
            daily_date += datetime.timedelta(days=1)

    else:
        props = np.array([select_props(n) for n in sizes])
        props = props / np.sum(props)
        for _ in range(num_grids):
            n = int(np.random.choice(sizes, p=props))
            helper(n, daily_date=None)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--sizes', nargs='+', type=int)
    parser.add_argument('-g', '--num-grids', nargs='?', type=int, default=1)
    parser.add_argument('-t', '--type', nargs='?', type=str, default='fake')
    args = parser.parse_args()

    if args.type.lower() == 'daily':
        publish_type = PublishType.DAILY
    elif not args.sizes:
        raise ValueError('Provide at least one grid size to generate.')
    elif args.type.lower() == 'free':
        publish_type = PublishType.FREE
    elif args.type.lower() == 'fake':
        warnings.warn("You are generating grids of type 'fake'.")
        publish_type = PublishType.FAKE
    else:
        raise Exception('Invalid --type.')

    main(args.sizes, args.num_grids, publish_type)
