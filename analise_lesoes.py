import csv
from pathlib import Path

pasta = (
    Path(__file__).resolve().parent
    / "datalake"
    / "transfermarkt"
    / "player_injuries"
)

arquivos = [
    "player_injuries.csv",
    "player_injuries_updated_20260929.csv"
]

temporadas_desejadas = [
    "15/16", "16/17", "17/18", "18/19", "19/20",
    "20/21", "21/22", "22/23", "23/24", "24/25"
]

for nome in arquivos:
    caminho = pasta / nome

    with open(caminho, "r", encoding="utf-8") as arquivo:
        dados = list(csv.DictReader(arquivo))

    temporadas = set(
        linha["season_name"] for linha in dados
    )

    print("\n" + "=" * 40)
    print("Arquivo:", nome)
    print("Total de registros:", len(dados))
    print("Temporadas disponíveis:", len(temporadas))

    print("\nRegistros por temporada:")

    for temporada in temporadas_desejadas:
        quantidade = sum(
            1 for linha in dados
            if linha["season_name"] == temporada
        )
        print(f"{temporada}: {quantidade}")

    total = sum(
        1 for linha in dados
        if linha["season_name"] in temporadas_desejadas
    )

    print("\nTotal no período:", total)

print("\nAnálise concluída!")
