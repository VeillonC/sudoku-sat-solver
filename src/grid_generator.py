"""
Utilities to generate, remove clues from, and pretty-print Sudoku grids of
any size whose square root is an integer (4x4, 9x9, 16x16...).

Grid filling uses randomized backtracking: it is the same constraint search
used later by the SAT-based and DPLL-based solvers, just applied here to
build a valid, fully solved grid before clues are removed from it.
"""
import math
import random


def initialize_grid(size):
    return [[0 for _ in range(size)] for _ in range(size)]


def is_valid(grid, number, position, block_size):
    row, col = position
    size = len(grid)

    if number in grid[row]:
        return False
    if number in [grid[i][col] for i in range(size)]:
        return False

    block_row, block_col = row // block_size, col // block_size
    for i in range(block_row * block_size, (block_row + 1) * block_size):
        for j in range(block_col * block_size, (block_col + 1) * block_size):
            if grid[i][j] == number:
                return False
    return True


def fill_grid(grid, block_size):
    size = len(grid)
    digits = list(range(1, size + 1))

    for row in range(size):
        for col in range(size):
            if grid[row][col] == 0:
                random.shuffle(digits)
                for number in digits:
                    if is_valid(grid, number, (row, col), block_size):
                        grid[row][col] = number
                        if fill_grid(grid, block_size):
                            return True
                        grid[row][col] = 0
                return False
    return True


def remove_clues(grid, num_to_remove):
    size = len(grid)
    cells_to_clear = random.sample(range(size * size), num_to_remove)
    for index in cells_to_clear:
        row, col = divmod(index, size)
        grid[row][col] = 0


def generate_sudoku(size, clues_to_keep):
    """Generate a full valid grid of the given size, then blank out cells
    until only `clues_to_keep` of them remain."""
    block_size = math.isqrt(size)
    grid = initialize_grid(size)
    fill_grid(grid, block_size)
    remove_clues(grid, size * size - clues_to_keep)
    return grid


def print_grid(grid):
    size = len(grid)
    block_size = math.isqrt(size)
    separator = "+" + "+".join(["-" * (2 * block_size + 1)] * block_size) + "+"

    for i in range(size):
        if i % block_size == 0 and i != 0:
            print(separator)
        row_str = ""
        for j in range(size):
            if j % block_size == 0 and j != 0:
                row_str += "| "
            row_str += (str(grid[i][j]) if grid[i][j] != 0 else ".") + " "
        print(row_str)
