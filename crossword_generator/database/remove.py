import pymongo

import database.constants as const
from database.documents import PublishType
from database.helper import query_yes_no


def remove(publish_type):
    """
    PROCEED WITH CAUTION.
    Removes all documents of type `publish_type` from COLLECTION. 
    """

    question = "This action cannot be undone. " + \
               f"This will permanently delete all puzzles of type '{publish_type}'."
    if publish_type.lower() == 'fake':
        if query_yes_no(question, default='no'):
            action = const.COLLECTION.delete_many({'puzzle_meta.publishType': PublishType.FAKE.value})
            print(action.deleted_count, "documents deleted.")
    else:
        raise NotImplementedError()

if __name__ == '__main__':
    remove('fake')