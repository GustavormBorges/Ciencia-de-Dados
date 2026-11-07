import csv
from pathlib import Path

base = Path(__file__).resolve().parent / "datalake" / "transfermarkt"

arquivos = {
    "LESOES": base / "player_injuries" / "player_injuries_updated_20260929.csv",
    "DESEMPENHO": base / "player_performances" / "player_performances.txt",
    "TRANSFERENCIAS": base / "transfer_history" / "transfer_history.txt"
}

for nome, caminho in arquivos.items():
    print("\n", "=" * 50)
    print(nome)
    print("=" * 50)

    with open(caminho, "r", encoding="utf-8") as arquivo:
        leitor = csv.DictReader(arquivo)

        print("Colunas:", leitor.fieldnames)

        for i, linha in enumerate(leitor):
            if i == 2:
                break
            print(linha)
