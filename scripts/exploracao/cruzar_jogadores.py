
import csv
from pathlib import Path

base = Path(__file__).resolve().parents[2] / "football-datasets-main" / "datalake" / "transfermarkt"

arquivo_desempenho = base / "player_performances" / "player_performances.txt"
arquivo_lesoes = base / "player_injuries" / "player_injuries_updated_20260929.csv"

temporadas = [
    "15/16", "16/17", "17/18", "18/19", "19/20",
    "20/21", "21/22", "22/23", "23/24", "24/25"
]

ligas = ["Premier League", "Ligue 1"]

with open(arquivo_desempenho, "r", encoding="utf-8-sig") as f:
    desempenho = list(csv.DictReader(f))

with open(arquivo_lesoes, "r", encoding="utf-8-sig") as f:
    lesoes = list(csv.DictReader(f))

desempenho = [
    linha for linha in desempenho
    if linha["season_name"] in temporadas
    and linha["competition_name"] in ligas
]

lesoes = [
    linha for linha in lesoes
    if linha["season_name"] in temporadas
]

jogadores_ligas = set(
    linha["player_id"] for linha in desempenho
)

jogadores_lesoes = set(
    linha["player_id"] for linha in lesoes
)

jogadores_com_lesao = jogadores_ligas & jogadores_lesoes

print("Jogadores nas duas ligas:", len(jogadores_ligas))
print("Jogadores com histórico de lesões:", len(jogadores_com_lesao))
print("Jogadores sem registro de lesão:", len(jogadores_ligas - jogadores_lesoes))

total_lesoes = sum(
    1 for linha in lesoes
    if linha["player_id"] in jogadores_ligas
)

print("Registros de afastamento encontrados:", total_lesoes)

print("\nRegistros por liga:")

for liga in ligas:
    jogadores = set(
        linha["player_id"] for linha in desempenho
        if linha["competition_name"] == liga
    )

    registros = sum(
        1 for linha in lesoes
        if linha["player_id"] in jogadores
    )

    print(liga, ":", registros)
