# The code generates a pattern of values for I and J where I starts at 0 and increases by 0.2 every three iterations, while J starts at 1 and increases by 1 in each iteration.
# The format of the output changes every five iterations, alternating between integer and one decimal place formatting for I and J. The loop continues until i exceeds 2.
i = 0
j = 1
value = 0
temp = 0
temp2 = 0
while i <= 2:
    if temp2 == 0:
        print(
            "I=%.0f J=%.0f" % (i, j)
        )  # if temp2 = 0, prints the values of I and J with no decimal places
    else:
        print("I=%.1f J=%.1f" % (i, j))  # Otherwise, it prints with one decimal place

    temp += 1  # Incremented by 1 in each iteration.
    if temp == 3:  # When temp reaches 3, the following actions occur:
        i += 0.2
        value += 0.2
        j = value
        temp = 0
        temp2 += 1  # The code generates a pattern of values for I and J where I starts at 0 and increases by 0.2 every three iterations, while J starts at 1 and increases by 1 in each iteration.

    if (
        temp2 == 5
    ):  # The format of the output changes every five iterations, alternating between integer and one decimal place formatting for I and J. The loop continues until i exceeds 2
        temp2 = 0
    j += 1
