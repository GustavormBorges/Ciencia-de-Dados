import csv
from pathlib import Path
from collections import Counter

pasta = (
    Path(__file__).resolve().parents[2]
    / "datalake"
    / "transfermarkt"
    / "player_injuries"
)

arquivo = pasta / "player_injuries_updated_20260929.csv"

temporadas = [
    "15/16", "16/17", "17/18", "18/19", "19/20",
    "20/21", "21/22", "22/23", "23/24", "24/25"
]

with open(arquivo, "r", encoding="utf-8") as f:
    dados = list(csv.DictReader(f))

dados = [
    linha for linha in dados
    if linha["season_name"] in temporadas
]

def classificar(motivo):
    motivo = motivo.lower()

    if motivo in ["unknown injury", "knock", "minor knock"]:
        return "Indeterminado"

    if motivo in ["rest", "fitness", "muscle fatigue"]:
        return "Condição física ou descanso"

    if any(palavra in motivo for palavra in [
        "flu", "virus", "ill", "fever", "cancer",
        "infection", "pneumonia", "depression",
        "malaria", "covid", "corona"
    ]):
        return "Doença"

    return "Possível lesão física"

categorias = Counter(
    classificar(linha["injury_reason"])
    for linha in dados
)

for categoria, quantidade in categorias.most_common():
    print(f"{categoria}: {quantidade}")

print("\nTotal:", sum(categorias.values()))
