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


def receive(program: List[int], ptr: int, modes: List[int]) -> int:
    value = input("enter integer:")
    write(program, program[ptr + 1], int(value))
    return ptr + 2


def output(program: List[int], ptr: int, modes: List[int]) -> int:
    value = fetch(program, program[ptr + 1], modes[0])
    print(value)
    return ptr + 2


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


def whats_a_computer(program: List[int]):
    halt = 99
    ops = {
        1: addition,
        2: multiplication,
        3: receive,
        4: output,
        5: true_jump,
        6: false_jump,
        7: less_than,
        8: equals,
    }

    ptr = 0
    while ptr < len(program):
        operation, modes = parse_instruction(str(program[ptr]))
        if operation == halt:
            break
        ptr = ops[operation](program, ptr, modes)
    return program


def main():
    programs = [
        [
            3,21,1008,21,8,20,1005,20,22,107,8,21,20,1006,20,31,
            1106,0,36,98,0,0,1002,21,125,20,4,20,1105,1,46,104,
            999,1105,1,46,1101,1000,1,20,4,20,1105,1,46,98,99,
        ],
    ]
    for program in programs:
        output = whats_a_computer(program)


if __name__ == "__main__":
    main()
