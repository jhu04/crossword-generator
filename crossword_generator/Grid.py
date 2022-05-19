from dataclasses import dataclass
from math import inf
from queue import Empty, PriorityQueue

from Entry import Entry
from word_generator import possible_words
from processor import extract_words, grid_to_string
from word_generator import generate_buckets

@dataclass(order=True)
class Grid:
    len_remaining_words: int
    
    remaining_words: PriorityQueue(Entry)
    
    n: int
    squares: tuple[tuple[str]]
    
    buckets: tuple[tuple[tuple[set]]]
    # buckets[len][pos][char] = possible_words
    
    def __init__(self, squares=(), buckets=None):
        if (squares == None):
            raise ValueError('Grid must not be None')
        if (len(squares) > 0 and len(squares) != len(squares[0])):
            raise ValueError('Grid must be square')
        
        self.squares = squares
        self.n = len(squares)
        
        self.remaining_words = PriorityQueue()
        # for some reason self.squares doesn't work
        words, contains_words = extract_words(squares)
        for coords, x in contains_words.items():
            for direction, id in x.items():
                word = words[direction][id]
                self.remaining_words.put(Entry(grid=self, word=word, r=coords[0], c=coords[1], direction=direction))
        
        self.len_remaining_words = self.remaining_words.qsize()
        self.buckets = buckets
        
    def __str__(self):
        return grid_to_string(self.squares)
    
    def fill(self, entry):
        res_squares = [list(x) for x in self.squares]
        for i in range(len(entry.word)):
            if entry.direction == 'across':
                res_squares[entry.r][entry.c + i] = entry.word[i]
            else:
                res_squares[entry.r + i][entry.c] = entry.word[i]
        res = Grid(res_squares, self.buckets)
        
        return res
    
    def possible_next_grids(self):
        cur_entry = self.remaining_words.get()
        
        possible = possible_words(word=cur_entry.word, buckets=self.buckets)
        
        res = (self.fill(Entry(grid=cur_entry.grid, word=x, r=cur_entry.r, c=cur_entry.c, direction=cur_entry.direction)) for i, x in enumerate(possible) if i < 5)
        print(x for x in res)
        return res
    
    def solve(self):
        pq = PriorityQueue()
        
        pq.put(self)
        
        while not pq.empty():
            p = pq.get()
            
            if p.len_remaining_words == 0:
                return p
            
            for p_next in self.possible_next_grids():
                # pq.put(p_next)
                return p
        
        return None
    
# unit testing
def main():
    n = 15
    
    buckets = generate_buckets()
    
    g = Grid(((' ', 'S', 'S'), ('S', ' ', ' '), ('S', ' ', 'S')), buckets=buckets)
    
    print(g.solve())
    
if __name__ == '__main__':
    main()