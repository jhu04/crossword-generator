import re
from tqdm import tqdm

import database.constants as const
from database.helper import to_bson

def rewrite_ids(query: dict, desc: str):
    """
    Requests `query` from PUZZLE_COLLECTION and outputs 
    desc: [list of matched ids] to ID_COLLECTION.
    """
    docs = const.PUZZLE_COLLECTION.find(query)
    puzzle_ids = [doc['_id'] for doc in docs]
    const.ID_COLLECTION.update_one(
        {'_id': desc}, 
        {'$set': to_bson({
            '_id': desc,
            'puzzle_id_list': puzzle_ids
        })},
        upsert=True
    )

if __name__ == '__main__':
    for size in tqdm([5, 7, 9, 11, 13, 15, 21]):
        query = {
            'puzzle_meta.width': size,
            'puzzle_meta.height': size,
            'puzzle_meta.publishType': {'$not': re.compile('Daily')}
        }
        desc = f'size_{size}'
        rewrite_ids(query, desc)