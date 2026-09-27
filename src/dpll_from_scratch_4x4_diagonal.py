"""
Diagonal Sudoku variant (4x4) solved with the same hand-written DPLL as
dpll_from_scratch_4x4.py, with two extra clauses for the main diagonals.
"""
import time

from grid_generator import print_grid
from dpll_from_scratch_4x4 import (
    dpll,
    decode_solution,
    variable,
)


def encode_diagonal_sudoku(board_size, clues):
    clauses = []
    block_size = int(board_size**0.5)

    for row in range(board_size):
        for col in range(board_size):
            clauses.append([variable(row, col, num, board_size) for num in range(1, board_size + 1)])

    # Main diagonal
    for num in range(1, board_size + 1):
        clauses.append([variable(i, i, num, board_size) for i in range(board_size)])

    # Anti-diagonal
    for num in range(1, board_size + 1):
        clauses.append([variable(i, board_size - 1 - i, num, board_size) for i in range(board_size)])

    for num in range(1, board_size + 1):
        for row in range(board_size):
            for col1 in range(board_size):
                for col2 in range(col1 + 1, board_size):
                    clauses.append([-variable(row, col1, num, board_size), -variable(row, col2, num, board_size)])
            for col in range(board_size):
                for row1 in range(board_size):
                    for row2 in range(row1 + 1, board_size):
                        clauses.append([-variable(row1, col, num, board_size), -variable(row2, col, num, board_size)])

        for row_block in range(0, board_size, block_size):
            for col_block in range(0, board_size, block_size):
                cells = [(row_block + i, col_block + j) for i in range(block_size) for j in range(block_size)]
                for a in range(len(cells)):
                    for b in range(a + 1, len(cells)):
                        r1, c1 = cells[a]
                        r2, c2 = cells[b]
                        clauses.append([-variable(r1, c1, num, board_size), -variable(r2, c2, num, board_size)])

    for row in range(board_size):
        for col in range(board_size):
            if clues[row][col] > 0:
                clauses.append([variable(row, col, clues[row][col], board_size)])

    return clauses


if __name__ == "__main__":
    board_size = 4
    sudoku = [
        [2, 0, 0, 3],
        [0, 1, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
    ]

    print("Puzzle:")
    print_grid(sudoku)

    start = time.time()
    clauses = encode_diagonal_sudoku(board_size, sudoku)
    satisfiable, final_assignment = dpll(clauses, {})
    elapsed = time.time() - start

    print(f"\n{len(clauses)} CNF clauses generated")
    print(f"Solved in {elapsed * 1000:.2f} ms")
    print("Satisfiable:", satisfiable)

    if satisfiable:
        print("\nSolution:")
        print_grid(decode_solution(final_assignment, board_size))
    else:
        print("No solution found.")
