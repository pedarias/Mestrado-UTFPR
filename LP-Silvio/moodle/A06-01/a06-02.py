#ex01
# Valores de entrada
a = 1
b = 1.0

# Realize a conversão implícita, se necessário
soma = a + b

# Imprima o tipo da variável soma
print(type(soma))

# Imprima o valor da soma formatado como float com duas casas decimais
print(f"O valor da soma é {soma:.2f}")

#ex02
# Valores de entrada
a = 3
b = 2

# Realize a conversão de uma das variáveis para float antes de somar
soma = float(a) + b

# Imprima o tipo da variável soma
print(type(soma))

# Imprima o valor da soma formatado como float com duas casas decimais
print(f"O valor da soma é {soma:.2f}")

#ex03
# Valor de entrada
a = 1200

# Converta 'a' para float e atribua a 'b'
b = float(a)

# Converta 'a' para hexadecimal e atribua a 'c'
c = hex(a)

# Imprima os resultados
print(f"a = {a}")
print(f"O valor de 'a' convertido para o tipo 'float' é {b:.2f}")
print(f"O valor de 'a' convertido para hexadecimal é {c}")
