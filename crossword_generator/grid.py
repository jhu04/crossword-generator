from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
import random
from typing import ClassVar

from crossword_generator.clue_processor import ClueProcessor


@dataclass()
class Position:
    """Should be an inner class for Cardinal, but isn't due to Enum"""

    row: int
    col: int

    def __repr__(self):
        return f'({self.row}, {self.col})'


class Cardinal(Enum):
    NORTH = Position(-1, 0)
    SOUTH = Position(1, 0)
    EAST = Position(0, 1)
    WEST = Position(0, -1)

    value: Position


class Direction(Enum):
    ACROSS = 'across'
    DOWN = 'down'

    value: str

    def opposite(self):
        return Direction.DOWN if self is Direction.ACROSS else Direction.ACROSS


class Grid:
    """1-indexed N x N grid of Cells"""

    def __init__(self, n, set_layout=True):
        assert 4 <= n <= 15
        self.n = n
        self.grid = [[Cell(self, r, c) for c in range(n + 2)] for r in range(n + 2)]
        for i in range(self.n + 2):
            self.grid[i][0].make_wall()
            self.grid[i][self.n + 1].make_wall()
            self.grid[0][i].make_wall()
            self.grid[self.n + 1][i].make_wall()
        for i in range(self.n + 2):
            for j in range(self.n + 2):
                self.cell(i, j).set_neighbors()

        self.across = {}
        self.down = {}
        self.ids = {}
        self.entries = []
        if set_layout:
            self.generate_layout()
            self.number_cells()

    def cell(self, r: int, c: int) -> Cell | None:
        if r < 0 or r >= len(self.grid) or c < 0 or c >= len(self.grid[0]):
            return None
        return self.grid[r][c]

    def generate_layout(self) -> None:
        """Generates a 2D array of Cells, subject to requirements on the number of 
        walls and words and lengths of words it contains. Implemented via repeatedly 
        adding walls that satisfy these requirements."""

        # TODO: make cleaner bounds
        MAX_WALL = int(0.17 * self.n ** 2 + 0.066 * self.n - 1.1)
        MAX_WORDS = int(0.34 * self.n ** 2 - 0.3 * self.n + 4)
        MIN_WORD_LENGTH = 3
        SYMMETRIC_SIZES = [6, 7, 11, 12, 13, 14, 15]

        curr_wall = 0
        curr_words = 2 * self.n
        available_cells = [(i, j) for i in range(1, self.n + 1) for j in range(1, self.n + 1)]

        def added_words(r, c) -> int:
            """Incremented number of words by adding a wall at (r, c)"""
            return 2 - sum(
                [self.grid[r + direction.value.row][c + direction.value.col].is_wall() for direction in Cardinal])

        def add_wall(r: int, c: int) -> None:
            nonlocal curr_wall, curr_words
            self.cell(r, c).make_wall()
            curr_wall += 1
            curr_words += added_words(r, c)
            available_cells.remove((r, c))

        illegal_cells = []
        if self.n in SYMMETRIC_SIZES and self.n % 2 == 1:
            for i in range(int(-(MIN_WORD_LENGTH + 1) / 2), int((MIN_WORD_LENGTH + 1) / 2)):
                illegal_cells.append((i + (self.n + 1) / 2, (self.n + 1) / 2))
                illegal_cells.append(((self.n + 1) / 2, i + (self.n + 1) / 2))

        while curr_wall < MAX_WALL and curr_words < MAX_WORDS:
            r, c = available_cells[random.randint(0, len(available_cells) - 1)]
            if all(self.cell(r, c).neighbors[dir].is_wall()
                   or len(self.cell(r, c).in_direction(dir)) > MIN_WORD_LENGTH for dir in Cardinal):
                if (r, c) not in illegal_cells:
                    add_wall(r, c)
                    if self.n in SYMMETRIC_SIZES:
                        add_wall(self.n + 1 - r, self.n + 1 - c)

    def number_cells(self) -> None:
        """Assigns clue numbers to cells. Specifically, assigns `across`,
        `down`, `ids`, and `entries`."""
        identifier = 1
        for r in range(1, self.n + 1):
            for c in range(1, self.n + 1):
                if self.cell(r, c).is_wall():
                    continue
                is_entry = False
                if self.cell(r, c).neighbors[Cardinal.WEST].is_wall():
                    is_entry = True
                    self.across[identifier] = self.cell(r, c)
                    self.ids[(r, c)] = identifier
                    self.entries.append(Entry(self, self.cell(r, c).get_across()))
                if self.cell(r, c).neighbors[Cardinal.NORTH].is_wall():
                    is_entry = True
                    self.down[identifier] = self.cell(r, c)
                    self.ids[(r, c)] = identifier
                    self.entries.append(Entry(self, self.cell(r, c).get_down()))
                if is_entry:
                    identifier += 1
        self.entries.sort(key=lambda e: -e.length)

    def fill(self, clue_processor: ClueProcessor, num_attempts=10, num_test_strings=10, verbosity=0) -> None:
        """Fills in the grid, roughly* in order of decreasing word length. TODO: make this faster!

        *We actually want words to be entered in order of the number of blank cells. However,
        this is pretty annoying (and probably slow) to implement.

        Args:
            clue_processor: The clue processor.
            num_attempts: number of times grid tries filling from scratch
            num_test_strings: number of strings grid tests per entry
            verbosity: proportion of the time things will print

        Returns:
            None
        """

        def intersection(sets: tuple[set] | list[set]):
            if len(sets) == 1:
                return sets[0]
            return sets[0].intersection(*sets[1:])

        def filled(grid: Grid) -> bool:
            return all(not (grid.cell(r, c).is_blank()) for c in range(1, grid.n + 1) for r in range(1, grid.n + 1))

        res: Grid | None = None
        counter, print_every = 0, int(1 / verbosity) if verbosity else 0

        def helper(grid: Grid, entries: list) -> None:
            """Fills in one word at a time, proceeding by DFS. TODO: set to list cast is slow!"""

            # TODO: memoize get_across(), get_down() after layout is set

            def get_candidates(entry: Entry):
                constraints = [(i, entry.cells[i].label) for i in range(entry.length) if not entry.cells[i].is_blank()]
                return list(
                    intersection([clue_processor.words[entry.length][constraint] for constraint in constraints])) \
                    if constraints else list(clue_processor.words[entry.length]['all'])

            nonlocal res, counter
            if res:
                return
            counter += 1
            if verbosity and counter % print_every == 0:
                print(grid, '\n')
            entries = [Entry(grid, [grid.cell(p.row, p.col) for p in entry.positions()]) for entry in entries]
            if not entries:
                res = grid
                return
            entry = entries[0]
            candidates = get_candidates(entry)
            if candidates:
                # if verbose:
                #     print(entry, candidates[:num_test_strings], entries)
                words = random.sample(candidates, min(num_test_strings, len(candidates)))
                for word in words:
                    orthogonal_conflict = False
                    for i in range(entry.length):
                        entry.cells[i].label = word[i]
                        orthogonal = Entry(grid, entry.cells[i].get_entry(entry.direction.opposite()))
                        if not get_candidates(orthogonal):
                            orthogonal_conflict = True
                            break
                    if not orthogonal_conflict:
                        helper(grid.copy(), entries[1:])

        for _ in range(num_attempts):
            helper(self.copy(), self.entries)
            if res and filled(res):
                self.__dict__.update(res.__dict__)
                return

    def copy(self) -> Grid:
        g = Grid(self.n, set_layout=False)
        for r in range(1, self.n + 1):
            for c in range(1, self.n + 1):
                g.cell(r, c).label = self.cell(r, c).label
        g.number_cells()
        return g

    def __str__(self):
        return '\n'.join(' '.join(self.cell(i, j).label for j in range(1, self.n + 1)) for i in range(1, self.n + 1))


@dataclass()
class Cell:
    # WARNING: Cell.BLANK and Cell.WALL are NOT Cells!
    BLANK: ClassVar[str] = "."
    WALL: ClassVar[str] = "#"

    grid: Grid
    row: int
    col: int
    label: str = BLANK
    neighbors: dict[Cardinal, Cell] = field(init=False, default_factory=dict)

    def set_neighbors(self) -> None:
        for dir in Cardinal:
            self.neighbors[dir] = self.grid.cell(self.row + dir.value.row, self.col + dir.value.col)

    def is_blank(self) -> bool:
        return self.label == Cell.BLANK

    def is_wall(self) -> bool:
        return self.label == Cell.WALL

    def make_wall(self) -> None:
        self.label = Cell.WALL

    def get_across(self) -> list[Cell, ...]:
        """Across array of Cells containing self"""
        left = self.in_direction(Cardinal.WEST)[:0:-1]
        right = self.in_direction(Cardinal.EAST)[1:]
        return left + [self] + right

    def get_down(self) -> list[Cell, ...]:
        """Down array of Cells containing self"""
        up = self.in_direction(Cardinal.NORTH)[:0:-1]
        down = self.in_direction(Cardinal.SOUTH)[1:]
        return up + [self] + down

    def get_entry(self, dir: Direction) -> list[Cell, ...]:
        return self.get_across() if dir is Direction.ACROSS else self.get_down()

    def in_direction(self, dir: Cardinal) -> list[Cell, ...]:
        """Returns a list of cells starting at self (inclusive) until hitting a wall.
        Only used internally (for get_across and get_down)."""
        if self.is_wall():
            return []
        return [self] + self.neighbors[dir].in_direction(dir)

    def __repr__(self):
        return f'Cell({self.row}, {self.col})'


@dataclass()
class Entry:
    grid: Grid
    cells: tuple[Cell] | list[Cell]
    length: int = field(init=False)
    direction: Direction = field(init=False)
    id: int = field(init=False)

    def __post_init__(self):
        self.length = len(self.cells)
        self.direction = Direction.ACROSS if self.cells[0].row == self.cells[1].row else Direction.DOWN
        self.id = self.grid.ids[(self.cells[0].row, self.cells[0].col)]

    def positions(self) -> tuple[Position]:
        return tuple(Position(c.row, c.col) for c in self.cells)

    def __repr__(self):
        return f"{self.id}-{self.direction.value}"
