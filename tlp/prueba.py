import random

opciones = ["Ganar $1", "Ganar $10", "Ganar el Premio Mayor"]
# Definimos los pesos (probabilidades relativas)
pesos = [80, 19, 1] 

# Simulamos 100 sorteos sesgados
resultados = random.choices(opciones, weights=pesos, k=100)
print(resultados)