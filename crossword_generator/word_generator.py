from cachetools.keys import hashkey
from cachetools import cached


def upper_to_int(ch):
    """Returns an integer based on the mapping {'A': 0, ..., 'Z': 25}

    Args:
        ch (char): character to be mapped

    Returns:
        int: mapped value
    """
    return ord(ch) - ord('A')


def generate_buckets(n=15):
    """Generates buckets

    Returns:
        tuple[tuple[tuple[set]]]: buckets[len][pos][char] = set of possible words
    """
    with open('./data/wordlist.txt', 'r') as f:
        buckets = [[[set([]) for ch in range(26)]
                    for ch_pos in range(length + 1)]
                   for length in range(n + 1)]

        for x in f:
            x = x.strip()
            if len(x) <= n and x.isalpha():
                for i, ch in enumerate(x):
                    buckets[len(x)][i][upper_to_int(ch)].add(x)

        # preprocess word = '.' * len
        for length in range(n + 1):
            possible = set()
            for possible_i in buckets[length]:
                for possible_ch in possible_i:
                    possible = possible.union(possible_ch)

            buckets[length][length] = possible

        return buckets


# https://stackoverflow.com/questions/30730983/make-lru-cache-ignore-some-of-the-function-arguments


@cached(cache={}, key=lambda buckets, word: hashkey(word))
def possible_words(word, buckets):
    possible = set()
    first = True

    if word == '.' * len(word):
        return buckets[len(word)][len(word)]
    else:
        for i, ch in enumerate(word):
            if ch == '.':
                continue

            if first:
                possible = buckets[len(word)][i][upper_to_int(ch)]
                first = False
            elif possible == set():
                return set()
            else:
                possible = possible.intersection(
                    buckets[len(word)][i][upper_to_int(ch)])

    return possible
