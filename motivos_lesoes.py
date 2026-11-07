import csv
from pathlib import Path
from collections import Counter

pasta = (
    Path(__file__).resolve().parent
    / "datalake"
    / "transfermarkt"
    / "player_injuries"
)

arquivo = pasta / "player_injuries_updated_20260929.csv"

with open(arquivo, "r", encoding="utf-8") as f:
    dados = list(csv.DictReader(f))

motivos = Counter(
    linha["injury_reason"] for linha in dados
    if linha["season_name"] in [
        "15/16", "16/17", "17/18", "18/19", "19/20",
        "20/21", "21/22", "22/23", "23/24", "24/25"
    ]
)

for motivo, quantidade in motivos.most_common():
    print(f"{motivo}: {quantidade}")

print("\nTotal de motivos diferentes:", len(motivos))
