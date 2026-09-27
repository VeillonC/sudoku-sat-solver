"""
Export a Sudoku's CNF encoding to the standard DIMACS format, so it can be
fed to any off-the-shelf SAT solver (MiniSat, CaDiCaL, Glucose command-line
binaries, etc.), not just the ones implemented in this repository.
"""
from sat_solver_classic import encode_sudoku
from grid_generator import generate_sudoku, print_grid


def to_dimacs(clauses, num_vars):
    """Convert a list of clauses into a DIMACS CNF formatted string."""
    lines = [f"p cnf {num_vars} {len(clauses)}"]
    for clause in clauses:
        lines.append(" ".join(map(str, clause)) + " 0")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    board_size = 9
    sudoku = generate_sudoku(size=board_size, clues_to_keep=25)

    print("Puzzle:")
    print_grid(sudoku)

    clauses = encode_sudoku(board_size, sudoku)
    num_vars = board_size**3
    dimacs = to_dimacs(clauses, num_vars)

    output_path = "sudoku.cnf"
    with open(output_path, "w") as f:
        f.write(dimacs)

    print(f"\n{len(clauses)} clauses, {num_vars} variables")
    print(f"Written to {output_path} (DIMACS CNF format)")
