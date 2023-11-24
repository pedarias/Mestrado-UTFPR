import math

# Valores de entrada
valores = [5.5, 5.1, 5.9, -5.9, -5.2]

# Loop através dos valores e calcular o menor inteiro maior ou igual a cada um
for valor in valores:
    resultado = math.ceil(valor)
    print(f"{resultado}")
