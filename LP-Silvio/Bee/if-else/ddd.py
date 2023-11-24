# -*- coding: utf-8 -*-

# Create a dictionary to map DDD codes to destinations
ddd_to_destination = {
    61: "Brasilia",
    71: "Salvador",
    11: "Sao Paulo",
    21: "Rio de Janeiro",
    32: "Juiz de Fora",
    19: "Campinas",
    27: "Vitoria",
    31: "Belo Horizonte",
}

# Read the integer DDD code from input
ddd = int(input())

# Check if the DDD code exists in the dictionary
if ddd in ddd_to_destination:
    print(ddd_to_destination[ddd])
else:
    print("DDD nao cadastrado")
