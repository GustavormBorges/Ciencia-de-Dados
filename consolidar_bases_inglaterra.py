
import csv
from pathlib import Path
from collections import Counter, defaultdict

PASTA = Path("data/processed")

ARQUIVO_PL = PASTA / "partidas_por_clube.csv"
ARQUIVO_FA = PASTA / "partidas_facup.csv"
ARQUIVO_EFL = PASTA / "partidas_eflcup.csv"

ARQUIVO_FA_RESUMO = PASTA / "partidas_facup_por_clube.csv"
ARQUIVO_EFL_RESUMO = PASTA / "partidas_eflcup_por_clube.csv"

def ler_csv(caminho):
    with open(caminho, "r", encoding="utf-8-sig", newline="") as arquivo:
        return list(csv.DictReader(arquivo))


def salvar_csv(caminho, colunas, dados):
    with open(caminho, "w", encoding="utf-8-sig", newline="") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=colunas)
        escritor.writeheader()
        escritor.writerows(dados)


def padronizar_clube(nome, nomes_pl):
    nome = nome.strip()
    return nomes_pl.get(nome.casefold(), nome)


def carregar_partidas(caminho, competicao, nomes_pl):
    partidas = []

    for linha in ler_csv(caminho):
        if linha["contar_como_partida"].strip().lower() != "sim":
            continue

        mandante = padronizar_clube(linha["mandante"], nomes_pl)
        visitante = padronizar_clube(linha["visitante"], nomes_pl)

        partida = {
            "competicao": competicao,
            "temporada": linha["temporada"],
            "data": linha["data"],
            "mandante": mandante,
            "visitante": visitante,
            "gols_mandante": linha["gols_mandante"],
            "gols_visitante": linha["gols_visitante"],
            "fonte": linha["fonte"],
            "status_competicao": linha["status_competicao"]
        }

        partidas.append(partida)

    return partidas


def carregar_resumo(caminho, coluna_partidas, nomes_pl):
    resumo = {}

    for linha in ler_csv(caminho):
        temporada = linha["temporada"]
        clube = padronizar_clube(linha["clube"], nomes_pl)
        chave = (temporada, clube)

        resumo[chave] = int(linha[coluna_partidas])

    return resumo


def main():
    print("LENDO BASES...")

    dados_pl = ler_csv(ARQUIVO_PL)

    dados_pl = [
        linha for linha in dados_pl
        if linha["liga"] == "Premier League"
    ]

    nomes_pl = {
        linha["clube"].strip().casefold(): linha["clube"].strip()
        for linha in dados_pl
    }

    partidas_fa = carregar_partidas(
        ARQUIVO_FA, "FA Cup", nomes_pl
    )

    partidas_efl = carregar_partidas(
        ARQUIVO_EFL, "EFL Cup", nomes_pl
    )

    todas_partidas = partidas_fa + partidas_efl

    print("FA Cup:", len(partidas_fa), "partidas")
    print("EFL Cup:", len(partidas_efl), "partidas")

    # Contagem de participações nas copas
    contagem_fa = Counter()
    contagem_efl = Counter()

    for partida in partidas_fa:
        temporada = partida["temporada"]
        contagem_fa[(temporada, partida["mandante"])] += 1
        contagem_fa[(temporada, partida["visitante"])] += 1

    for partida in partidas_efl:
        temporada = partida["temporada"]
        contagem_efl[(temporada, partida["mandante"])] += 1
        contagem_efl[(temporada, partida["visitante"])] += 1

    # Resumos originais para comparação
    resumo_fa = carregar_resumo(
        ARQUIVO_FA_RESUMO, "partidas_facup", nomes_pl
    )

    resumo_efl = carregar_resumo(
        ARQUIVO_EFL_RESUMO, "partidas_eflcup", nomes_pl
    )

    divergencias = []

    for chave in sorted(set(contagem_fa) | set(resumo_fa)):
        calculado = contagem_fa[chave]
        original = resumo_fa.get(chave, 0)

        if calculado != original:
            divergencias.append({
                "competicao": "FA Cup",
                "temporada": chave[0],
                "clube": chave[1],
                "calculado": calculado,
                "resumo_original": original
            })

    for chave in sorted(set(contagem_efl) | set(resumo_efl)):
        calculado = contagem_efl[chave]
        original = resumo_efl.get(chave, 0)

        if calculado != original:
            divergencias.append({
                "competicao": "EFL Cup",
                "temporada": chave[0],
                "clube": chave[1],
                "calculado": calculado,
                "resumo_original": original
            })

    # Base de partidas individuais das copas
    colunas_partidas = [
        "competicao",
        "temporada",
        "data",
        "mandante",
        "visitante",
        "gols_mandante",
        "gols_visitante",
        "fonte",
        "status_competicao"
    ]

    salvar_csv(
        PASTA / "partidas_copas_inglaterra.csv",
        colunas_partidas,
        todas_partidas
    )

    # Contagem da Premier League
    contagem_pl = {}

    for linha in dados_pl:
        chave = (linha["temporada"], linha["clube"])
        contagem_pl[chave] = int(linha["partidas"])

    # Consolidação por clube e temporada
    todas_chaves = (
        set(contagem_pl)
        | set(contagem_fa)
        | set(contagem_efl)
    )

    base_clubes = []

    for temporada, clube in sorted(todas_chaves):
        pl = contagem_pl.get((temporada, clube), 0)
        fa = contagem_fa.get((temporada, clube), 0)
        efl = contagem_efl.get((temporada, clube), 0)

        base_clubes.append({
            "temporada": temporada,
            "clube": clube,
            "partidas_premier_league": pl,
            "partidas_facup": fa,
            "partidas_eflcup": efl,
            "total_partidas": pl + fa + efl
        })

    colunas_clubes = [
        "temporada",
        "clube",
        "partidas_premier_league",
        "partidas_facup",
        "partidas_eflcup",
        "total_partidas"
    ]

    salvar_csv(
        PASTA / "partidas_inglaterra_por_clube.csv",
        colunas_clubes,
        base_clubes
    )

    # Auditoria por temporada
    temporadas = sorted(set(
        linha["temporada"] for linha in dados_pl
    ))

    auditoria = []

    for temporada in temporadas:
        pl_participacoes = sum(
            valor for (ano, clube), valor in contagem_pl.items()
            if ano == temporada
        )

        fa_partidas = sum(
            1 for partida in partidas_fa
            if partida["temporada"] == temporada
        )

        efl_partidas = sum(
            1 for partida in partidas_efl
            if partida["temporada"] == temporada
        )

        pl_partidas = pl_participacoes // 2

        clubes_pl = sum(
            1 for ano, clube in contagem_pl
            if ano == temporada
        )

        auditoria.append({
            "temporada": temporada,
            "clubes_premier_league": clubes_pl,
            "partidas_premier_league": pl_partidas,
            "partidas_facup": fa_partidas,
            "partidas_eflcup": efl_partidas,
            "total_partidas": pl_partidas + fa_partidas + efl_partidas,
            "participacoes_premier_league_pares":
                "sim" if pl_participacoes % 2 == 0 else "nao"
        })

    salvar_csv(
        PASTA / "auditoria_inglaterra.csv",
        [
            "temporada",
            "clubes_premier_league",
            "partidas_premier_league",
            "partidas_facup",
            "partidas_eflcup",
            "total_partidas",
            "participacoes_premier_league_pares"
        ],
        auditoria
    )

    salvar_csv(
        PASTA / "divergencias_resumos_copas.csv",
        [
            "competicao",
            "temporada",
            "clube",
            "calculado",
            "resumo_original"
        ],
        divergencias
    )

    # Verificações finais
    chaves_duplicadas = Counter(
        (
            p["competicao"],
            p["temporada"],
            p["data"],
            p["mandante"],
            p["visitante"]
        )
        for p in todas_partidas
    )

    duplicadas = sum(
        1 for quantidade in chaves_duplicadas.values()
        if quantidade > 1
    )

    print("\n=== RESULTADO FINAL ===")
    print("Partidas individuais das copas:", len(todas_partidas))
    print("Registros de clube-temporada:", len(base_clubes))
    print("Premier League:", sum(contagem_pl.values()) // 2, "partidas")
    print("FA Cup:", len(partidas_fa), "partidas")
    print("EFL Cup:", len(partidas_efl), "partidas")
    print("Total de partidas nas tres competicoes:",
          sum(contagem_pl.values()) // 2
          + len(partidas_fa)
          + len(partidas_efl))
    print("Duplicatas nas copas:", duplicadas)
    print("Divergencias com resumos originais:", len(divergencias))

    if duplicadas == 0 and len(divergencias) == 0:
        print("\nVALIDACAO: APROVADA")
    else:
        print("\nVALIDACAO: VERIFICAR DIVERGENCIAS")

    print("\nArquivos gerados:")
    print("- partidas_copas_inglaterra.csv")
    print("- partidas_inglaterra_por_clube.csv")
    print("- auditoria_inglaterra.csv")
    print("- divergencias_resumos_copas.csv")


if __name__ == "__main__":
    main()
