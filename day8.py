from numpy import array, argmin, logical_and


def main():
    height, width = 6, 25
    with open("day8.txt") as f:
        img_str = f.readline().strip()
    raw_img = array(list(map(lambda x: int(x), img_str)), dtype="uint8")
    img = raw_img.reshape((-1, height, width))

    zeros = (img == 0).sum((1, 2))
    layer_id = argmin(zeros)
    channel = img[layer_id]
    result = (channel == 1).sum() * (channel == 2).sum()
    print(result)

    transparency = img[0] == 2
    final_img = img[0]

    current_layer = 1
    while transparency.sum() >= 0 and current_layer < img.shape[0]:
        final_img[transparency] = img[current_layer][transparency]
        transparency = logical_and(transparency, img[current_layer] == 2)
        current_layer += 1

    print("*****")
    print(final_img)


if __name__ == "__main__":
    main()
