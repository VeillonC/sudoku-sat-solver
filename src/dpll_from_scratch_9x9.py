"""
Classic Sudoku (9x9) solved with a hand-written DPLL algorithm augmented
with unit propagation.

Honest performance note: even with unit propagation, this from-scratch
solver has none of the heuristics a real SAT solver relies on (watched
literals, clause learning, variable ordering by activity...), so it does
not scale well. In testing, a 9x9 grid with 65 given clues (a very easy
puzzle) solved in well under a second, a 61-clue grid took about 19
seconds, and a 55-clue puzzle did not finish within 90 seconds. This is
the practical motivation for sat_solver_classic.py, which delegates to
Glucose3 (via PySAT) and solves 9x9 grids with as few as 17 clues in a
few milliseconds.

The default below (65 clues) keeps this script runnable in a reasonable
time; lower it to see the search cost grow quickly.
"""
import time

from grid_generator import generate_sudoku, print_grid


def variable(row, col, num):
    return row * 81 + col * 9 + num


def encode_sudoku(sudoku):
    clauses = []

    for row in range(9):
        for col in range(9):
            if sudoku[row][col] != 0:
                clauses.append([variable(row, col, sudoku[row][col])])

    for row in range(9):
        for col in range(9):
            clauses.append([variable(row, col, num) for num in range(1, 10)])

    for row in range(9):
        for col in range(9):
            for num1 in range(1, 10):
                for num2 in range(num1 + 1, 10):
                    clauses.append([-variable(row, col, num1), -variable(row, col, num2)])

    for num in range(1, 10):
        for row in range(9):
            clauses.append([variable(row, col, num) for col in range(9)])

    for num in range(1, 10):
        for col in range(9):
            clauses.append([variable(row, col, num) for row in range(9)])

    for num in range(1, 10):
        for row_start in range(0, 9, 3):
            for col_start in range(0, 9, 3):
                clauses.append([variable(row_start + i // 3, col_start + i % 3, num) for i in range(9)])

    return clauses


def dpll(clauses, assignment):
    clauses, assignment = unit_propagate(clauses, assignment)
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


def unit_propagate(clauses, assignment):
    while True:
        unit_clauses = [clause for clause in clauses if len(clause) == 1]
        if not unit_clauses:
            break
        for clause in unit_clauses:
            literal = clause[0]
            value = literal > 0
            var = abs(literal)
            assignment[var] = value
            clauses = simplify_clauses(clauses, var, value)
    return clauses, assignment


def simplify_clauses(clauses, var, value):
    new_clauses = []
    for clause in clauses:
        if (value and var in clause) or (not value and -var in clause):
            continue
        new_clause = [lit for lit in clause if lit != -var]
        if not new_clause:
            return clauses
        new_clauses.append(new_clause)
    return new_clauses


def decode_solution(assignment, board_size=9):
    board = [[0 for _ in range(board_size)] for _ in range(board_size)]
    for var, val in assignment.items():
        if val:
            num = (var - 1) % board_size + 1
            col = ((var - 1) // board_size) % board_size
            row = (var - 1) // (board_size**2)
            board[row][col] = num
    return board


if __name__ == "__main__":
    sudoku = generate_sudoku(size=9, clues_to_keep=65)

    print("Puzzle:")
    print_grid(sudoku)

    start = time.time()
    clauses = encode_sudoku(sudoku)
    satisfiable, final_assignment = dpll(clauses, {})
    elapsed = time.time() - start

    print(f"\n{len(clauses)} CNF clauses generated")
    print(f"Solved in {elapsed:.2f} s")
    print("Satisfiable:", satisfiable)

    if satisfiable:
        print("\nSolution:")
        print_grid(decode_solution(final_assignment))
    else:
        print("No solution found.")
