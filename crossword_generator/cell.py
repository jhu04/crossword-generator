from crossword_generator.direction import Direction

class Cell:
    # WARNING: Cell.BLANK and Cell.WALL are NOT Cells!
    BLANK = "."
    WALL = "#"

    def __init__(self, grid, row, col, label=BLANK):
        self.grid = grid
        self.row = row
        self.col = col
        self.label = label
        self.neighbors = {}

    def set_neighbors(self):
        for dir in Direction:
            self.neighbors[dir] = self.grid.cell(self.row + dir.value.r, self.col + dir.value.c)

    def is_blank(self):
        return self.label == Cell.BLANK

    def is_wall(self):
        return self.label == Cell.WALL

    def set_label(self, label):
        self.label = label

    def make_wall(self):
        self.set_label(Cell.WALL)
    
    def get_across(self):
        """`Across` array of Cells containing self"""
        left = self.in_direction(Direction.WEST)[:0:-1]
        right = self.in_direction(Direction.EAST)[1:]
        return left + [self] + right
    
    def get_down(self):
        """`Down` array of Cells containing self"""
        up = self.in_direction(Direction.NORTH)[:0:-1]
        down = self.in_direction(Direction.SOUTH)[1:]
        return up + [self] + down

    def in_direction(self, dir):
        """Returns a list of cells starting at self (inclusive) until hitting a wall"""
        if self.is_wall():
            return []
        return [self] + self.neighbors[dir].in_direction(dir)

    def __repr__(self):
        return f'Cell({self.row}, {self.col})'
        