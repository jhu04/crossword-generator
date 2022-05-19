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
    
    # remaining_words: PriorityQueue(Entry)
    
    # n: int
    # squares: tuple[tuple[str]]
    
    # buckets: tuple[tuple[tuple[set]]]
    # buckets[len][pos][char] = possible_words
    
    def __init__(self, squares=(), buckets=None):
        if (squares == None):
            raise ValueError('Grid must not be None')
        if (len(squares) > 0 and len(squares) != len(squares[0])):
            raise ValueError('Grid must be square')
        
        self.squares = squares
        self.n = len(squares)
        
        self.remaining_words = PriorityQueue()
        words, contains_words = extract_words(self.squares)
        for coords, x in contains_words.items():
            for direction, id in x.items():
                word = words[direction][id]
                if '.' in word:
                    self.remaining_words.put(Entry(grid=self, word=word, r=coords[0], c=coords[1], direction=direction))
        
        self.len_remaining_words = self.remaining_words.qsize()
        self.buckets = buckets
        
    def __str__(self):
        return grid_to_string(self.squares)
    
    def valid(self):
        """Checks if grid has a valid solution

        Returns:
            bool: True if the grid has a valid solution, False else
        """
        words = extract_words(self.squares)[0]
        # print(words)
        for direction, more_info in words.items():
            for id, word in more_info.items():
                if possible_words(word=word, buckets=self.buckets) == set():
                    return False
        return True
    
    def fill(self, entry):
        """Fills the grid with one word

        Args:
            entry (Entry): An Entry describing the word to be filled

        Raises:
            ValueError: Raises if self conflicts with entry.grid; see comment below 

        Returns:
            Grid: Grid with filled entry
        """
        
        if self != entry.grid:
            # techinically self is unnecessary, but this check is likely good to make sure the right grid is modified
            raise ValueError('Self should be equal to entry.grid')
        
        res_squares = [list(x) for x in self.squares]
        for i in range(len(entry.word)):
            if entry.direction == 'across':
                res_squares[entry.r][entry.c + i] = entry.word[i]
            else:
                res_squares[entry.r + i][entry.c] = entry.word[i]
        res_squares = tuple(tuple(x) for x in res_squares)
        
        res = Grid(res_squares, self.buckets)
        return res
    
    def possible_next_grids(self):
        """Generates possible grids after filling in one word

        Returns:
            generator[Grid]: A generator containing the first 5 possible grids
        """
        cur_entry = self.remaining_words.get()
        
        possible = possible_words(word=cur_entry.word, buckets=self.buckets)
        
        res = (self.fill(Entry(grid=cur_entry.grid, word=x, r=cur_entry.r, c=cur_entry.c, direction=cur_entry.direction)) for i, x in enumerate(possible) if i < 5)
        # for x in res:
        #     print(x)
        return res
    
    def solve(self):
        """Solves the grid

        Returns:
            Grid: Solved grid
        """
        # debug
        cnt = 0
        
        pq = PriorityQueue()
        
        pq.put(self)
        
        while not pq.empty():
            p = pq.get()
            
            # print("ORIGINAL GRID:")
            # print(p)
            
            if not p.valid():
                continue
            
            if p.len_remaining_words == 0:
                return p
            
            # print("NEXT GRIDS:")
            for p_next in p.possible_next_grids():
                pq.put(p_next)
                # print(p_next)
        
        return None
    
# unit testing
def main():
    buckets = generate_buckets()
    
    # squares = (('.', 'S', 'S'), ('S', '.', '.'), ('S', '.', 'S'))
    # from word_generator import example_grid_str
    # from processor import string_to_grid
    
    # squares = string_to_grid(example_grid_str)
    # print(len(squares), len(squares[0]))
    
    from grid_generator import make_grid
    
    squares = make_grid(7)
    print(squares)
    
    g = Grid(squares, buckets=buckets)
    
    print(g.solve())
    
if __name__ == '__main__':
    main()