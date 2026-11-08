

import csv
from pathlib import Path
from datetime import datetime, timedelta

base = Path(__file__).resolve().parent

arquivo_lesoes = base / "player_injuries_updated_20260929.csv"
arquivo_desempenho = base / "player_performances.txt"
arquivo_transferencias = base / "transfer_history.txt"

temporadas = {
    "15/16", "16/17", "17/18", "18/19", "19/20",
    "20/21", "21/22", "22/23", "23/24", "24/25"
}

ligas = {
    "GB1": "Premier League",
    "FR1": "Ligue 1"
}


def ler(caminho):
    with open(caminho, "r", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def converter_data(valor):
    return datetime.strptime(valor[:10], "%Y-%m-%d").date()


lesoes = ler(arquivo_lesoes)
desempenho = ler(arquivo_desempenho)
transferencias = ler(arquivo_transferencias)

# Guarda os clubes em que cada jogador atuou nas ligas do projeto.
clubes_temporada = {}

for linha in desempenho:
    temporada = linha["season_name"]
    codigo_liga = linha["competition_id"]

    if temporada in temporadas and codigo_liga in ligas:
        chave = (linha["player_id"], temporada)

        if chave not in clubes_temporada:
            clubes_temporada[chave] = {}

        id_clube = linha["team_id"].strip()

        clubes_temporada[chave][id_clube] = {
            "nome": linha["team_name"].strip(),
            "liga": ligas[codigo_liga]
        }


# Guarda o histórico de transferências de cada jogador.
historico = {}

for linha in transferencias:
    try:
        data = converter_data(linha["transfer_date"])
    except (ValueError, TypeError):
        continue

    jogador = linha["player_id"]

    historico.setdefault(jogador, []).append({
        "data": data,
        "origem_id": linha["from_team_id"].strip(),
        "origem_nome": linha["from_team_name"].strip(),
        "destino_id": linha["to_team_id"].strip(),
        "destino_nome": linha["to_team_name"].strip()
    })


for jogador in historico:
    historico[jogador].sort(key=lambda x: x["data"])


# Separa uma lesão em períodos conforme as transferências.
def separar_periodos(jogador, inicio, fim):
    movimentos = historico.get(jogador, [])

    anteriores = [
        movimento for movimento in movimentos
        if movimento["data"] <= inicio
    ]

    if anteriores:
        ultimo = anteriores[-1]
        clube_id = ultimo["destino_id"]
        clube_nome = ultimo["destino_nome"]

    elif movimentos:
        primeiro = movimentos[0]
        clube_id = primeiro["origem_id"]
        clube_nome = primeiro["origem_nome"]

    else:
        return [{
            "inicio": inicio,
            "fim": fim,
            "clube_id": "",
            "clube_nome": ""
        }]

    # Guarda as mudanças de clube que acontecem durante a lesão.
    mudancas = {}

    for movimento in movimentos:
        data = movimento["data"]

        if inicio < data <= fim:
            mudancas[data] = {
                "id": movimento["destino_id"],
                "nome": movimento["destino_nome"]
            }

    periodos = []
    inicio_periodo = inicio

    for data in sorted(mudancas):
        fim_periodo = data - timedelta(days=1)

        periodos.append({
            "inicio": inicio_periodo,
            "fim": fim_periodo,
            "clube_id": clube_id,
            "clube_nome": clube_nome
        })

        clube_id = mudancas[data]["id"]
        clube_nome = mudancas[data]["nome"]
        inicio_periodo = data

    # Adiciona o último período.
    periodos.append({
        "inicio": inicio_periodo,
        "fim": fim,
        "clube_id": clube_id,
        "clube_nome": clube_nome
    })

    return periodos


resultado_ligas = []
resultado_fora = []
resultado_invalidas = []

lesoes_processadas = 0
lesoes_divididas = 0
lesoes_sem_data = 0

for numero, lesao in enumerate(lesoes, start=1):
    temporada = lesao["season_name"]
    jogador = lesao["player_id"]

    chave = (jogador, temporada)

    if temporada not in temporadas or chave not in clubes_temporada:
        continue

    try:
        inicio = converter_data(lesao["from_date"])
        fim = converter_data(lesao["end_date"])

        if fim < inicio:
            raise ValueError

    except (ValueError, TypeError):
        lesoes_sem_data += 1

        novo = lesao.copy()

        if not lesao["from_date"].strip():
            novo["motivo"] = "Data de inicio ausente"

        elif not lesao["end_date"].strip():
            novo["motivo"] = "Data final ausente"

        else:
            novo["motivo"] = "Datas invalidas"

        resultado_invalidas.append(novo)
        continue

    lesoes_processadas += 1

    periodos = separar_periodos(jogador, inicio, fim)

    if len(periodos) > 1:
        lesoes_divididas += 1

    chave = (jogador, temporada)
    clubes = clubes_temporada.get(chave, {})

    for periodo in periodos:
        clube_id = periodo["clube_id"]
        clube_nome = periodo["clube_nome"]

        dias = (
            periodo["fim"] - periodo["inicio"]
        ).days + 1

        # Verifica se o clube pertence a uma das ligas do projeto.
        if clube_id in clubes:
            informacoes = clubes[clube_id]
            status = "Identificado"
            nome_final = informacoes["nome"]
            liga_final = informacoes["liga"]

            destino = resultado_ligas

        else:
            status = "Fora das ligas analisadas"
            nome_final = clube_nome
            liga_final = ""

            destino = resultado_fora

        novo = lesao.copy()

        # Evita repetir os totais originais como se fossem de cada período.
        novo.pop("days_missed", None)
        novo.pop("games_missed", None)

        novo["id_lesao"] = numero
        novo["from_date_clube"] = periodo["inicio"].isoformat()
        novo["end_date_clube"] = periodo["fim"].isoformat()
        novo["days_missed_original"] = lesao["days_missed"]
        novo["days_missed_clube"] = dias
        novo["games_missed_total_lesao"] = lesao["games_missed"]
        novo["clube_id"] = clube_id
        novo["clube_identificado"] = nome_final
        novo["liga_identificada"] = liga_final
        novo["status_clube"] = status

        destino.append(novo)


# Salva os períodos pertencentes às ligas analisadas.
campos = [
    "id_lesao",
    "player_id",
    "season_name",
    "injury_reason",
    "from_date_clube",
    "end_date_clube",
    "days_missed_original",
    "days_missed_clube",
    "games_missed_total_lesao",
    "clube_id",
    "clube_identificado",
    "liga_identificada",
    "status_clube"
]
campos_originais = [
    "from_date",
    "end_date"
]

campos = campos_originais + campos

with open(
    base / "lesoes_distribuidas.txt",
    "w",
    newline="",
    encoding="utf-8-sig"
) as f:
    escritor = csv.DictWriter(f, fieldnames=campos)
    escritor.writeheader()
    escritor.writerows(resultado_ligas)


# Salva os períodos que aconteceram fora das ligas analisadas.
with open(
    base / "lesoes_fora_das_ligas.txt",
    "w",
    newline="",
    encoding="utf-8-sig"
) as f:
    escritor = csv.DictWriter(f, fieldnames=campos)
    escritor.writeheader()
    escritor.writerows(resultado_fora)
# Salva os registros que possuem datas invalidas.
if resultado_invalidas:
    campos_invalidos = list(resultado_invalidas[0].keys())

    with open(
        base / "lesoes_datas_invalidas.txt",
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as f:
        escritor = csv.DictWriter(
            f,
            fieldnames=campos_invalidos
        )
        escritor.writeheader()
        escritor.writerows(resultado_invalidas)

print("Lesões processadas:", lesoes_processadas)
print("Lesões divididas entre períodos:", lesoes_divididas)
print("Períodos nas ligas do projeto:", len(resultado_ligas))
print("Períodos fora das ligas:", len(resultado_fora))
print("Lesões com datas inválidas:", lesoes_sem_data)

print("\nArquivos gerados:")
print("lesoes_distribuidas.txt")
print("lesoes_fora_das_ligas.txt")
