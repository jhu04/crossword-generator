# THIS FILE IS ARCHIVED. THE WORDLIST FILE (../data/wordlist.txt) CAN BE FOUND AT
# https://crosswordnexus.com/downloads/wordlist.txt; REMOVE WORDS WITH NUMBERS TO OBTAIN THE FILE.

from cachetools.keys import hashkey
from cachetools import cached


def upper_to_int(ch):
    """Returns an integer based on the mapping {'A': 0, ..., 'Z': 25}. O(1) runtime.

    Args:
        ch (char): character to be mapped

    Returns:
        int: mapped value
    """
    return ord(ch) - ord('A')

def bit_mask(s, bits=0, fill='.') -> str:
    """Returns s masked by bits. O(len(s)) runtime

    Args:
        s (int): The string to be masked.
        bits (int): Bitmask. Defaults to 0.
        fill (str): Character to fill characers where the bit is 0. Defaults to '.'.

    Raises:
        ValueError: Raises if the bit mask contains too many bits
        ValueError: Raises if bits is not of type int

    Returns:
        str: The masked string
    """
    if isinstance(bits, int):
        if 1 << len(s) <= bits:
            raise ValueError('Invalid bit mask (bits too large)')
        
        res = []
        cnt = 0
        while bits > 0:
            res.append(s[-1 - cnt] if bits % 2 == 1 else fill)
            bits = bits >> 1
            cnt += 1
        
        res.append(fill * (len(s) - len(res)))
        return ''.join(res)[::-1]
    else:
        raise ValueError('bits must be of type int')

def pad(s, length, fill='.') -> str:
    return ''.join((s, fill * (length - len(s))))

def generate_buckets(n=15,k=7):
    """Generates buckets

    Args:
        n (int): Size of grid and maximum word length. Defaults to 15.
        k (int): Maximum word length stored in dictionary. Defaults to 10.

    Returns:
        dict[str -> list]: Maps from a string (e.g. 'p__y') to a set of valid words (e.g. {'penny', ...}). 
            For words of length greater than k, the subset of all possible clues for the first k characters 
            padded by '.' are stored
    """
    with open('../data/wordlist.txt', 'r') as f:
        buckets = {}

        for x in f:
            x = x.strip()
            if len(x) <= n and x.isalpha():
                len_mask = min(len(x), k)
                # splicing is O(n), would like to avoid
                # idk if interpreter optimizes putting the if statement out of the loop, did it myself 
                # just in case
                if len_mask == len(x):
                    for i in range(1 << len_mask):
                        key = bit_mask(x, i)
                        
                        if not key in buckets:
                            buckets[key] = [x]
                        else:
                            buckets[key].append(x)
                else:
                    for i in range(1 << len_mask):
                        key = pad(bit_mask(x[:len_mask], i), len(x))
                        
                        if not key in buckets:
                            buckets[key] = [x]
                        else:
                            buckets[key].append(x)
                
        # TODO: preprocess '.' * n to return all possible words of length n for n >= k

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

# unit testing
def main():
    # print(bit_mask('abcdef', int('010011', 2)))
    # print(pad('a', 2))
    
    import json
    
    buckets = generate_buckets()
    # print([(key, buckets[key]) for key in buckets if len(key) <= 2])
    
    # from sys import getsizeof
    # print(getsizeof(buckets))
    
    # https://stackoverflow.com/questions/8230315/how-to-json-serialize-sets
    # class SetEncoder(json.JSONEncoder):
    #     def default(self, obj):
    #         if isinstance(obj, set):
    #             return list(obj)
    #         return json.JSONEncoder.default(self, obj)
    
    with open('buckets.json', 'w') as f:
        f.write(json.dumps(buckets))
    
if __name__ == '__main__':
    main()