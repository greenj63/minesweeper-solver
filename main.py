# Solves a minesweeper board of nxn dimension with x bombs
"""
Algorithm Details:

Two lists will be used: an "active" list and a "resolved" list

Each iteration will take nodes from the active list and determine the
number of non-number neighbors it has. This excludes all mines. If the number of
non-number neighbors is the same as the node, all neighbors will be marked as
mines and this node is resolved.

There will be another check for the number of known mines next to the node.
If this number is the same as the node, the node will be marked as resolved and all
non-mine neighbors will be revealed.

When a node is revealed, it is immediately placed on the active list. Its value comes from the
solved board in generate_board.

1) Automatically reveal a safe node.
2) Select a node in the active list. If no node exists, end the program
3) Check if the node has the same number of non-number neighbors and mines as its number.
    If so, mark mines and resolve.
4) Otherwise, check if the node has the same number of neighboring mines as its number.
    If so, reveal all non-mine neighbors and resolve this node.
5) If a node has not been resolved this iteration, return to step 2.
6) If no nodes could be resolved in active list, randomly guess and try again.
7) If the board is solved, print the board. If not, an extra mine was marked somewhere.

"""

import random as rnd
from copy import deepcopy

# Constants
MINE: str = "X"
BLANK: str = "_"
FAIL: str = "*"


class MinesweeperBoard:
    # Member Variables
    # board: list[list[str]]
    # solution: list[list[str]]
    # n: int
    # mine_count: int

    def __init__(self, n: int, mine_count: int) -> None:
        self.n: int = n
        self.mine_count: int = mine_count

        # Define a board state
        self.board: list[list[str]] = []
        self.solution: list[list[str]] = []

        # Generate a board of all unique values
        for y in range(n):
            row = []
            for x in range(n):
                row.append(BLANK)
            self.solution.append(row)

        # Copy blank board into working copy
        self.board = deepcopy(self.solution)

        # Generate mines
        while mine_count > 0:
            # Find a random location
            x = rnd.randint(0, n - 1)
            y = rnd.randint(0, n - 1)

            # Check if it is a mine. If not, place a mine
            if self.solution[y][x] != MINE:
                self.solution[y][x] = MINE
                mine_count -= 1

        # Determine number of mine neighbors for each slot and place number
        for y in range(n):
            for x in range(n):
                if self.solution[y][x] != MINE:
                    mine_neighbors = self._find_neighbors_of(x, y, MINE, self.solution)
                    self.solution[y][x] = str(mine_neighbors)

    def _find_neighbors_of(self, x: int, y: int, cat: str = MINE, board=None) -> int:
        # Set default board
        if board is None:
            board = self.board

        # Track total observed count
        obs = 0

        # Check all possible positions
        for yn in range(y - 1, y + 2):
            for xn in range(x - 1, x + 2):
                if self._is_in_bounds(xn, yn):
                    if board[yn][xn] == cat:
                        obs += 1

        # Return the number of observed neighbors
        return obs

    def _is_in_bounds(self, x: int, y: int) -> bool:
        return (0 <= x < self.n) and (0 <= y < self.n)

    def __str__(self) -> str:
        board_str = ""
        for row in self.board:
            for char in row:
                if char == "0":
                    char = ' '
                board_str += f"{char} "
            board_str += "\n"

        return board_str

    def print(self) -> None:
        width = (self.n + 2) * 2 - 1
        print("=" * width)
        for row in self.board:
            print("| ", end="")
            for char in row:
                if char == "0":
                    char = " "
                print(f"{char} ", end="")
            print("|")
        print("=" * width)

    def _print_answer(self):
        width = (self.n + 2) * 2 - 1
        print("=" * width)
        for row in self.solution:
            print("| ", end="")
            for char in row:
                if char == "0":
                    char = " "
                print(f"{char} ", end="")
            print("|")
        print("=" * width)

    def solve(self) -> bool:
        active: list[tuple[int, int]] = []  # List of active nodes

        # Step 1: Add a random solved node to the active list
        while len(active) == 0:
            # Find a random spot, reveal it if it's not a mine
            x = rnd.randint(1, self.n - 1)
            y = rnd.randint(1, self.n - 1)

            if self.solution[y][x] != MINE:
                self._reveal(x, y)
                active.append((y, x))

        # Step 2: Select a node in the active list if one exists
        while len(active) > 0 or not self.is_solved():
            change_occurred = False
            for node in active:
                # Extract components from board
                y = node[0]
                x = node[1]
                num = int(self.board[y][x])

                # Find blank and mines counts
                num_blanks = self._find_neighbors_of(x, y, BLANK)
                num_mines = self._find_neighbors_of(x, y, MINE)

                # Step 3: Check the number of neighboring blanks and mark all blanks if mines capped
                if num == num_blanks + num_mines:
                    self._mark_neighbors(x, y)
                    active.remove(node)
                    change_occurred = True
                    break

                # Step 4: Check the number of neighboring mines and reveal all blanks if
                if num == num_mines:
                    revealed_spots = self._reveal_neighbors(x, y)

                    # Check if a mine was found
                    for yn, xn in revealed_spots:
                        # Check if the reveal was successful
                        if self.board[yn][xn] == MINE:
                            self._mark_fail(xn, yn, "Bad Reveal")
                            return False
                        else:
                            active.append((yn, xn))

                    active.remove(node)
                    change_occurred = True
                    break

                # Step 5: If no change can be made, check the next node (Repeat For)

            # No node could make a change occur. Randomly guess if board isn't already solved
            if not change_occurred and not self.is_solved():
                pos = self._guess(active)
                guess = self.board[pos[0]][pos[1]]

                # If the guess was good, add it to the active list!
                if guess != MINE:
                    active.append(pos)
                else:
                    self._mark_fail(pos[1], pos[0], "Incorrect Guess")
                    return False

        # Step 7: If the board is solved, print it with success. Otherwise failure
        if self.is_solved():
            self._win()
            return True
        else:
            self._lose("Still spots left to expand!")
            return False

    # Returns true if all blanks have been expanded, false otherwise
    def is_solved(self):
        for row in self.board:
            for cell in row:
                if cell == BLANK:
                    return False

        return True

    # Places the component from board at [y][x] on the solution.
    # Returns true if reveal was a success, false if a mine was hit
    def _reveal(self, x: int, y: int) -> tuple[int, int]:
        # Sanity check
        if not self._is_in_bounds(x, y):
            return -1, -1

        # Copy into the board
        self.board[y][x] = self.solution[y][x]
        return y, x

    def _reveal_neighbors(self, x: int, y: int) -> list[tuple[int, int]]:
        revealed_list = []
        for yn in range(y - 1, y + 2):
            for xn in range(x - 1, x + 2):
                # Reveal the spot if the neighbor was a blank
                if self._is_in_bounds(xn, yn) and self.board[yn][xn] == BLANK:
                    node = self._reveal(xn, yn)
                    revealed_list.append(node)

        return revealed_list

    def _guess(self, active: list[tuple[int, int]]) -> tuple[int, int]:
        # Find a low numbered cell and expand one of its neighbors
        for num in range(1, 8):
            # Extract cell coordinates
            for y, x in active:
                # Check if the cell is one of the numbers to be checked
                cell = self.board[y][x]
                if str(num) == cell:
                    # Find one of its neighbors and reveal it
                    for yn in range(y - 1, y + 2):
                        for xn in range(x - 1, x + 2):
                            if self._is_in_bounds(xn, yn) and self.board[yn][xn] == BLANK:
                                return self._reveal(xn, yn)


        # No good options (Failsafe
        # Pick random spots until one of them is blank, then expand it
        while True:
            x = rnd.randint(1, self.n - 1)
            y = rnd.randint(1, self.n - 1)

            if self.board[y][x] == BLANK:
                return self._reveal(x, y)

    def _mark(self, x: int, y: int) -> None:
        # Sanity check
        if not self._is_in_bounds(x, y):
            return

        self.board[y][x] = MINE

    def _mark_neighbors(self, x: int, y: int) -> None:
        for yn in range(y - 1, y + 2):
            for xn in range(x - 1, x + 2):
                # Reveal the spot if the neighbor was a blank
                if self._is_in_bounds(xn, yn) and self.board[yn][xn] == BLANK:
                    self._mark(xn, yn)

    def _mark_fail(self, x: int, y: int, reason="Mine Exploded") -> None:
        # Sanity Check
        if not self._is_in_bounds(x, y):
            return

        self.board[y][x] = FAIL
        self._lose(reason)

    def _lose(self, reason="Mine Exploded") -> None:
        print(f"Failure -> {reason}")
        print("Final Board State:")
        self.print()
        print()
        print("Intended Solution:")
        self._print_answer()
        print()

    def _win(self) -> None:
        print("Solution Found!")
        self.print()
        print()


def main():
    # Set random seed
    seed = 42
    rnd.seed(seed)

    # Find a board that breaks
    while not MinesweeperBoard(45, 225).solve():
        seed += 1
        rnd.seed(seed)
    print(f"Seed: {seed}")


if __name__ == "__main__":
    main()
