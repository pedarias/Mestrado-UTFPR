# Read the coordinates of the point
x, y = map(float, input().split())

# Check if the point is at the origin
if x == 0.0 and y == 0.0:
    print("Origem")

# Check if the point is on the X or Y axis
elif x == 0.0:
    print("Eixo Y")
elif y == 0.0:
    print("Eixo X")

# Check the quadrant
elif x > 0.0 and y > 0.0:
    print("Q1")
elif x < 0.0 and y > 0.0:
    print("Q2")
elif x < 0.0 and y < 0.0:
    print("Q3")
else:
    print("Q4")
