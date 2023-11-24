def main():
    X = int(input())
    Y = int(input())
    start = (
        min(X, Y) + 1
    )  # values based on the minimum and maximum of X and Y, ensuring that start is always the smaller value.
    end = max(X, Y)
    if (
        start % 2 == 0
    ):  # ensures that the start value is odd by incrementing it if it's even.
        start += 1

    sum = 0
    for i in range(start, end, 2):
        sum += i
    print(sum)


if __name__ == "__main__":
    main()
