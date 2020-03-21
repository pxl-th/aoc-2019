from pickle import dump, load
import curses
from numpy import zeros
from typing import List, Tuple
from copy import deepcopy


class AMP:
    def __init__(self, program: List[int]):
        self.halt = 99
        self.ops = {
            1: self.addition, 2: self.multiplication,
            3: self.receive, 4: self.output,
            5: self.true_jump, 6: self.false_jump,
            7: self.less_than, 8: self.equals,
            9: self.offset_relative,
        }

        self.ptr = 0
        self.relative_base = 0
        self.program = program
        self.inputs = []

    def parse_instruction(self, instruction: str) -> Tuple[int, List[int]]:
        instruction = instruction.rjust(5, "0")
        operation = int(instruction[-2:])
        modes = list(map(lambda x: int(x), reversed(instruction[:-2])))
        return operation, modes

    def fetch(self, parameter: int, mode: int) -> int:
        if mode == 0:
            return self.program[parameter]
        elif mode == 2:
            return self.program[self.relative_base + parameter]
        return parameter

    def write(self, parameter: int, value: int, mode: int) -> None:
        if mode == 0:
            self.program[parameter] = value
        elif mode == 2:
            self.program[self.relative_base + parameter] = value

    def addition(self, modes: List[int]) -> None:
        ad1 = self.fetch(self.program[self.ptr + 1], modes[0])
        ad2 = self.fetch(self.program[self.ptr + 2], modes[1])
        self.write(self.program[self.ptr + 3], ad1 + ad2, modes[2])
        self.ptr += 4

    def multiplication(self, modes: List[int]) -> None:
        ad1 = self.fetch(self.program[self.ptr + 1], modes[0])
        ad2 = self.fetch(self.program[self.ptr + 2], modes[1])
        self.write(self.program[self.ptr + 3], ad1 * ad2, modes[2])
        self.ptr += 4

    def receive(self, value: int, modes: List[int]) -> None:
        self.write(self.program[self.ptr + 1], value, modes[0])
        self.ptr += 2

    def output(self, modes: List[int]) -> int:
        value = self.fetch(self.program[self.ptr + 1], modes[0])
        self.ptr += 2
        return value

    def true_jump(self, modes: List[int]) -> None:
        if self.fetch(self.program[self.ptr + 1], modes[0]) == 0:
            self.ptr += 3
        else:
            self.ptr = self.fetch(self.program[self.ptr + 2], modes[1])

    def false_jump(self, modes: List[int]) -> None:
        if self.fetch(self.program[self.ptr + 1], modes[0]) > 0:
            self.ptr += 3
        else:
            self.ptr = self.fetch(self.program[self.ptr + 2], modes[1])

    def less_than(self, modes: List[int]) -> None:
        p1 = self.fetch(self.program[self.ptr + 1], modes[0])
        p2 = self.fetch(self.program[self.ptr + 2], modes[1])
        self.write(self.program[self.ptr + 3], 1 if p1 < p2 else 0, modes[2])
        self.ptr += 4

    def equals(self, modes: List[int]) -> None:
        p1 = self.fetch(self.program[self.ptr + 1], modes[0])
        p2 = self.fetch(self.program[self.ptr + 2], modes[1])
        self.write(self.program[self.ptr + 3], 1 if p1 == p2 else 0, modes[2])
        self.ptr += 4

    def offset_relative(self, modes: List[int]) -> None:
        parameter = self.fetch(self.program[self.ptr + 1], modes[0])
        self.relative_base += parameter
        self.ptr += 2

    def run(self):
        while self.ptr < len(self.program):
            op, modes = self.parse_instruction(str(self.program[self.ptr]))
            if op == self.halt:
                break

            if op == 3:
                yield "INP"
                self.ops[op](self.inputs.pop(0), modes)
            elif op == 4:
                yield self.ops[op](modes)
            else:
                self.ops[op](modes)


class Arcanoid:
    def __init__(self, amp: AMP):
        self.amp = amp
        self.grid_size = (21, 44)
        self.grid = zeros(self.grid_size, dtype="uint8")

        self.graphics = {0: ".", 1: "W", 2: "B", 3: "=", 4: "O"}
        self.controls = {"h": -1, "j": 0, "k": 1}

    def run(self):
        game_runner = self.amp.run()
        screen = curses.initscr()
        curses.curs_set(0)

        responses = []
        score = 0
        playing = True
        while playing:
            screen.clear()
            self._draw_grid(screen)
            screen.addstr(0, self.grid_size[1] + 5, f"SCORE: {score}")
            screen.refresh()

            if len(responses) == 3:
                x, y, tile = responses
                responses.clear()

                if x == -1 and y == 0:
                    score = tile
                    continue
                self.grid[y, x] = tile

            try:
                response = next(game_runner)
            except StopIteration:
                playing = False
                continue

            if response != "INP":
                responses.append(response)
                continue

            screen.clear()
            self._draw_grid(screen)
            screen.addstr(0, self.grid_size[1] + 5, f"SCORE: {score}")
            screen.addstr(self.grid_size[0] + 5, 0, "CONTROL")
            screen.refresh()

            control = self._input(screen)
            if control == "q":
                playing = False
                continue
            elif control == "s":
                with open("day13.arc.pkl", "wb") as f:
                    dump(self, f)
                continue
            self.amp.inputs.append(self.controls[control])

        curses.endwin()
        return score

    def _draw_grid(self, screen) -> None:
        for i in range(self.grid_size[0]):
            for j in range(self.grid_size[1]):
                screen.addch(i, j, self.graphics[self.grid[i, j]])

    def _input(self, screen) -> str:
        return chr(screen.getch())


def main():
    memory = list(zeros(10000, dtype="int32"))
    with open("day13.txt") as f:
        program = list(map(lambda x: int(x), f.readline().strip().split(",")))
    memory[:len(program)] = program
    memory[0] = 2

    amp = AMP(deepcopy(memory))
    arcanoid = Arcanoid(amp)
    # with open("day13.arc.pkl", "rb") as f:
    #     arcanoid = load(f)
    score = arcanoid.run()
    print(f"Final score: {score}")


if __name__ == "__main__":
    main()
