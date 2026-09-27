"""
Classic Sudoku (4x4) solved with a hand-written DPLL algorithm, to show how
a SAT solver works internally before reaching for a library like PySAT.

This is a textbook DPLL with no unit propagation or clause-learning
heuristics, which is why it is only run here on a 4x4 grid: see
dpll_from_scratch_9x9.py for a discussion of how it scales.
"""
import time

from grid_generator import generate_sudoku, print_grid


def variable(row, col, num, board_size):
    return row * board_size**2 + col * board_size + num


def encode_sudoku(board_size, clues):
    clauses = []
    block_size = int(board_size**0.5)

    for row in range(board_size):
        for col in range(board_size):
            clauses.append([variable(row, col, num, board_size) for num in range(1, board_size + 1)])

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


def dpll(clauses, assignment):
    if all_clauses_satisfied(clauses, assignment):
        return True, assignment
    if any_clause_unsatisfied(clauses, assignment):
        return False, None

    var = select_unassigned_variable(clauses, assignment)
    for value in [True, False]:
        local_assignment = assignment.copy()
        local_assignment[var] = value
        sat, final_assignment = dpll(clauses, local_assignment)
        if sat:
            return True, final_assignment

    return False, None


def all_clauses_satisfied(clauses, assignment):
    for clause in clauses:
        if not any((literal > 0 and assignment.get(abs(literal), False) is True) or
                   (literal < 0 and assignment.get(abs(literal), True) is False) for literal in clause):
            return False
    return True


def any_clause_unsatisfied(clauses, assignment):
    for clause in clauses:
        if all((literal > 0 and assignment.get(abs(literal), None) is False) or
               (literal < 0 and assignment.get(abs(literal), None) is True) for literal in clause):
            return True
    return False


def select_unassigned_variable(clauses, assignment):
    for clause in clauses:
        for literal in clause:
            if abs(literal) not in assignment:
                return abs(literal)
    raise ValueError("No unassigned variables found")


def decode_solution(assignment, board_size):
    board = [[0 for _ in range(board_size)] for _ in range(board_size)]
    for var, val in assignment.items():
        if val:
            num = (var - 1) % board_size + 1
            col = ((var - 1) // board_size) % board_size
            row = (var - 1) // (board_size**2)
            board[row][col] = num
    return board


if __name__ == "__main__":
    board_size = 4
    sudoku = generate_sudoku(size=board_size, clues_to_keep=6)

    print("Puzzle:")
    print_grid(sudoku)

    start = time.time()
    clauses = encode_sudoku(board_size, sudoku)
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
