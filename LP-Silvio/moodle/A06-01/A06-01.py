import math

#Exerc01
# Valores de entrada
valores = [5.5, 5.1, 5.9, -5.9, -5.2]

# Loop através dos valores e calcular o menor inteiro maior ou igual a cada um
for valor in valores:
    resultado = math.ceil(valor)
    print(f"{resultado}")

#Exerc02
# Valores de entrada
valores = [5.5, 5.1, 5.9, -5.9, -5.2]

# Loop através dos valores e calcular o menor inteiro menor ou igual a cada um
for valor in valores:
    resultado = math.floor(valor)
    print(f"{resultado}")

#Exerc03
# Defina os valores de a, b e c
a = 10
b = 2
c = 15

# Calcule o valor absoluto de 'a'
valor_absoluto_a = abs(a)

# Calcule o exponencial de 'b'
exponencial_b = math.exp(b)

# Calcule o valor absoluto de 'a' como um float
valor_absoluto_a_float = float(valor_absoluto_a)

# Calcule o fatorial de 'c'
fatorial_c = math.factorial(c)

# Calcule o logaritmo de 'c' na base 2
logaritmo_base_2 = math.log(c, 2)

# Calcule o logaritmo de 'c' na base 4
logaritmo_base_4 = math.log(c, 4)

# Imprima os resultados
print(f"a = {a}")
print(f"b = {b}")
print(f"c = {c}")
print(f"O valor absoluto de 'a' é {valor_absoluto_a}.")
print(f"O exponencial de 'b' é {exponencial_b}")
print(f"O valor absoluto de 'a' é {valor_absoluto_a_float}")
print(f"O fatorial de 'c' é {fatorial_c}")
print(f"O logaritmo de 'c' na base 2 é {logaritmo_base_2}")
print(f"O logaritmo de 'c' na base 4 é {logaritmo_base_4}")
