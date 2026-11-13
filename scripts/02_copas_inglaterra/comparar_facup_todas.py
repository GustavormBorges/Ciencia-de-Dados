
import re
import unicodedata
from collections import Counter

import pyreadr


PASTA_INGLATERRA = "../fontes-copas-inglaterra"
PASTA_RSSSF = PASTA_INGLATERRA + "/rsssf"


MESES = {
    "Jan": 1, "Feb": 2, "Mar": 3,
    "Apr": 4, "May": 5, "Jun": 6,
    "Jul": 7, "Aug": 8, "Sep": 9,
    "Oct": 10, "Nov": 11, "Dec": 12
}


def normalizar_clube(nome):
    nome = str(nome).lower().strip()
    nome = nome.replace("&", "and")

    nome = unicodedata.normalize("NFKD", nome)
    nome = "".join(
        caractere for caractere in nome
        if not unicodedata.combining(caractere)
    )

    nome = nome.replace(".", "")
    nome = re.sub(r"\b(fc|afc)\b", "", nome)
    nome = re.sub(r"\s+", " ", nome).strip()

    equivalencias = {
        "yeovil": "yeovil town",
        "accrington": "accrington stanley",
        "cheltenham town": "cheltenham",
        "stevenage": "stevenage borough",
        "mk dons": "milton keynes dons",
        "spennymoor town": "spennymoor",
        "spennymoor united": "spennymoor",
        "solihull moors": "solihull",
        "st albans city": "st albans",
        "macclesfield town": "macclesfield",
        "hereford united": "hereford",
        "billericay": "billericay town",
        "hampton and richmond": "hampton and richmond borough",
        "hampton and richmond bgh": "hampton and richmond borough",
        "king's lynn": "king's lynn town",
        "cray valley pm": "cray valley paper mills",
        "shefffield united": "sheffield united",
        "rushall olympics": "rushall olympic",
        "hayes and yeading": "hayes and yeading united",
    }

    return equivalencias.get(nome, nome)


def criar_data(mes_nome, dia, ano):
    mes = MESES[mes_nome]

    return f"{ano}-{mes:02d}-{int(dia):02d}"


def atualizar_data(mes_nome, dia, ano_temporada,
                   mes_anterior=None, ano_atual=None):
    mes = MESES[mes_nome]

    if ano_atual is None:
        ano_atual = ano_temporada

    if mes_anterior is not None:
        if mes < mes_anterior:
            ano_atual += 1

    return criar_data(mes_nome, dia, ano_atual), mes, ano_atual


def separar_confronto(linha):
    resultado = re.search(r"(\d+)-(\d+)", linha)

    if resultado is None:
        return None

    # Identifica partidas decididas nos pênaltis.
    # O placar depois de "pen." é o resultado da disputa.
    # O placar depois de "a.e.t." é o resultado da partida.
    resultado_prorrogacao = re.search(
        r"(\d+)-(\d+)\s+pen\.\s*"
        r"(\d+)-(\d+)\s+a\.e\.t\.",
        linha,
        flags=re.IGNORECASE
    )

    antes = linha[:resultado.start()].strip()
    depois = linha[resultado.end():].strip()

    gols_a = int(resultado.group(1))
    gols_b = int(resultado.group(2))

    if resultado_prorrogacao is not None:
        gols_a = int(resultado_prorrogacao.group(3))
        gols_b = int(resultado_prorrogacao.group(4))

    # Formato OpenFootball: Time A v Time B 2-1 (1-0).
    if re.search(r"\s+v\s+", antes):
        clubes = re.split(r"\s+v\s+", antes, maxsplit=1)

        if len(clubes) != 2:
            return None

        mandante = clubes[0].strip()
        visitante = clubes[1].strip()

        mandante = re.sub(
            r"^\d{1,2}:\d{2}\s+",
            "",
            mandante
        )

        return mandante, visitante, gols_a, gols_b

    # Formato RSSSF: Time A 2-1 Time B [aet].
    mandante = antes
    visitante = depois

    visitante = re.sub(
        r"\s*[\[(].*[\])]\s*$",
        "",
        visitante
    ).strip()

    if not mandante or not visitante:
        return None

    return mandante, visitante, gols_a, gols_b


def ler_openfootball(caminho, ano):
    with open(caminho, "r", encoding="utf-8-sig") as arquivo:
        linhas = arquivo.readlines()

    partidas = []
    data_atual = None
    mes_anterior = None
    ano_atual = ano

    for linha in linhas:
        linha = linha.strip()

        data = re.match(
            r"^(?:(?:Mon|Tue|Wed|Thu|Fri|Sat|Sun)\s+)?"
            r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)"
            r"\s+(\d{1,2})(?:\s+(\d{4}))?$",
            linha
        )

        if data:
            mes_nome = data.group(1)
            dia = data.group(2)
            ano_explicito = data.group(3)

            if ano_explicito is not None:
                ano_atual = int(ano_explicito)
                mes_anterior = MESES[mes_nome]

                data_atual = criar_data(
                    mes_nome, dia, ano_atual
                )
            else:
                data_atual, mes_anterior, ano_atual = atualizar_data(
                    mes_nome,
                    dia,
                    ano,
                    mes_anterior,
                    ano_atual
                )

            continue

        if data_atual is None or "v" not in linha:
            continue

        confronto = separar_confronto(linha)

        if confronto is None:
            continue

        mandante, visitante, gols_a, gols_b = confronto

        partidas.append({
            "data": data_atual,
            "mandante": normalizar_clube(mandante),
            "visitante": normalizar_clube(visitante),
            "gols_mandante": gols_a,
            "gols_visitante": gols_b
        })

    return partidas


def ler_rsssf_html(caminho, ano):
    with open(caminho, "r", encoding="utf-8") as arquivo:
        linhas = arquivo.readlines()

    inicio = None
    fim = None

    for i, linha in enumerate(linhas):
        if 'name="facup"' in linha:
            inicio = i + 1

        elif inicio is not None and 'name="leaguecup"' in linha:
            fim = i
            break

    if inicio is None or fim is None:
        raise ValueError(
            f"Nao foi possivel localizar a secao FA Cup em {caminho}"
        )

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

            data_atual, mes_anterior, ano_atual = atualizar_data(
                mes_nome,
                dia,
                ano,
                mes_anterior,
                ano_atual
            )

        if data_atual is None:
            continue

        confronto = separar_confronto(linha)

        if confronto is None:
            continue

        mandante, visitante, gols_a, gols_b = confronto

        partidas.append({
            "data": data_atual,
            "mandante": normalizar_clube(mandante),
            "visitante": normalizar_clube(visitante),
            "gols_mandante": gols_a,
            "gols_visitante": gols_b
        })

    return partidas


def ler_rsssf_txt(caminho, ano):
    with open(caminho, "r", encoding="utf-8-sig") as arquivo:
        linhas = arquivo.readlines()

    partidas = []
    data_atual = None
    mes_anterior = None
    ano_atual = ano

    for linha in linhas:
        linha = linha.strip()

        # Aceita datas como "Jul 18" e "Jul 18 @ London".
        data = re.match(
            r"^(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)"
            r"\s+(\d{1,2})(?:\s+@.*)?$",
            linha
        )

        if data:
            mes_nome = data.group(1)
            dia = data.group(2)

            data_atual, mes_anterior, ano_atual = atualizar_data(
                mes_nome,
                dia,
                ano,
                mes_anterior,
                ano_atual
            )

            continue

        if data_atual is None:
            continue

        confronto = separar_confronto(linha)

        if confronto is None:
            continue

        mandante, visitante, gols_a, gols_b = confronto

        partidas.append({
            "data": data_atual,
            "mandante": normalizar_clube(mandante),
            "visitante": normalizar_clube(visitante),
            "gols_mandante": gols_a,
            "gols_visitante": gols_b
        })

    return partidas


def ler_rda():
    resultado = pyreadr.read_r(
        "../fontes-engsoccerdata/data/facup.rda"
    )

    df = next(iter(resultado.values()))
    df = df[df["Season"].between(2015, 2018)].copy()

    partidas = []

    for _, linha in df.iterrows():
        partidas.append({
            "temporada": int(linha["Season"]),
            "data": str(linha["Date"])[:10],
            "mandante": normalizar_clube(linha["home"]),
            "visitante": normalizar_clube(linha["visitor"]),
            "gols_mandante": int(linha["hgoal"]),
            "gols_visitante": int(linha["vgoal"])
        })

    return partidas


def criar_chave(partida):
    clubes = sorted([
        partida["mandante"],
        partida["visitante"]
    ])

    return (
        partida["data"],
        clubes[0],
        clubes[1]
    )


def criar_placar_por_clube(partida):
    return {
        partida["mandante"]: partida["gols_mandante"],
        partida["visitante"]: partida["gols_visitante"]
    }


def comparar(ano, fonte_a, partidas_a, fonte_b, partidas_b):
    chaves_a = [criar_chave(p) for p in partidas_a]
    chaves_b = [criar_chave(p) for p in partidas_b]

    contagem_a = Counter(chaves_a)
    contagem_b = Counter(chaves_b)

    duplicadas_a = [
        chave for chave, quantidade in contagem_a.items()
        if quantidade > 1
    ]

    duplicadas_b = [
        chave for chave, quantidade in contagem_b.items()
        if quantidade > 1
    ]

    jogos_a = {
        criar_chave(p): p
        for p in partidas_a
    }

    jogos_b = {
        criar_chave(p): p
        for p in partidas_b
    }

    comuns = set(jogos_a) & set(jogos_b)
    somente_a = set(jogos_a) - set(jogos_b)
    somente_b = set(jogos_b) - set(jogos_a)

    placares_iguais = 0
    divergencias = []

    for chave in sorted(comuns):
        placar_a = criar_placar_por_clube(jogos_a[chave])
        placar_b = criar_placar_por_clube(jogos_b[chave])

        if placar_a == placar_b:
            placares_iguais += 1
        else:
            divergencias.append(
                (chave, placar_a, placar_b)
            )

    validado = (
        len(partidas_a) == len(partidas_b)
        and len(comuns) == len(partidas_a)
        and len(comuns) == len(partidas_b)
        and placares_iguais == len(comuns)
        and not duplicadas_a
        and not duplicadas_b
    )

    print("\n" + "=" * 55)
    print(f"FA CUP {ano}/{ano + 1}")
    print("=" * 55)

    print(f"Fonte A ({fonte_a}):", len(partidas_a))
    print(f"Fonte B ({fonte_b}):", len(partidas_b))
    print("Confrontos coincidentes:", len(comuns))
    print("Somente na fonte A:", len(somente_a))
    print("Somente na fonte B:", len(somente_b))
    print("Placares iguais:", placares_iguais)
    print("Divergencias de placar:", len(divergencias))
    print("Duplicadas na fonte A:", len(duplicadas_a))
    print("Duplicadas na fonte B:", len(duplicadas_b))

    if somente_a:
        print("\nSomente na fonte A:")
        for jogo in sorted(somente_a):
            print(jogo)

    if somente_b:
        print("\nSomente na fonte B:")
        for jogo in sorted(somente_b):
            print(jogo)

    if divergencias:
        print("\nDivergencias de placar:")
        for divergencia in divergencias:
            print(divergencia)

    if duplicadas_a:
        print("\nConfrontos duplicados na fonte A:")
        for jogo in duplicadas_a:
            print(jogo)

    if duplicadas_b:
        print("\nConfrontos duplicados na fonte B:")
        for jogo in duplicadas_b:
            print(jogo)

    if validado:
        print("\nAS DUAS FONTES COINCIDEM!")
    else:
        print("\nVALIDACAO PRECISA DE INVESTIGACAO.")

    return {
        "temporada": f"{ano}/{ano + 1}",
        "partidas_a": len(partidas_a),
        "partidas_b": len(partidas_b),
        "coincidentes": len(comuns),
        "divergencias": len(divergencias),
        "duplicadas": len(duplicadas_a) + len(duplicadas_b),
        "validado": validado
    }


def main():
    partidas_rda = ler_rda()
    resultados = []

    for ano in range(2015, 2025):
        if ano <= 2017:
            arquivo = f"{PASTA_RSSSF}/eng{ano + 1}.html"

            partidas_rsssf = ler_rsssf_html(
                arquivo, ano
            )

            partidas = [
                p for p in partidas_rda
                if p["temporada"] == ano
            ]

            resultado = comparar(
                ano,
                "RDA",
                partidas,
                "RSSSF",
                partidas_rsssf
            )

        elif ano == 2018:
            arquivo = (
                f"{PASTA_INGLATERRA}/2018-19/facup.txt"
            )

            partidas_openfootball = ler_openfootball(
                arquivo, ano
            )

            partidas = [
                p for p in partidas_rda
                if p["temporada"] == ano
            ]

            resultado = comparar(
                ano,
                "RDA",
                partidas,
                "OpenFootball",
                partidas_openfootball
            )

        elif ano == 2019:
            arquivo_rsssf = (
                f"{PASTA_RSSSF}/eng2020-facup.txt"
            )

            arquivo_openfootball = (
                f"{PASTA_INGLATERRA}/2019-20/facup.txt"
            )

            partidas_rsssf = ler_rsssf_txt(
                arquivo_rsssf, ano
            )

            partidas_openfootball = ler_openfootball(
                arquivo_openfootball, ano
            )

            resultado = comparar(
                ano,
                "RSSSF",
                partidas_rsssf,
                "OpenFootball",
                partidas_openfootball
            )

        else:
            arquivo_rsssf = (
                f"{PASTA_RSSSF}/eng{ano + 1}.html"
            )

            arquivo_openfootball = (
                f"{PASTA_INGLATERRA}/{ano}-{str(ano + 1)[-2:]}/facup.txt"
            )

            partidas_rsssf = ler_rsssf_html(
                arquivo_rsssf, ano
            )

            partidas_openfootball = ler_openfootball(
                arquivo_openfootball, ano
            )

            resultado = comparar(
                ano,
                "RSSSF",
                partidas_rsssf,
                "OpenFootball",
                partidas_openfootball
            )

        resultados.append(resultado)

    print("\n")
    print("=" * 75)
    print("RESUMO GERAL - VALIDACAO DA FA CUP")
    print("=" * 75)

    print(
        f"{'Temporada':<15}"
        f"{'Fonte A':>10}"
        f"{'Fonte B':>10}"
        f"{'Coincidentes':>15}"
        f"{'Status':>15}"
    )

    for resultado in resultados:
        status = "VALIDADA" if resultado["validado"] else "INVESTIGAR"

        print(
            f"{resultado['temporada']:<15}"
            f"{resultado['partidas_a']:>10}"
            f"{resultado['partidas_b']:>10}"
            f"{resultado['coincidentes']:>15}"
            f"{status:>15}"
        )

    total_validado = sum(
        1 for r in resultados if r["validado"]
    )

    print("\nTemporadas validadas:", total_validado)
    print("Total de temporadas:", len(resultados))


if __name__ == "__main__":
    main()


