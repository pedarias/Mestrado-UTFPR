import math

# Valores de entrada
valores = [5.5, 5.1, 5.9, -5.9, -5.2]

# Loop através dos valores e calcular o menor inteiro menor ou igual a cada um
for valor in valores:
    resultado = math.floor(valor)
    print(f"{resultado}")
