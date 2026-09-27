"""
Classic Sudoku solved by encoding it as a SAT (boolean satisfiability)
problem and handing it to Glucose3, a real CDCL SAT solver, via the PySAT
library.

Each (row, col, digit) possibility is a boolean variable. The Sudoku rules
(one digit per cell, each digit once per row/column/3x3 block) become CNF
clauses, and the given clues become unit clauses fixing their variable to
true.
"""
import time

from pysat.solvers import Glucose3

from grid_generator import generate_sudoku, print_grid


def variable(row, col, num, board_size):
    return row * board_size**2 + col * board_size + num


def encode_sudoku(board_size, clues):
    clauses = []
    block_size = int(board_size**0.5)

    # Each cell has at least one value
    for row in range(board_size):
        for col in range(board_size):
            clauses.append([variable(row, col, num, board_size) for num in range(1, board_size + 1)])

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


def solve_sudoku(board_size, clues):
    solver = Glucose3()
    clauses = encode_sudoku(board_size, clues)

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
        return solution, len(clauses)
    return None, len(clauses)


if __name__ == "__main__":
    sudoku = generate_sudoku(size=9, clues_to_keep=17)  # 17 clues: the minimum for a unique-solution 9x9 grid

    print("Puzzle:")
    print_grid(sudoku)

    start = time.time()
    solution, num_clauses = solve_sudoku(9, sudoku)
    elapsed = time.time() - start

    print(f"\n{num_clauses} CNF clauses generated")
    print(f"Solved in {elapsed * 1000:.2f} ms")

    if solution:
        print("\nSolution:")
        print_grid(solution)
    else:
        print("No solution found.")
