from math import gcd
from functools import reduce
from numpy import array, ndarray, zeros_like, vectorize, abs
from tqdm import tqdm


def lcm(denominators):
    return reduce(lambda a, b: a * b // gcd(a, b), denominators)


def parse_input(position: str) -> list:
    return list(map(
        lambda x: int(x[2:]),
        position.strip().strip("<>").split(", ")
    ))


def spaceship(x, y):  # because i'm using python 3.7 instead of 3.8
    if x == y:
        return 0
    return -1 if x < y else 1


def apply_gravity(positions: ndarray, velocities: ndarray) -> ndarray:
    sp = vectorize(spaceship)
    for i, position in enumerate(positions):
        velocities[i] += (sp(position, positions) * -1).sum(axis=0)
    return velocities


def calculate_energy(positions: ndarray, velocities: ndarray) -> ndarray:
    potential = abs(positions).sum(axis=1)
    kinetic = abs(velocities).sum(axis=1)
    return (potential * kinetic).sum()


def main():
    positions = """
    <x=15, y=-2, z=-6>
    <x=-5, y=-4, z=-11>
    <x=0, y=-6, z=0>
    <x=5, y=9, z=6>
    """
    positions = array([
        parse_input(p) for p in positions.strip().split("\n") if p
    ])
    velocities = zeros_like(positions)

    cycles = []
    for i in tqdm(range(3)):
        tmp_positions = positions[:, i].copy()
        tmp_velocities = velocities[:, i].copy()
        init_position = tmp_positions.copy()
        init_velocity = tmp_velocities.copy()

        steps = 0
        cycle = False
        while not cycle:
            steps += 1
            tmp_velocities = apply_gravity(tmp_positions, tmp_velocities)
            tmp_positions += tmp_velocities
            cycle = (
                (tmp_positions == init_position).all()
                and (tmp_velocities == init_velocity).all()
            )
            if cycle:
                cycles.append(steps)

    # energy = calculate_energy(positions, velocities)

    total_cycle = reduce(lambda x, y: x * y, cycles)
    print(cycles, total_cycle)
    print(lcm(cycles))


if __name__ == "__main__":
    main()
