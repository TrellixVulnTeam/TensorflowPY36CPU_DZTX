import os


def main():
    root_dir = "C:\\temp"

    files = get_files(root_dir)
    print("Found these files")
    for f in files:
        print(f)
    print('done')


def get_files(root_dir):
    for item in os.listdir(root_dir):
        if item == '.DS_Store':
            continue

        full_item = os.path.join(root_dir, item)
        if os.path.isfile(full_item):
            yield full_item
        elif os.path.isdir(full_item):
            # old skool style loop
            # for f in get_files(full_item):
            #     yield f
            # new recursive yield style
            yield from get_files(full_item)


if __name__ == '__main__':
    main()
