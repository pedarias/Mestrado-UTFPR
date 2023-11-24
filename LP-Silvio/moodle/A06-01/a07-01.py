#ex01
a = int(input())
b = int(input())

if b > a:
    print("b é maior que a")
elif a == b:
    print("a e b são iguais")

#ex02
a = int(input())
b = int(input())

if b > a:
    print("b é maior que a")
elif a == b:
    print("a e b são iguais")
else:
    print("a é maior que b")

#ex03
a = int(input())
b = int(input())
c = int(input())

if a > b and a > c:
    print("Ambas as condições são verdadeiras")

#ex04
a = int(input())
b = int(input())
c = int(input())

if a > b or a > c:
    print("pelo menos uma das condições é verdadeira")

#ex05
a = int(input())
b = int(input())

if not a > b:
    print("a não é maior que b")

#ex06
valor = int(input("Digite o valor: "))

if valor > 10:
    print("Maior que 10")
    if valor > 20:
        print("E também maior que 20")
    else:
        print("Mas menor que 20")

