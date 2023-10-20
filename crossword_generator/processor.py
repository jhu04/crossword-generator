from .grid_generator import off_or_black


def grid_to_string(grid):
    return '\n'.join(''.join(row) for row in grid)


def string_to_grid(s):
    return [list(row) for row in s.split('\n')]


def extract_words(grid):
    """
    Extracts horizontal and vertical words from a filled grid

    Args:
        grid (list(list(char)))

    Returns:
        words (dict(str, dict(int, str))):
          - "across"/"down" (str)
          - id (int), word (str)
        contains_words (dict(tuple, dict(str, int))):
          - coords (tuple)
          - "across"/"down" (str), id (int)
    """
    words = {"across": {}, "down": {}}
    contains_words = {}
    id = 1
    for r in range(len(grid)):
        for c in range(len(grid[0])):
            if grid[r][c] != '#':
                contains_words[(r, c)] = {"across": None, "down": None}

    for r in range(len(grid)):
        for c in range(len(grid[0])):
            if grid[r][c] == '#':
                continue
            word = False
            if off_or_black(grid, r, c-1):
                word, x, s = True, c, ""
                while x < len(grid[0]) and grid[r][x] != '#':
                    s += grid[r][x]
                    contains_words[(r, x)]["across"] = id
                    x += 1
                words["across"][id] = s
            if off_or_black(grid, r-1, c):
                word, x, s = True, r, ""
                while x < len(grid) and grid[x][c] != '#':
                    s += grid[x][c]
                    contains_words[(x, c)]["down"] = id
                    x += 1
                words["down"][id] = s
            id += word

    return words, contains_words
