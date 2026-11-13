# Competições europeias e copas francesas

Os jogos de liga e das copas inglesas não bastam para medir a carga de jogos: os clubes também disputam as copas da França e as competições da UEFA. Esta parte completa a base com essas competições, de 2015/16 a 2024/25.

## Escopo

| Entra | Fica de fora |
|---|---|
| Champions League, Europa League e Conference League, **incluindo as fases qualificatórias** | Supercopa da UEFA |
| Coupe de France | Community Shield (Inglaterra) |
| Coupe de la Ligue (extinta após 2019/20) | Mundial de Clubes |
| Trophée des Champions | |

Uma partida é contada para um clube se ele entrou em campo. Prorrogação e pênaltis contam como uma única partida. Partidas abandonadas contam (os jogadores atuaram); partidas decididas por W.O. sem bola rolando não contam. A temporada de cada partida segue o ano da edição da competição (as qualificatórias de julho de 2018 pertencem a 2018/19).

## Fontes e processo

| Competição | Fonte principal | Conferência |
|---|---|---|
| Champions, Europa League e Conference (jogo a jogo, com qualificatórias) | [RSSSF](https://rsssf.org/ec/), uma página por temporada | Total de partidas da fase principal de cada edição comparado com o formato oficial; contagem de jogos dos clubes ingleses e franceses comparada com o OpenFootball (Champions 2015/16 a 2023/24, Europa League 2020/21 a 2023/24 e Conference) |
| Coupe de France | RSSSF (todas as fases de 2015/16 a 2019/20; só dos 16-avos em diante a partir de 2020/21) e Wikipedia (32-avos em diante) | Resultados das duas fontes comparados clube a clube e fase a fase |
| Coupe de la Ligue | RSSSF | Todo clube da Ligue 1 aparece em ao menos um jogo por temporada |
| Trophée des Champions | Wikipedia | Uma única partida por edição |

As páginas foram baixadas por `baixar_fontes_europa_franca.py` e `baixar_fontes_wikipedia.py` para a pasta `fontes-europa-franca/`, fora do repositório (como as fontes das copas inglesas). Cada fonte tem seu leitor: `leitor_rsssf_europa.py` e `leitor_copas_franca.py`. `nomes_clubes.py` padroniza os nomes para os da base de partidas e só reconhece um clube se ele estava na Premier League ou na Ligue 1 naquela temporada. Adversários estrangeiros e clubes amadores ficam de fora da contagem.

## Gerar os arquivos

```bash
python scripts/03_europa_franca/gerar_base_europa.py          # competições europeias
python scripts/03_europa_franca/gerar_base_franca.py          # copas francesas
python scripts/05_integracao/consolidar_base_completa.py   # junta liga + copas + Europa
```

## Arquivos gerados (`data/processed/`)

| Arquivo | Conteúdo |
|---|---|
| `partidas_europa.csv` | uma linha por partida europeia de clube das ligas (inclui `etapa`: fase principal ou qualificatória) |
| `partidas_europa_por_clube.csv` | partidas por clube e temporada em cada competição europeia |
| `auditoria_europa.csv` | partidas lidas por edição e conferência com o formato oficial |
| `partidas_copas_franca.csv` | uma linha por partida das copas francesas de clube da Ligue 1 |
| `partidas_copas_franca_por_clube.csv` | partidas por clube e temporada em cada copa |
| `auditoria_copas_franca.csv` | cobertura por temporada (clubes da Ligue 1 com jogo / clubes na liga) |
| `divergencias_franca.csv` | diferenças entre RSSSF e Wikipedia e a fonte escolhida |
| `partidas_todas_competicoes.csv` | **base final**: liga + copas nacionais + Europa, por clube e temporada (396 linhas) |
| `base_integrada_completa.csv` | a base final com `quantidade_lesoes` e `dias_ausencia` |

`data/excecoes/excecoes_europa.csv` registra as correções feitas à fonte, no mesmo formato de `data/excecoes/excecoes_facup.csv`.

## Principais colunas de `partidas_todas_competicoes.csv`

| Coluna | Descrição |
|---|---|
| `partidas_liga` | Premier League ou Ligue 1 |
| `partidas_facup`, `partidas_eflcup` | copas inglesas |
| `partidas_coupe_de_france`, `partidas_coupe_de_la_ligue`, `partidas_trophee_des_champions` | copas francesas |
| `partidas_copas_nacionais` | soma das copas do país |
| `partidas_champions`, `partidas_europa_league`, `partidas_conference_league` | competições da UEFA |
| `partidas_europa` | soma das três (inclui qualificatórias) |
| `partidas_europa_qualificatorias` | parte de `partidas_europa` disputada em qualificatórias |
| `total_partidas` | liga + copas nacionais + Europa |

## Problemas encontrados e decisões

- **Coupe de France sem a estreia da Ligue 1.** De 2020/21 a 2024/25 a RSSSF começa nos 16-avos; os 32-avos (onde a Ligue 1 entra) vêm da Wikipedia. Em 2015/16 a 2019/20 as duas fontes cobrem os 32-avos e foram comparadas.
- **Erro da RSSSF na Champions 2023/24.** A fonte lista "Milan AC x Crvena zvezda" no Grupo G; o jogo real foi Manchester City 3–1 Crvena zvezda (confirmado no OpenFootball). A correção está em `data/excecoes/excecoes_europa.csv`; sem ela o total do Manchester City ficaria errado.
- **Diferença de placar entre fontes.** Paris SG x Linas-Montlhéry (Coupe de France 2019/20): Wikipedia sem placar, RSSSF 6–0. Foi usado o da RSSSF.
- **Agregado digitado errado na RSSSF.** Ventspils x Bordeaux (Europa League 2018/19) vem com agregado 2–3; os placares das duas partidas (0–1 e 1–2) estão certos e conferem com a Wikipedia. As partidas foram mantidas.
- **Partida abandonada.** Paris FC x Lyon (Coupe de France 2021/22) foi interrompida por confusão e os dois clubes foram eliminados; a partida conta e fica sem placar.

## Limitações

- Europa League 2015/16 a 2019/20 e as fases qualificatórias de todas as edições têm uma única fonte (RSSSF). Para elas a conferência é o total de partidas por fase e a soma dos placares dos confrontos de ida e volta.
- A Coupe de la Ligue tem uma única fonte (RSSSF).
- A Supercopa da UEFA, a Community Shield e o Mundial de Clubes não foram incluídos.
- O OpenFootball de 2024/25 está incompleto para clubes franceses e não foi usado como referência para essa edição.
