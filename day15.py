from pickle import dump, load
import curses
from numpy import array, full, zeros, argwhere, ndarray, full_like
from typing import List, Tuple
from copy import deepcopy
from tqdm import tqdm


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


class DroidControl:
    def __init__(self, amp: AMP):
        self.amp = amp
        self.grid_size = (50, 150)
        self.grid = full(self.grid_size, 1)
        self.position = array([25, 75])

        self.graphics = {0: "#", 1: ".", 2: "O"}
        self.controls = {"w": 1, "s": 2, "a": 3, "d": 4}
        self.control_inputs = {
            "w": [-1, 0], "s": [1, 0], "a": [0, -1], "d": [0, 1],
        }

    def run(self):
        droid_runner = self.amp.run()
        screen = curses.initscr()
        curses.curs_set(0)

        screen.clear()
        self._draw_grid(screen)
        screen.refresh()

        responses = []
        score = 0
        searching = True
        last_move = None
        while searching:
            if responses:
                response = responses.pop()
                if response == 0:
                    wall = self.position + self.control_inputs[last_move]
                    self.grid[wall[0], wall[1]] = 0
                else:
                    self.position += self.control_inputs[last_move]
                    if response == 2:
                        self.grid[self.position[0], self.position[1]] = 2

            screen.clear()
            self._draw_grid(screen)
            screen.refresh()

            try:
                response = next(droid_runner)
            except StopIteration:
                searching = False
                continue

            if response != "INP":
                responses.append(response)
                continue

            control = self._input(screen)
            if control == "q":
                searching = False
                continue
            elif control == "j":
                with open("day15.save.pkl", "wb") as f:
                    dump(self, f)
                continue

            last_move = control
            self.amp.inputs.append(self.controls[control])

        curses.endwin()
        return score

    def _draw_grid(self, screen) -> None:
        for i in range(self.grid_size[0]):
            for j in range(self.grid_size[1]):
                screen.addch(i, j, self.graphics[self.grid[i, j]])
        screen.addch(self.position[0], self.position[1], "D")
        screen.addch(25, 75, "S")

    def _input(self, screen) -> str:
        return chr(screen.getch())


def find_path(
    droid: DroidControl, visited: ndarray,
    start: ndarray, end: ndarray, step: int = 0,
):
    visited[start[0], start[1]] = True

    if (start == end).all():
        return step
    elif droid.grid[start[0], start[1]] == 0:
        return None

    for turn in droid.control_inputs.values():
        next_tile = start + turn
        if visited[next_tile[0], next_tile[1]]:
            continue
        turn_tile = find_path(
            droid, visited, start=next_tile, end=end, step=step + 1,
        )
        if turn_tile is not None:
            return turn_tile
    return None


def main():
    memory = list(zeros(10000, dtype="int32"))
    with open("day15.txt") as f:
        program = list(map(lambda x: int(x), f.readline().strip().split(",")))
    memory[:len(program)] = program

    # amp = AMP(deepcopy(memory))
    # droid = DroidControl(amp)
    # droid.run()
    with open("day15.save.pkl", "rb") as f:
        droid: DroidControl = load(f)

    droid.grid[25, 75] = 4
    walls = argwhere(droid.grid == 0)
    droid.grid = droid.grid[
        min(walls[:, 0]):max(walls[:, 0]) + 1,
        min(walls[:, 1]):max(walls[:, 1]) + 1,
    ]
    visited = full_like(droid.grid, False, dtype=bool)
    start = argwhere(droid.grid == 4)[0]
    target = argwhere(droid.grid == 2)[0]
    path_length = find_path(droid, visited, start=start, end=target)
    print(path_length)

    max_distance = 0
    open_spaces = argwhere(droid.grid == 1)
    start = argwhere(droid.grid == 2)[0]
    for space in tqdm(open_spaces):
        visited = full_like(droid.grid, False, dtype=bool)
        path_length = find_path(droid, visited, start, space)
        if path_length is not None and max_distance < path_length:
            max_distance = path_length
    print(max_distance)


if __name__ == "__main__":
    main()
