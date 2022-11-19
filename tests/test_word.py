from crossword_generator.grid import Grid
from crossword_generator.grid_generator import make_grid
from crossword_generator.word_generator import generate_buckets


def test_word():
    buckets = generate_buckets()
    squares = make_grid(5)
    print('INITIAL GRID:\n' + squares)
    g = Grid(squares, buckets=buckets)
    solved = g.solve()
    print('SOLVED GRID:\n' + solved)


if __name__ == '__main__':
    test_word()
