def fib(n):
    if n == 1:
        return 1
    if n == 2:
        return 1
    return fib(n - 1) + fib(n - 2)


def main():
    if fib(12) == 144:
        return 42
    return 1
