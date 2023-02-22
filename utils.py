from os import makedirs, path


def check_folder(folder):
    if not path.exists(folder):
        makedirs(folder)


def write_msg(msg):
    i = 1
    check_folder("results")
    while path.exists(f"results/results{i}.txt"):
        i += 1

    with open(f"results/results{i}.txt", "w") as f:
        f.write(msg)
        print(msg)
