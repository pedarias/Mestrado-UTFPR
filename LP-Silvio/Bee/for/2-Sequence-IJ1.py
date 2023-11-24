j, i = 65, -2

for I in range(1, 14):  # In each interation:
    J = j - 5  # J is calculated by subtracting 5 from the current value of j.
    I = i + 3  # I is calculated by adding 3 to the current value of i
    print("I=%d J=%d" % (I, J))  # print I,J String formatting
    j = J  # j is updated to the current value of J
    i = I
