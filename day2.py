def mod_op(opcode: list, noun: int, verb: int) -> list:
    opcode[1] = noun
    opcode[2] = verb
    return opcode


def test(opcode: list):
    add = 1
    mul = 2
    halt = 99
    for i in range(0, len(opcode), 4):
        if opcode[i] == halt:
            break
        if opcode[i] == add:
            opcode[opcode[i + 3]] = opcode[opcode[i + 1]] + opcode[opcode[i + 2]]
        elif opcode[i] == mul:
            opcode[opcode[i + 3]] = opcode[opcode[i + 1]] * opcode[opcode[i + 2]]
        else:
            break

    return opcode


if __name__ == "__main__":
    # test([1, 0, 0, 0, 99])
    # test([2, 3, 0, 3, 99])
    # test([2, 4, 4, 5, 99, 0])
    # test([1, 1, 1, 4, 99, 5, 6, 0, 99])

    target = 19690720
    input_opcode = [1,0,0,3,1,1,2,3,1,3,4,3,1,5,0,3,2,1,6,19,1,19,5,23,2,13,23,27,1,10,27,31,2,6,31,35,1,9,35,39,2,10,39,43,1,43,9,47,1,47,9,51,2,10,51,55,1,55,9,59,1,59,5,63,1,63,6,67,2,6,67,71,2,10,71,75,1,75,5,79,1,9,79,83,2,83,10,87,1,87,6,91,1,13,91,95,2,10,95,99,1,99,6,103,2,13,103,107,1,107,2,111,1,111,9,0,99,2,14,0,0]
    found = False
    for noun in range(100):
        if found:
            break

        for verb in range(100):
            result = test(mod_op(input_opcode[:], noun, verb))
            if result[0] == target:
                print(f"noun: {noun}, verb: {verb}")
                print(f"answer: {100 * noun + verb}")
                found = True
                break
