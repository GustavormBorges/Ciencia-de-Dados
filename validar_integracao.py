
import csv
from pathlib import Path

base = Path(__file__).resolve().parent


def ler(arquivo):
    with open(base / arquivo, encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


integrada = ler("data/processed/base_integrada.csv")
lesoes = ler("lesoes_distribuidas.txt")

# Verifica combinações duplicadas.
combinacoes = set()

for linha in integrada:
    chave = (
        linha["liga"],
        linha["temporada"],
        linha["clube"]
    )
    combinacoes.add(chave)

# Confere os totais de dias.
dias_lesoes = 0

for linha in lesoes:
    dias_lesoes += int(linha["days_missed_clube"])

dias_integrados = 0

for linha in integrada:
    dias_integrados += int(linha["dias_ausencia"])

# Confere a quantidade de partidas.
partidas_invalidas = 0

for linha in integrada:
    if int(linha["partidas"]) <= 0:
        partidas_invalidas += 1

# Conta clubes sem lesões registradas.
clubes_sem_lesoes = 0

for linha in integrada:
    if int(linha["quantidade_lesoes"]) == 0:
        clubes_sem_lesoes += 1

# Verifica valores negativos.
valores_negativos = 0

for linha in integrada:
    if (
        int(linha["partidas"]) < 0
        or int(linha["quantidade_lesoes"]) < 0
        or int(linha["dias_ausencia"]) < 0
    ):
        valores_negativos += 1


print("=== VALIDACAO DA INTEGRACAO ===")

print("Linhas na base:", len(integrada))
print("Combinações diferentes:", len(combinacoes))
print("Combinações duplicadas:", len(integrada) - len(combinacoes))

print("\nConferência dos dias:")
print("Dias na base de lesões:", dias_lesoes)
print("Dias na base integrada:", dias_integrados)
print("Diferença:", dias_lesoes - dias_integrados)

print("\nOutras verificações:")
print("Linhas sem partidas válidas:", partidas_invalidas)
print("Clubes sem lesões registradas:", clubes_sem_lesoes)
print("Linhas com valores negativos:", valores_negativos)
