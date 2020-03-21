from numpy import fromfile, array


def test():
    masses = fromfile(
        r"C:\Users\tonys\projects\python\aoc\day1-input.txt", sep="\n",
        dtype="int64",
    )
    # masses = array([12, 14, 1969, 100756], dtype="int64")
    total = masses // 3 - 2
    remainder = total.copy()

    while (remainder != 0).any():
        remainder = remainder // 3 - 2
        remainder[remainder < 0] = 0
        total += remainder

    print(total.sum())


if __name__ == "__main__":
    test()
