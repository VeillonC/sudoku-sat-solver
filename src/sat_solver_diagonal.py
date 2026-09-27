"""
Diagonal Sudoku variant (both main diagonals must also contain every digit
exactly once), solved the same way as the classic version: encoded to CNF
and handed to Glucose3 (PySAT).
"""
import time

from pysat.solvers import Glucose3

from grid_generator import print_grid


def variable(row, col, num, board_size):
    return row * board_size**2 + col * board_size + num


def encode_diagonal_sudoku(board_size, clues):
    clauses = []
    block_size = int(board_size**0.5)

    # Each cell has at least one value
    for row in range(board_size):
        for col in range(board_size):
            clauses.append([variable(row, col, num, board_size) for num in range(1, board_size + 1)])

    # Main diagonal: every digit must appear once
    for num in range(1, board_size + 1):
        clauses.append([variable(i, i, num, board_size) for i in range(board_size)])

    # Anti-diagonal: every digit must appear once
    for num in range(1, board_size + 1):
        clauses.append([variable(i, board_size - 1 - i, num, board_size) for i in range(board_size)])

    # Row / column / block constraints: a value can't repeat
    for row in range(board_size):
        for col in range(board_size):
            for num in range(1, board_size + 1):
                for other_col in range(board_size):
                    if other_col != col:
                        clauses.append([-variable(row, col, num, board_size), -variable(row, other_col, num, board_size)])

                for other_row in range(board_size):
                    if other_row != row:
                        clauses.append([-variable(row, col, num, board_size), -variable(other_row, col, num, board_size)])

                start_row, start_col = (row // block_size) * block_size, (col // block_size) * block_size
                for i in range(start_row, start_row + block_size):
                    for j in range(start_col, start_col + block_size):
                        if i != row and j != col:
                            clauses.append([-variable(row, col, num, board_size), -variable(i, j, num, board_size)])

    # Fix the given clues
    for row in range(board_size):
        for col in range(board_size):
            if clues[row][col] > 0:
                clauses.append([variable(row, col, clues[row][col], board_size)])

    return clauses


def solve_diagonal_sudoku(board_size, clues):
    solver = Glucose3()
    clauses = encode_diagonal_sudoku(board_size, clues)

    for clause in clauses:
        solver.add_clause(clause)

    if solver.solve():
        model = solver.get_model()
        solution = [[0] * board_size for _ in range(board_size)]
        for row in range(board_size):
            for col in range(board_size):
                for num in range(1, board_size + 1):
                    if model[variable(row, col, num, board_size) - 1] > 0:
                        solution[row][col] = num
                        break
        return solution
    return None


if __name__ == "__main__":
    board_size = 9
    clues = [
        [2, 0, 0, 0, 0, 0, 0, 0, 5],
        [0, 5, 0, 0, 2, 0, 8, 0, 0],
        [7, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 3, 0, 0, 0, 0, 0, 9],
        [0, 0, 0, 4, 3, 9, 0, 0, 0],
        [4, 0, 0, 0, 0, 0, 6, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 4],
        [0, 0, 1, 0, 4, 0, 0, 6, 0],
        [8, 0, 0, 0, 0, 0, 0, 0, 7],
    ]

    print("Puzzle:")
    print_grid(clues)

    start = time.time()
    solution = solve_diagonal_sudoku(board_size, clues)
    elapsed = time.time() - start

    print(f"\nSolved in {elapsed * 1000:.2f} ms")

    if solution:
        print("\nSolution:")
        print_grid(solution)
    else:
        print("No solution found.")
