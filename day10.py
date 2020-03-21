from typing import Tuple
from numpy import (
    array, ndarray, logical_or, isclose, full, logical_and,
    argwhere, argmin, dot, arctan2, pi, argsort, argmax,
)
from numpy.linalg import norm
from tqdm import tqdm


def parse_map(raw_map: str) -> Tuple[ndarray, ndarray]:
    raw_map = map(lambda x: x.strip(), raw_map.split("\n"))
    raw_map = [x for x in raw_map if x]
    raw_map = array([[obj for obj in x] for x in raw_map])
    return raw_map, argwhere(raw_map == "#")


def on_line(l1: ndarray, l2: ndarray, p: ndarray) -> ndarray:
    line_distance = norm(l1 - l2)
    point_line_distance = norm(p - l1, axis=1) + norm(p - l2, axis=1)
    return isclose(point_line_distance, line_distance)


def closest(main_asteroid: ndarray, choices: ndarray) -> int:
    distances = norm(choices - main_asteroid, axis=1)
    return argmin(distances)


def count_asteroids(asteroids: ndarray, main_asteroid: ndarray):
    in_sight = 0
    mask = (asteroids != main_asteroid).any(1)
    asteroids = asteroids[mask]

    visible = []

    processed = full(mask.shape[0] - 1, False)
    for asteroid in asteroids:
        lined_asteroids = on_line(main_asteroid, asteroid, asteroids)
        lined_asteroids_num = lined_asteroids.sum()

        in_line = logical_and(lined_asteroids, ~processed)
        in_line_num = in_line.sum()
        if lined_asteroids_num != in_line_num:
            continue

        if in_line_num == 1:
            visible.append(asteroids[in_line].tolist()[0])
        elif in_line_num > 1:
            closest_id = closest(main_asteroid, asteroids[in_line])
            visible.append(asteroids[in_line][closest_id].tolist())

        in_sight += min(1, in_line_num)
        processed = logical_or(processed, lined_asteroids)

    return in_sight, array(visible)


def angle(origin: ndarray, points: ndarray) -> Tuple[ndarray, ndarray]:
    reference = array([0, 1], dtype="float32")

    points_vectors = (points - origin).reshape((-1, 2))
    distances = norm(points_vectors, axis=1)

    non_zero_mask = ~isclose(distances, 0)
    points_vectors[non_zero_mask] = (
        points_vectors[non_zero_mask]
        / distances.reshape((-1, 1))[non_zero_mask]
    )

    dot_product = dot(points_vectors, reference)
    diff_product = (
        reference[1] * points_vectors[:, 0]
        - reference[0] * points_vectors[:, 1]
    )

    angles = arctan2(diff_product, dot_product)
    negative_angle_mask = angles < 0
    angles[negative_angle_mask] = 2 * pi + angles[negative_angle_mask]
    angles[~non_zero_mask] = 0
    return angles, distances


def main():
    amap = """
    #.#.###.#.#....#..##.#....
    .....#..#..#..#.#..#.....#
    .##.##.##.##.##..#...#...#
    #.#...#.#####...###.#.#.#.
    .#####.###.#.#.####.#####.
    #.#.#.##.#.##...####.#.##.
    ##....###..#.#..#..#..###.
    ..##....#.#...##.#.#...###
    #.....#.#######..##.##.#..
    #.###.#..###.#.#..##.....#
    ##.#.#.##.#......#####..##
    #..##.#.##..###.##.###..##
    #..#.###...#.#...#..#.##.#
    .#..#.#....###.#.#..##.#.#
    #.##.#####..###...#.###.##
    #...##..#..##.##.#.##..###
    #.#.###.###.....####.##..#
    ######....#.##....###.#..#
    ..##.#.####.....###..##.#.
    #..#..#...#.####..######..
    #####.##...#.#....#....#.#
    .#####.##.#.#####..##.#...
    #..##..##.#.##.##.####..##
    .##..####..#..####.#######
    #.#..#.##.#.######....##..
    .#.##.##.####......#.##.##
    """
    raw_map, asteroids = parse_map(amap)
    visible = [count_asteroids(asteroids, m)[0] for m in tqdm(asteroids)]
    target_id = argmax(visible)
    main_asteroid = asteroids[target_id]
    print(main_asteroid, visible[target_id])

    mask, objects = count_asteroids(asteroids, main_asteroid)
    angles = angle(main_asteroid.astype("float32"), objects.astype("float32"))[0]
    angles += pi / 2
    angles -= 2 * pi
    angles[angles < 0] = 2 * pi + angles[angles < 0]
    sorted_ids = argsort(angles)

    final = objects[sorted_ids[199]]
    print(f"{final[1] * 100 + final[0]}")


if __name__ == "__main__":
    main()
