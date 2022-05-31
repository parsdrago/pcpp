def main():
    a: list[int] = [1, 2, 3, 4]
    s = 0
    for i in a:
        s = s + i

    if s == 10:
        return 42
    else:
        return 0
