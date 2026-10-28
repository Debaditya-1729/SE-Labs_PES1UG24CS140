from board import Board


class Game:
    def __init__(self):
        self.board = Board()
        self.best_score = 0
        self.history = None

    def display(self):
        print("\n" + "+------+------+------+------+")

        for row in self.board.grid:
            print(
                "|"
                + "|".join(
                    f"{x:^6}" if x else f"{' ':^6}"
                    for x in row
                )
                + "|"
            )

            print("+------+------+------+------+")

        print("Score:", self.board.score, " Best:", self.best_score)

    def move(self, key):
        moves = {
            "a": self.board.move_left,
            "d": self.board.move_right,
            "w": self.board.move_up,
            "s": self.board.move_down,
        }

        if key not in moves:
            return False, False

        previous_grid = [row[:] for row in self.board.grid]
        previous_score = self.board.score

        changed = moves[key]()

        if not changed:
            return False, False

        self.history = (
            previous_grid,
            previous_score,
        )

        merged = self.board.score > previous_score

        self.board.add_random_tile()

        self.best_score = max(
            self.best_score,
            self.board.score,
        )

        return True, merged

    def undo(self):
        if self.history is None:
            return False

        previous_grid, previous_score = self.history

        self.board.grid = [row[:] for row in previous_grid]
        self.board.score = previous_score

        self.history = None

        return True

    def run(self):
        print("2048 — W/A/S/D to move, U to undo, Q to quit.")

        while True:
            self.display()

            if self.board.has_won():
                print("You reached 2048!")
                return

            if not self.board.can_move():
                print("No legal moves remain.")
                return

            key = input("> ").strip().lower()

            if key == "q":
                return

            if key == "u":
                if self.undo():
                    print("Move undone.")
                else:
                    print("Nothing to undo.")
                continue

            if key not in "wasd":
                print("Use W/A/S/D.")
                continue

            successful, merged = self.move(key)

            if not successful:
                print("Move did not change the board.")
            else:
                direction = {
                    "w": "up",
                    "a": "left",
                    "s": "down",
                    "d": "right",
                }[key]

                if merged:
                    print(f"Moved {direction} — tiles merged.")
                else:
                    print(f"Moved {direction}.")