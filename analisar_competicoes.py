import csv
from pathlib import Path
from collections import Counter

base = Path(__file__).resolve().parent / "datalake" / "transfermarkt"

arquivo = base / "player_performances" / "player_performances.txt"

temporadas = [
    "15/16", "16/17", "17/18", "18/19", "19/20",
    "20/21", "21/22", "22/23", "23/24", "24/25"
]

with open(arquivo, "r", encoding="utf-8") as f:
    dados = list(csv.DictReader(f))

competicoes = Counter(
    linha["competition_name"]
    for linha in dados
    if linha["season_name"] in temporadas
)

for nome, quantidade in competicoes.most_common():
    if "premier league" in nome.lower() or "ligue 1" in nome.lower():
        print(nome, ":", quantidade)
