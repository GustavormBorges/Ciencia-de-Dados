import csv
from pathlib import Path
from collections import Counter

base = Path(__file__).resolve().parents[2] / "datalake" / "transfermarkt"

arquivo = base / "player_performances" / "player_performances.txt"

temporadas = [
    "15/16", "16/17", "17/18", "18/19", "19/20",
    "20/21", "21/22", "22/23", "23/24", "24/25"
]

ligas = ["Premier League", "Ligue 1"]

with open(arquivo, "r", encoding="utf-8") as f:
    dados = list(csv.DictReader(f))

filtrados = [
    linha for linha in dados
    if linha["season_name"] in temporadas
    and linha["competition_name"] in ligas
]

print("Total de registros:", len(filtrados))

for liga in ligas:
    registros = [
        linha for linha in filtrados
        if linha["competition_name"] == liga
    ]

    jogadores = set(linha["player_id"] for linha in registros)
    clubes = set(linha["team_name"] for linha in registros)

    print("\nLiga:", liga)
    print("Registros:", len(registros))
    print("Jogadores:", len(jogadores))
    print("Clubes:", len(clubes))

    print("\nRegistros por temporada:")

    contagem = Counter(linha["season_name"] for linha in registros)

    for temporada in temporadas:
        print(temporada, ":", contagem[temporada])
