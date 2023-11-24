# reads an unspecified number of integer values from the input until an EOFError is encountered
# For each set of input values, it calculates a value N based on the maximum value in the input list
while True:
    try:
        n = int(input())  # Read the number of elements in the list
        x = (
            input().split()
        )  # Read the list of integers as a space-separated string and split it
        m = 0  # Initialize a variable to store the maximum value

        for i in range(
            n
        ):  ## Iterate through the list of integers to find the maximum value
            if int(x[i]) > m:
                m = int(x[i])

        if m < 10:  # Determine the value of N based on the maximum value
            N = 1
        elif m >= 10 and m < 20:
            N = 2
        else:
            N = 3
        print(N)

    except EOFError:
        break

# INPUT consists of multiple sets of values, where each set begins with the number of elements in the list (n), followed by the list of integers (x)
# ex: 5
# 3 15 7 12 18
