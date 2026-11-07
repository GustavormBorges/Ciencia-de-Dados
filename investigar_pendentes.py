import csv
from pathlib import Path

pasta = Path(__file__).resolve().parent

with open(pasta / "lesoes_com_clube.txt", encoding="utf-8-sig") as f:
    lesoes = list(csv.DictReader(f))

pendentes = [
    linha for linha in lesoes
    if linha["status_clube"] == "Revisar"
]

saida = pasta / "lesoes_pendentes.txt"

with open(saida, "w", newline="", encoding="utf-8-sig") as f:
    campos = list(pendentes[0].keys())
    escritor = csv.DictWriter(f, fieldnames=campos)
    escritor.writeheader()
    escritor.writerows(pendentes)

print("Registros pendentes:", len(pendentes))
print("Arquivo gerado:", saida)