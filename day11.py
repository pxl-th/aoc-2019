"""
modes:
    0 - position mode
    1 - immediate mode
    2 - relative mode (can read and write to)
        count from 'relative base'
        rb + param
instruction:
    XXXX|OP: OP - operation, XXXX modes
        read from right to left
        default mode = 0
operaitons:
    1 - add
    2 - multiply
    3 - input from user and stores it at its value parameter
    4 - output value of its parameter (4, 50) -- prints value at address 50
"""
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
                self.ops[op](self.inputs.pop(0), modes)
            elif op == 4:
                yield self.ops[op](modes)
            else:
                self.ops[op](modes)


def main():
    from numpy import zeros, array, cos, sin, pi, savetxt
    grid = zeros((200, 200), dtype="uint8")
    painted = zeros((200, 200), dtype="uint8")
    position = array([100, 100])
    direction = array([1, 0])

    right_rotation = array([
        [cos(pi / 2), -sin(pi / 2)], [sin(pi / 2), cos(pi / 2)]
    ])
    left_rotation = array([
        [cos(-pi / 2), -sin(-pi / 2)], [sin(-pi / 2), cos(-pi / 2)]
    ])

    memory = list(zeros(10000, dtype="int32"))
    with open("day11.txt") as f:
        program = list(map(lambda x: int(x), f.readline().strip().split(",")))
    memory[:len(program)] = program
    amp = AMP(deepcopy(memory))
    grid[position[0], position[1]] = 1
    amp.inputs.append(grid[position[0], position[1]])

    print("working...")
    paint = True
    for output in amp.run():
        if paint:
            grid[position[0], position[1]] = output
            painted[position[0], position[1]] = 1
        else:
            if output == 0:
                direction = left_rotation.dot(direction).astype("int32")
            else:
                direction = right_rotation.dot(direction).astype("int32")
            position += direction
            amp.inputs.append(grid[position[0], position[1]])

        paint = not paint

    savetxt("day11-out.txt", grid[::-1], fmt="%d")
    print(painted.sum())


if __name__ == "__main__":
    main()
