
import csv
from collections import Counter, defaultdict
from pathlib import Path

import comparar_facup_todas as comparador


PASTA = Path(__file__).resolve().parent
PASTA_PROCESSADA = PASTA / "data" / "processed"

PASTA_INGLATERRA = (
    PASTA / comparador.PASTA_INGLATERRA
).resolve()

PASTA_RSSSF = PASTA_INGLATERRA / "rsssf"

ARQUIVO_EXCECOES = PASTA / "excecoes_facup.csv"


NOMES_PREMIER_LEAGUE = {
    "manchester city": "Man City",
    "manchester united": "Man United",
    "nottingham forest": "Nott'm Forest",
    "huddersfield town": "Huddersfield",
    "hull city": "Hull",
    "cardiff city": "Cardiff",
    "leicester city": "Leicester",
    "west bromwich albion": "West Brom",
    "wolverhampton wanderers": "Wolves",
    "brighton and hove albion": "Brighton",
    "newcastle united": "Newcastle",
    "tottenham hotspur": "Tottenham",
    "west ham united": "West Ham",
    "stoke city": "Stoke",
    "swansea city": "Swansea",
    "norwich city": "Norwich",
    "ipswich town": "Ipswich",
    "leeds united": "Leeds",
    "luton town": "Luton",
}


def nome_padronizado(nome):
    nome = comparador.normalizar_clube(nome)

    if nome in NOMES_PREMIER_LEAGUE:
        return NOMES_PREMIER_LEAGUE[nome]

    return nome.title().replace("'S", "'s")


def carregar_excecoes():
    excecoes = {}

    with open(
        ARQUIVO_EXCECOES,
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as arquivo:
        leitor = csv.DictReader(arquivo, delimiter=";")

        for linha in leitor:
            clubes = sorted([
                comparador.normalizar_clube(linha["mandante"]),
                comparador.normalizar_clube(linha["visitante"])
            ])

            chave = (
                linha["data"],
                clubes[0],
                clubes[1]
            )

            excecoes[chave] = linha

    return excecoes


def carregar_partidas(ano):
    if ano <= 2017:
        partidas = comparador.ler_rda()

        partidas = [
            partida for partida in partidas
            if partida["temporada"] == ano
        ]

        return partidas, "RDA"

    if ano == 2018:
        caminho = (
            PASTA_INGLATERRA / "2018-19" / "facup.txt"
        )

        return (
            comparador.ler_openfootball(str(caminho), ano),
            "OpenFootball"
        )

    if ano == 2019:
        caminho = PASTA_RSSSF / "eng2020-facup.txt"

        return (
            comparador.ler_rsssf_txt(str(caminho), ano),
            "RSSSF"
        )

    if ano in (2020, 2021):
        temporada = f"{ano}-{str(ano + 1)[-2:]}"
        caminho = PASTA_INGLATERRA / temporada / "facup.txt"

        return (
            comparador.ler_openfootball(str(caminho), ano),
            "OpenFootball"
        )

    caminho = PASTA_RSSSF / f"eng{ano + 1}.html"

    return (
        comparador.ler_rsssf_html(str(caminho), ano),
        "RSSSF"
    )


def criar_chave(partida):
    clubes = sorted([
        comparador.normalizar_clube(partida["mandante"]),
        comparador.normalizar_clube(partida["visitante"])
    ])

    return (
        partida["data"],
        clubes[0],
        clubes[1]
    )


def aplicar_excecoes(partidas, fonte, excecoes):
    resultado = []
    excecoes_aplicadas = set()

    for partida in partidas:
        chave = criar_chave(partida)

        linha_excecao = excecoes.get(chave)

        gols_mandante = partida["gols_mandante"]
        gols_visitante = partida["gols_visitante"]
        status = "normal"
        contar = "sim"
        fonte_final = fonte

        if linha_excecao is not None:
            placar = linha_excecao["placar_final"].split("-")

            gols_mandante = int(placar[0])
            gols_visitante = int(placar[1])

            status = linha_excecao["status_competicao"]
            contar = linha_excecao["contar_como_partida"]
            fonte_final = linha_excecao["fonte_escolhida"]

            excecoes_aplicadas.add(chave)

        resultado.append({
            "data": partida["data"],
            "mandante": nome_padronizado(partida["mandante"]),
            "visitante": nome_padronizado(partida["visitante"]),
            "gols_mandante": gols_mandante,
            "gols_visitante": gols_visitante,
            "fonte": fonte_final,
            "status_competicao": status,
            "contar_como_partida": contar
        })

    return resultado, excecoes_aplicadas


def salvar_csv(caminho, campos, linhas):
    with open(
        caminho,
        "w",
        encoding="utf-8-sig",
        newline=""
    ) as arquivo:
        escritor = csv.DictWriter(
            arquivo,
            fieldnames=campos
        )

        escritor.writeheader()
        escritor.writerows(linhas)


def main():
    PASTA_PROCESSADA.mkdir(parents=True, exist_ok=True)

    excecoes = carregar_excecoes()

    todas_partidas = []
    auditoria = []
    excecoes_aplicadas_total = set()

    for ano in range(2015, 2025):
        temporada = f"{ano}/{ano + 1}"

        partidas, fonte = carregar_partidas(ano)

        partidas, excecoes_aplicadas = aplicar_excecoes(
            partidas,
            fonte,
            excecoes
        )

        for partida in partidas:
            partida["temporada"] = temporada

        todas_partidas.extend(partidas)
        excecoes_aplicadas_total.update(excecoes_aplicadas)

        anuladas = sum(
            1 for partida in partidas
            if partida["status_competicao"] == "anulada"
        )

        auditoria.append({
            "temporada": temporada,
            "fonte_principal": fonte,
            "partidas_lidas": len(partidas),
            "partidas_contabilizadas": sum(
                1 for partida in partidas
                if partida["contar_como_partida"] == "sim"
            ),
            "partidas_anuladas": anuladas,
            "excecoes_aplicadas": len(excecoes_aplicadas)
        })

        print(
            f"{temporada}: {len(partidas)} partidas "
            f"({fonte})"
        )

    if len(excecoes_aplicadas_total) != len(excecoes):
        faltantes = set(excecoes) - excecoes_aplicadas_total

        raise ValueError(
            "Nem todas as excecoes foram encontradas "
            f"nas fontes escolhidas: {faltantes}"
        )

    chaves = [criar_chave(p) for p in todas_partidas]

    duplicadas = [
        chave for chave, quantidade in Counter(chaves).items()
        if quantidade > 1
    ]

    if duplicadas:
        raise ValueError(
            f"Foram encontradas partidas duplicadas: {duplicadas}"
        )

    campos_partidas = [
        "temporada",
        "data",
        "mandante",
        "visitante",
        "gols_mandante",
        "gols_visitante",
        "fonte",
        "status_competicao",
        "contar_como_partida"
    ]

    salvar_csv(
        PASTA_PROCESSADA / "partidas_facup.csv",
        campos_partidas,
        todas_partidas
    )

    contagens = defaultdict(int)

    for partida in todas_partidas:
        if partida["contar_como_partida"] != "sim":
            continue

        temporada = partida["temporada"]

        contagens[(temporada, partida["mandante"])] += 1
        contagens[(temporada, partida["visitante"])] += 1

    partidas_por_clube = []

    for (temporada, clube), quantidade in sorted(contagens.items()):
        partidas_por_clube.append({
            "temporada": temporada,
            "clube": clube,
            "partidas_facup": quantidade
        })

    salvar_csv(
        PASTA_PROCESSADA / "partidas_facup_por_clube.csv",
        ["temporada", "clube", "partidas_facup"],
        partidas_por_clube
    )

    salvar_csv(
        PASTA_PROCESSADA / "auditoria_facup.csv",
        [
            "temporada",
            "fonte_principal",
            "partidas_lidas",
            "partidas_contabilizadas",
            "partidas_anuladas",
            "excecoes_aplicadas"
        ],
        auditoria
    )

    print("\nGERACAO CONCLUIDA")
    print("Total de partidas:", len(todas_partidas))
    print("Clubes-temporada:", len(partidas_por_clube))
    print("Excecoes aplicadas:", len(excecoes_aplicadas_total))
    print(
        "Partidas anuladas:",
        sum(
            1 for p in todas_partidas
            if p["status_competicao"] == "anulada"
        )
    )


if __name__ == "__main__":
    main()
