"""
modes:
    0 - position mode
    1 - immediate mode
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
from itertools import permutations
from copy import deepcopy


def parse_instruction(instruction: str) -> Tuple[int, List[int]]:
    instruction = instruction.rjust(4, "0")
    operation = int(instruction[-2:])
    modes = list(map(lambda x: int(x), reversed(instruction[:-2])))
    return operation, modes


def fetch(program: List[int], parameter: int, mode: int) -> int:
    return program[parameter] if mode == 0 else parameter


def write(program: List[int], ptr: int, value: int) -> List[int]:
    program[ptr] = value
    return program


def addition(program: List[int], ptr: int, modes: List[int]) -> int:
    ad1 = fetch(program, program[ptr + 1], modes[0])
    ad2 = fetch(program, program[ptr + 2], modes[1])
    write(program, program[ptr + 3], ad1 + ad2)
    return ptr + 4


def multiplication(program: List[int], ptr: int, modes: List[int]) -> int:
    ad1 = fetch(program, program[ptr + 1], modes[0])
    ad2 = fetch(program, program[ptr + 2], modes[1])
    write(program, program[ptr + 3], ad1 * ad2)
    return ptr + 4


def receive(program: List[int], ptr: int, modes: List[int], value: int) -> int:
    write(program, program[ptr + 1], value)
    return ptr + 2


def output(program: List[int], ptr: int, modes: List[int]) -> Tuple[int, int]:
    value = fetch(program, program[ptr + 1], modes[0])
    return ptr + 2, value


def true_jump(program: List[int], ptr: int, modes: List[int]) -> int:
    if fetch(program, program[ptr + 1], modes[0]) == 0:
        return ptr + 3
    return fetch(program, program[ptr + 2], modes[1])


def false_jump(program: List[int], ptr: int, modes: List[int]) -> int:
    if fetch(program, program[ptr + 1], modes[0]) > 0:
        return ptr + 3
    return fetch(program, program[ptr + 2], modes[1])


def less_than(program: List[int], ptr: int, modes: List[int]) -> int:
    p1 = fetch(program, program[ptr + 1], modes[0])
    p2 = fetch(program, program[ptr + 2], modes[1])
    write(program, program[ptr + 3], 1 if p1 < p2 else 0)
    return ptr + 4


def equals(program: List[int], ptr: int, modes: List[int]) -> int:
    p1 = fetch(program, program[ptr + 1], modes[0])
    p2 = fetch(program, program[ptr + 2], modes[1])
    write(program, program[ptr + 3], 1 if p1 == p2 else 0)
    return ptr + 4


class AMP:
    def __init__(self, program: List[int]):
        self.halt = 99
        self.ops = {
            1: addition,
            2: multiplication,
            3: receive,
            4: output,
            5: true_jump,
            6: false_jump,
            7: less_than,
            8: equals,
        }

        self.ptr = 0
        self.program = program

    def run(self, inputs: List[str]):
        while self.ptr < len(self.program):
            operation, modes = parse_instruction(str(self.program[self.ptr]))
            if operation == self.halt:
                break

            argv = [inputs.pop(0)] if operation == 3 else []
            self.ptr = self.ops[operation](self.program, self.ptr, modes, *argv)

            if operation == 4:
                self.ptr, op_output = self.ptr
                return [op_output]
                # inputs.append(op_output)
        return self.halt


def main():
    amplifiers = 5
    program = [3,52,1001,52,-5,52,3,53,1,52,56,54,1007,54,5,55,1005,55,26,1001,54,-5,54,1105,1,12,1,53,54,53,1008,54,0,55,1001,55,1,55,2,53,55,53,4,53,1001,56,-1,56,1005,56,6,99,0,0,0,0,10]
    phases_sequences = permutations(range(5, 10), amplifiers)

    thrusts = []
    for phase_seq in phases_sequences:
        outputs = [0]
        amps = [AMP(deepcopy(program)) for _ in range(amplifiers)]

        output_amplifier = None
        halted = False
        loop = 0
        while not halted:
            for i in range(amplifiers):
                inputs = [phase_seq[i]] + outputs if loop == 0 else outputs
                outputs = amps[i].run(inputs)
                if i == amplifiers - 1:
                    output_amplifier = outputs
                if outputs == 99:
                    halted = True
                    break
            loop += 1

        thrusts.append(output_amplifier)

    max_thrust = max(thrusts)
    print(f"[*] Max thrust: {max_thrust}")


if __name__ == "__main__":
    main()
