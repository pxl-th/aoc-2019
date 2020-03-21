from typing import List, Union


class SpaceObject:
    def __init__(self, name: str):
        self.name = name
        self.parent = None
        self.children = []

    def insert(self, around: str, child: "SpaceObject") -> bool:
        if self.name == around:
            child.parent = self
            if child not in self.children:
                self.children.append(child)
            return True

        if not self.children:
            return False
        for c in self.children:
            if c.insert(around, child):
                return True

    def __str__(self) -> str:
        description = ""
        if not self.children:
            return description
        for c in self.children:
            description += f"{self.name}){c.name}\n"
            description += str(c)
        return description

    def total_orbits(self, current_depth: int = 0) -> int:
        if not self.children:
            return current_depth
        next_depth = current_depth + 1
        for c in self.children:
            current_depth += c.total_orbits(next_depth)
        return current_depth

    def find(self, space_object: Union["SpaceObject", str]) -> "SpaceObject":
        target = (
            space_object if isinstance(space_object, str) else
            space_object.name
        )
        if self.name == target:
            return self
        if not self.children:
            return None
        for c in self.children:
            found = c.find(space_object)
            if found is not None:
                return found
        return None

    def find_path(
        self, space_object: "SpaceObject", visited: set,
    ) -> List["SpaceObject"]:
        visited.add(self)

        if self.name == space_object.name:
            return [self]
        if not self.children and (self.parent is None or self.parent in visited):
            return None

        path = [self]
        if self.parent is not None and self.parent not in visited:
            found = self.parent.find_path(space_object, visited)
            if found is not None:
                path.extend(found)
                return path

        for child in self.children:
            if child in visited:
                continue
            found = child.find_path(space_object, visited)
            if found is not None:
                path.extend(found)
                return path
        return None


def join_clusters(clusters: List[SpaceObject]):
    com: SpaceObject = None
    for i in range(len(clusters)):
        if clusters[i].name == "COM":
            com = clusters.pop(i)
            break

    i = 0
    while i < len(clusters):
        print(f"Unlinked clusters: {len(clusters)}")
        missing_link = com.find(clusters[i])
        if missing_link is None:
            i += 1
            continue

        cluster = clusters.pop(i)
        missing_link.children = list(set(cluster.children + missing_link.children))
        for j in range(len(missing_link.children)):
            missing_link.children[j].parent = missing_link
        i = 0

    return com, clusters


def main():
    with open("day6.txt") as map_file:
        orbits = [line.strip().split(")") for line in map_file.readlines()]

    clusters = []
    for i, orbit in enumerate(orbits):
        around, new_object = orbit
        if not clusters:
            clusters = [SpaceObject(around)]

        inserted = False
        for i in range(len(clusters)):
            if inserted:
                break
            inserted = clusters[i].insert(around, SpaceObject(new_object))

        if not inserted:
            clusters.append(SpaceObject(around))
            clusters[-1].insert(around, SpaceObject(new_object))

    com, clusters = join_clusters(clusters)
    print("rc:", len(clusters))
    print(com)
    print(com.total_orbits())

    you = com.find("YOU")
    san = com.find("SAN")
    print(you, you.name, you.parent.name)
    print(san, san.name, san.parent.name)

    print("[!] Finding link...")
    path = you.find_path(san, set())

    print(len(path))
    print(len(path) - 3)


if __name__ == "__main__":
    main()
