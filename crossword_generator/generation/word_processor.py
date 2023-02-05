import os
import numpy as np
import requests
import wordninja
from nltk.corpus import wordnet
from nltk.stem.wordnet import WordNetLemmatizer
from tqdm import tqdm

import generation.constants as const
from generation.clue_processor import CollectiveClueProcessor
from helper import query_yes_no


def split_words(s):
    """Probabilistically splits strings into English words."""
    contractions = ['d', 'm', 's', 't', 'll', 're', 've']
    split = wordninja.split(s)
    for i in range(len(split)-1, 0, -1):
        if split[i] in contractions:
            split[i-1] += split.pop(i)
    return ' '.join(split)

def get_answer_variants():
    for source in const.CLUE_SOURCES:
        source['path'] = os.path.join(const.DATA_PATH, source['file_name'])
    clue_processor = CollectiveClueProcessor(const.CLUE_SOURCES)

    answers = np.unique(clue_processor.clues['answer'])
    answers = {answer: list({answer.lower(), split_words(answer).lower()}) 
               for answer in answers}
    return {answer: [variant.split() for variant in variants]
            for answer, variants in answers.items()}

def main():
    """
    PROCEED WITH CAUTION.
    Overwrites data/english.txt and data/not-english.txt,
    with runtime dependent on internet speed (took 45 minutes for me on 1/21/23).

    Filters answers provided by CollectiveClueProcessor according to Wordnet
    and dictionary.com.
    """
    question = "This action cannot be undone. " + \
               "This will permanently overwrite data/english.txt and data/not-english.txt."
    if not query_yes_no(question, default='no'):
        return

    english = set()
    answers = get_answer_variants()

    with open(os.path.join(const.DATA_PATH, 'english.txt'), 'a') as english_file:
        # Phase 1: Wordnet
        lem = WordNetLemmatizer()
        with open(os.path.join(const.DATA_PATH, 'wordnet-stopwords.txt'), 'r') as stopwords_file:
            stopwords = [line.strip() for line in stopwords_file]
            wordnet_words = {w.lower().replace('-', '').replace('_', '').replace('.', '') 
                             for w in set(wordnet.words()).union(stopwords)}
        parts_of_speech = ['n', 'v', 'a', 'r', 's']
        for answer, variants in tqdm(answers.items()):
            if any(all(any(lem.lemmatize(word, pos=pos) in wordnet_words
                        for pos in parts_of_speech)
                        for word in variant)
                        for variant in variants):
                english.add(answer)
                english_file.write(answer + '\n')

        # Phase 2: Dictionary.com
        headers = {'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246"}
        for answer in tqdm(set(answers).difference(english)):
            r = requests.get(url=f'https://www.dictionary.com/browse/{answer}', headers=headers)
            if r.status_code == 200:
                english.add(answer)
                english_file.write(answer + '\n')
    
    with open(os.path.join(const.DATA_PATH, 'not-english.txt'), 'a') as not_english_file:
        not_english_file.write('\n'.join(set(answers).difference(english)))


if __name__ == '__main__':
    main()