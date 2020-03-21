def decompose_doubles(decomposition):
    doubles = []
    current_double = []
    for i, d in enumerate(decomposition):
        if not current_double:
            current_double.append(d)
            continue

        if current_double[-1] == d:
            current_double.append(d)
        else:
            if len(current_double) >= 2:
                doubles.append(current_double)
            current_double = [d]

        if i == len(decomposition) - 1 and len(current_double) >= 2:
            doubles.append(current_double)
    return doubles


def has_double(decomposition) -> bool:
    doubles = decompose_doubles(decomposition)
    for d in doubles:
        if len(d) == 2:
            return True
    return False


def increasing(decomposition) -> bool:
    for i in range(len(decomposition) - 1):
        if decomposition[i] > decomposition[i + 1]:
            return False
    return True


def rules(decomposition):
    if len(decomposition) != 6:
        return False
    if not has_double(decomposition):
        return False
    if not increasing(decomposition):
        return False
    return True


def main():
    sat = 0
    for number in range(171309, 643604):
        decomposition = list(map(lambda x: int(x), list(str(number))))
        if rules(decomposition):
            sat += 1
    print("SAT:", sat)


if __name__ == "__main__":
    main()
