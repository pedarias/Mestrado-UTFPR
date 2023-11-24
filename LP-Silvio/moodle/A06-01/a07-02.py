# ex01
salary = float(input("Enter the salary: "))
years_of_service = int(input("Enter the years of service: "))

if years_of_service >= 5:
    # Calculate the bonus as 5% of the salary
    bonus = salary * 0.05
    print(f"The bonus amount is $ {bonus:.2f}")
else:
    print("not eligible for a bonus.")

# ex02
print("Enter the quantity of products purchased:")
quantity = int(input())

# Calculate the total cost of the purchase (one unit costs 100.00)
total_cost = quantity * 100

if total_cost >= 1000:
    # Apply a 10% discount
    total_cost -= total_cost * 0.10

print(f"total cost of the purchase is $ {total_cost:.2f}")

# ex03
idade = int(input("Digite sua idade: "))
tem_dependentes = input("Possui dependentes? (S/N): ").upper()
e_casado = input("É casado? (S/N): ").upper()

# Verificar
if tem_dependentes == "S":
    local_de_trabalho = "áreas urbanas"
elif tem_dependentes == "N" and 20 <= idade <= 40:
    local_de_trabalho = "qualquer lugar"
elif tem_dependentes == "N" and 41 <= idade <= 60:
    local_de_trabalho = "áreas urbanas"
else:
    local_de_trabalho = "ERRO"

# Exibe o local de trabalho
if local_de_trabalho != "ERRO":
    print(f"Seu local de trabalho é em {local_de_trabalho}.")
else:
    print("ERRO")
