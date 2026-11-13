
import csv
from pathlib import Path

pasta = Path(__file__).resolve().parents[2] / "data" / "interim"


def ler(arquivo):
    with open(pasta / arquivo, encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


dentro = ler("lesoes_distribuidas.csv")
fora = ler("lesoes_fora_das_ligas.csv")
invalidas = ler("lesoes_datas_invalidas.csv")

registros = dentro + fora

# 1. Confere se os dias originais foram preservados.
lesoes = {}

for linha in registros:
    identificador = linha["id_lesao"]

    if identificador not in lesoes:
        lesoes[identificador] = {
            "original": float(linha["days_missed_original"]),
            "distribuido": 0
        }

    lesoes[identificador]["distribuido"] += int(
        linha["days_missed_clube"]
    )

diferencas = []

for identificador, dados in lesoes.items():
    if dados["original"] != dados["distribuido"]:
        diferencas.append(identificador)


# 2. Conta clubes e temporadas.
clubes = set()
temporadas = set()
ligas = set()
status = set()

for linha in dentro:
    clubes.add(linha["clube_id"])
    temporadas.add(linha["season_name"])
    ligas.add(linha["liga_identificada"])
    status.add(linha["status_clube"])


# 3. Procura períodos duplicados.
periodos = {}

for linha in registros:
    chave = (
        linha["id_lesao"],
        linha["clube_id"],
        linha["from_date_clube"],
        linha["end_date_clube"]
    )

    if chave not in periodos:
        periodos[chave] = 0

    periodos[chave] += 1

duplicados = 0

for quantidade in periodos.values():
    if quantidade > 1:
        duplicados += 1


# 4. Confere os registros com datas inválidas.
motivos = {}

for linha in invalidas:
    motivo = linha["motivo"]

    if motivo not in motivos:
        motivos[motivo] = 0

    motivos[motivo] += 1


# 5. Mostra os resultados.
print("=== VALIDACAO DA BASE DE LESOES ===")

print("\nQuantidade de registros:")
print("Lesoes originais com periodos:", len(lesoes))
print("Periodos gerados:", len(registros))
print("Periodos nas ligas:", len(dentro))
print("Periodos fora das ligas:", len(fora))
print("Datas invalidas:", len(invalidas))

print("\nConferencia dos dias:")
print("Lesoes com diferenca nos dias:", len(diferencas))

print("\nInformacoes das ligas:")
print("Clubes diferentes:", len(clubes))
print("Temporadas:", sorted(temporadas))
print("Ligas:", sorted(ligas))
print("Status encontrados:", sorted(status))

print("\nConferencia de duplicados:")
print("Periodos duplicados:", duplicados)

print("\nMotivos das datas invalidas:")
for motivo, quantidade in motivos.items():
    print(motivo, ":", quantidade)