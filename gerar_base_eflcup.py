
import csv
import re
from collections import Counter, defaultdict
from pathlib import Path

import pyreadr

import comparar_facup_todas as comparador


PASTA = Path(__file__).resolve().parent
PASTA_PROCESSADA = PASTA / "data" / "processed"
PASTA_INGLATERRA = PASTA.parent / "fontes-copas-inglaterra"

ARQUIVO_RDA = (
    PASTA.parent
    / "fontes-engsoccerdata"
    / "data"
    / "leaguecup.rda"
)

TOTAL_ESPERADO = {
    2015: 93,
    2016: 93,
    2017: 93,
    2018: 93,
    2019: 92,
    2020: 90,
    2021: 92,
    2022: 93,
    2023: 93,
    2024: 93
}

# Equivalencias entre os nomes das fontes da EFL Cup
# e os nomes utilizados na base da Premier League.
ALIAS_PREMIER_LEAGUE = {
    "leicester city": "leicester",
    "manchester city": "man city",
    "manchester united": "man united",
    "newcastle united": "newcastle",
    "norwich city": "norwich",
    "stoke city": "stoke",
    "swansea city": "swansea",
    "tottenham hotspur": "tottenham",
    "west bromwich albion": "west brom",
    "west ham united": "west ham",
    "brighton and hove albion": "brighton",
    "cardiff city": "cardiff",
    "hull city": "hull",
    "huddersfield town": "huddersfield",
    "leeds united": "leeds",
    "luton town": "luton",
    "nottingham forest": "nott'm forest",
    "wolverhampton wanderers": "wolves",
    "ipswich town": "ipswich"
}


def temporada_texto(ano):
    return f"{ano}/{ano + 1}"


def padronizar_nome(nome, nomes_base):
    normalizado = comparador.normalizar_clube(nome)

    normalizado = ALIAS_PREMIER_LEAGUE.get(
        normalizado,
        normalizado
    )

    if normalizado in nomes_base:
        return nomes_base[normalizado]

    return str(nome).strip().title()


def carregar_nomes_base():
    caminho = PASTA_PROCESSADA / "partidas_por_clube.csv"

    nomes = {}

    with open(
        caminho,
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as arquivo:
        leitor = csv.DictReader(arquivo)

        for linha in leitor:
            if linha["liga"] != "Premier League":
                continue

            nome = linha["clube"]
            chave = comparador.normalizar_clube(nome)

            nomes[chave] = nome

    return nomes


def converter_partida(partida, fonte, nomes_base, ano):
    mandante = padronizar_nome(
        partida["mandante"],
        nomes_base
    )

    visitante = padronizar_nome(
        partida["visitante"],
        nomes_base
    )

    return {
        "temporada": temporada_texto(ano),
        "data": partida["data"],
        "mandante": mandante,
        "visitante": visitante,
        "gols_mandante": int(partida["gols_mandante"]),
        "gols_visitante": int(partida["gols_visitante"]),
        "fonte": fonte,
        "status_competicao": "normal",
        "contar_como_partida": "sim"
    }


def ler_rda(ano):
    resultado = pyreadr.read_r(str(ARQUIVO_RDA))
    df = next(iter(resultado.values()))

    df = df[df["Season"] == ano].copy()

    partidas = []

    for _, linha in df.iterrows():
        partidas.append({
            "data": str(linha["Date"])[:10],
            "mandante": comparador.normalizar_clube(
                linha["home"]
            ),
            "visitante": comparador.normalizar_clube(
                linha["visitor"]
            ),
            "gols_mandante": int(linha["hgoal"]),
            "gols_visitante": int(linha["vgoal"])
        })

    return partidas


def ler_html_eflcup(caminho, ano):
    with open(caminho, "r", encoding="utf-8") as arquivo:
        linhas = arquivo.readlines()

    inicio = None
    fim = None

    for i, linha in enumerate(linhas):
        if 'name="leaguecup"' in linha:
            inicio = i + 1
            continue

        if inicio is not None and (
            "</pre>" in linha.lower()
            or "<hr" in linha.lower()
        ):
            fim = i
            break

    if inicio is None:
        raise ValueError(
            f"Secao League Cup nao encontrada: {caminho}"
        )

    if fim is None:
        fim = len(linhas)

    partidas = []
    data_atual = None
    mes_anterior = None
    ano_atual = ano

    for linha in linhas[inicio:fim]:
        linha = re.sub(r"<[^>]+>", "", linha).strip()

        datas = re.findall(
            r"\[([A-Z][a-z]{2})\s+(\d{1,2})",
            linha
        )

        if datas:
            mes_nome, dia = datas[-1]

            data_atual, mes_anterior, ano_atual = (
                comparador.atualizar_data(
                    mes_nome,
                    dia,
                    ano,
                    mes_anterior,
                    ano_atual
                )
            )

        if data_atual is None:
            continue

        confronto = comparador.separar_confronto(linha)

        if confronto is None:
            continue

        mandante, visitante, gols_a, gols_b = confronto

        partidas.append({
            "data": data_atual,
            "mandante": comparador.normalizar_clube(mandante),
            "visitante": comparador.normalizar_clube(visitante),
            "gols_mandante": gols_a,
            "gols_visitante": gols_b
        })

    return partidas


def carregar_partidas(ano):
    if 2015 <= ano <= 2017:
        partidas = ler_rda(ano)
        return partidas, "RDA"

    if ano == 2018:
        caminho = (
            PASTA_INGLATERRA
            / "2018-19"
            / "eflcup.txt"
        )

        partidas = comparador.ler_openfootball(
            str(caminho),
            ano
        )

        return partidas, "OpenFootball"

    if ano == 2019:
        caminho = (
            PASTA_INGLATERRA
            / "rsssf"
            / "eng2020-leaguecup.txt"
        )

        partidas = comparador.ler_rsssf_txt(
            str(caminho),
            ano
        )

        return partidas, "RSSSF"

    caminho = (
        PASTA_INGLATERRA
        / "rsssf"
        / f"eng{ano + 1}.html"
    )

    partidas = ler_html_eflcup(caminho, ano)

    return partidas, "RSSSF"


def salvar_csv(caminho, colunas, linhas):
    with open(
        caminho,
        "w",
        encoding="utf-8-sig",
        newline=""
    ) as arquivo:
        escritor = csv.DictWriter(
            arquivo,
            fieldnames=colunas
        )

        escritor.writeheader()
        escritor.writerows(linhas)


def validar_premier_league(partidas_por_clube):
    caminho = PASTA_PROCESSADA / "partidas_por_clube.csv"

    combinacoes_efl = {
        (linha["temporada"], linha["clube"])
        for linha in partidas_por_clube
    }

    ausentes = []

    with open(
        caminho,
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as arquivo:
        leitor = csv.DictReader(arquivo)

        for linha in leitor:
            if linha["liga"] != "Premier League":
                continue

            combinacao = (
                linha["temporada"],
                linha["clube"]
            )

            if combinacao not in combinacoes_efl:
                ausentes.append(combinacao)

    print("\n=== VALIDACAO PREMIER LEAGUE ===")

    if ausentes:
        print("Clubes-temporada sem correspondencia:")

        for temporada, clube in ausentes:
            print(f"{temporada} - {clube}")

        raise ValueError(
            f"Existem {len(ausentes)} combinacoes "
            "da Premier League sem correspondencia na EFL Cup."
        )

    print(
        "Todas as combinacoes de clubes da "
        "Premier League foram encontradas."
    )


def main():
    PASTA_PROCESSADA.mkdir(
        parents=True,
        exist_ok=True
    )

    nomes_base = carregar_nomes_base()

    todas_partidas = []
    auditoria = []

    for ano in range(2015, 2025):
        partidas_lidas, fonte = carregar_partidas(ano)

        partidas = [
            converter_partida(
                partida,
                fonte,
                nomes_base,
                ano
            )
            for partida in partidas_lidas
        ]

        esperado = TOTAL_ESPERADO[ano]

        if len(partidas) != esperado:
            raise ValueError(
                f"{temporada_texto(ano)}: "
                f"esperadas {esperado} partidas, "
                f"mas foram encontradas {len(partidas)}."
            )

        chaves = [
            (
                partida["data"],
                partida["mandante"],
                partida["visitante"]
            )
            for partida in partidas
        ]

        if len(chaves) != len(set(chaves)):
            raise ValueError(
                f"Partidas duplicadas em {temporada_texto(ano)}."
            )

        todas_partidas.extend(partidas)

        auditoria.append({
            "temporada": temporada_texto(ano),
            "fonte_principal": fonte,
            "partidas_lidas": len(partidas_lidas),
            "partidas_contabilizadas": len(partidas),
            "partidas_anuladas": 0,
            "excecoes_aplicadas": 0
        })

        print(
            f"{temporada_texto(ano)}: "
            f"{len(partidas)} partidas ({fonte})"
        )

    contagem = defaultdict(Counter)

    for partida in todas_partidas:
        temporada = partida["temporada"]

        contagem[temporada][partida["mandante"]] += 1
        contagem[temporada][partida["visitante"]] += 1

    partidas_por_clube = []

    for temporada in sorted(contagem):
        for clube, quantidade in sorted(
            contagem[temporada].items()
        ):
            partidas_por_clube.append({
                "temporada": temporada,
                "clube": clube,
                "partidas_eflcup": quantidade
            })

    total_partidas = len(todas_partidas)

    total_contagem = sum(
        linha["partidas_eflcup"]
        for linha in partidas_por_clube
    )

    if total_contagem != total_partidas * 2:
        raise ValueError(
            "Erro: a soma por clube nao corresponde "
            "ao dobro do total de partidas."
        )

    validar_premier_league(partidas_por_clube)

    salvar_csv(
        PASTA_PROCESSADA / "partidas_eflcup.csv",
        [
            "temporada",
            "data",
            "mandante",
            "visitante",
            "gols_mandante",
            "gols_visitante",
            "fonte",
            "status_competicao",
            "contar_como_partida"
        ],
        todas_partidas
    )

    salvar_csv(
        PASTA_PROCESSADA / "partidas_eflcup_por_clube.csv",
        [
            "temporada",
            "clube",
            "partidas_eflcup"
        ],
        partidas_por_clube
    )

    salvar_csv(
        PASTA_PROCESSADA / "auditoria_eflcup.csv",
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
    print(f"Total de partidas: {total_partidas}")
    print(f"Clubes-temporada: {len(partidas_por_clube)}")
    print(f"Contagem por clube: {total_contagem}")
    print(f"Validacao: {total_contagem == total_partidas * 2}")


if __name__ == "__main__":
    main()

