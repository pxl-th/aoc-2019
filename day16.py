from tqdm import tqdm


def gen(repeat: int, length: int, offset: int) -> int:
    for i in range((repeat - 1) + offset * repeat, length + 1, 4 * repeat):
        for j in range(i, min(i + repeat, length)):
            yield j


def fftop(signal: list) -> list:
    return [
        abs(
            sum(signal[one_id] for one_id in gen(i + 1, len(signal), 0))
            - sum(signal[one_id] for one_id in gen(i + 1, len(signal), 2))
        ) % 10
        for i in tqdm(range(len(signal)))
    ]


def main():
    signal_raw = (
        "597198117423867120723225095505739674216475653326673671843889973352923"
        "498529541133438047871026046640962884401354722843083733262458775939561"
        "992255160712108827286142928711317651104169998174601409558563388301180"
        "609884970973243349625433892889795350541414951714617208365250907000929"
        "018495378430818417559543608116181532004428031972863995700233558219619"
        "895957057050457422624775972939741586965947951187837673001484147023475"
        "700641396656805160531430328252882316859623593932674619323846832184134"
        "832056716364642980573035884242786534497497819370142341197572200114719"
        "501961903139039062180801786440041641226652928704955476667007810579293"
        "19060171363468213087408071790"
    ) * 10_000
    # signal_raw = "03036732577212944063491565474664" * 10_000
    offset = int(signal_raw[:7])

    signal = list(map(lambda x: int(x), signal_raw))
    for i in tqdm(range(100)):
        signal = fftop(signal)
    print("".join(map(lambda x: str(x), signal[offset:offset + 8])))


if __name__ == "__main__":
    main()
