# Partidas das competições nacionais inglesas

## Objetivo

Além dos jogos da Premier League, foram coletados os resultados das duas principais copas nacionais inglesas: **FA Cup** e **EFL Cup**.

Essa ampliação permite considerar uma parcela maior da carga de jogos dos clubes, já que as equipes podem disputar partidas em diferentes competições durante a mesma temporada.

A coleta abrange as temporadas de **2015/16 a 2024/25**.

## Fontes dos dados

Foram utilizadas diferentes fontes públicas para obter e conferir os resultados:

- **FA Cup:** dados do repositório engsoccerdata, do OpenFootball e do RSSSF.
- **EFL Cup:** dados do repositório engsoccerdata, do OpenFootball e do RSSSF.

As fontes foram comparadas para identificar diferenças nos confrontos e placares. Quando foram encontradas divergências, elas foram investigadas e documentadas no arquivo `excecoes_facup.csv`, no caso da FA Cup.

## Bases geradas

| Arquivo | Descrição |
|---|---|
| `partidas_facup.csv` | Partidas individuais da FA Cup |
| `partidas_eflcup.csv` | Partidas individuais da EFL Cup |
| `partidas_facup_por_clube.csv` | Participações dos clubes na FA Cup por temporada |
| `partidas_eflcup_por_clube.csv` | Participações dos clubes na EFL Cup por temporada |
| `partidas_copas_inglaterra.csv` | Partidas individuais das duas copas |
| `partidas_inglaterra_por_clube.csv` | Total de partidas por clube e temporada nas três competições |
| `partidas_premier_league_com_copas.csv` | Base consolidada dos clubes da Premier League, incluindo as copas |

## Consolidação

A consolidação reuniu os jogos de três competições:

- Premier League: 3.800 partidas;
- FA Cup: 1.436 partidas;
- EFL Cup: 925 partidas.

Ao todo, foram contabilizadas **6.161 partidas** nas três competições, considerando as dez temporadas analisadas.

A base `partidas_premier_league_com_copas.csv` contém 200 registros, correspondentes aos 20 clubes da Premier League em cada uma das dez temporadas.

Suas colunas são:

| Coluna | Descrição |
|---|---|
| `temporada` | Temporada no formato ano inicial/ano final |
| `clube` | Nome padronizado do clube |
| `partidas_premier_league` | Partidas disputadas na Premier League |
| `partidas_facup` | Participações na FA Cup |
| `partidas_eflcup` | Participações na EFL Cup |
| `total_partidas` | Soma das partidas nas três competições |

## Auditoria e validação

Foram gerados arquivos de auditoria para registrar a quantidade de partidas por temporada e verificar a consistência dos dados.

As validações realizadas confirmaram:

- Ausência de partidas duplicadas nas bases consolidadas das copas;
- Correspondência entre os totais por clube e os resumos das fontes;
- Correspondência de todos os clubes da Premier League nas bases das copas;
- Tratamento documentado das divergências encontradas entre as fontes.

Uma partida disputada e posteriormente anulada pela entidade organizadora foi mantida na contagem de carga de jogos, pois os clubes efetivamente entraram em campo.

## Limitações

- Esta consolidação contempla apenas a Premier League, a FA Cup e a EFL Cup. As competições europeias e as copas francesas estão em [europa_e_copas_francesas.md](europa_e_copas_francesas.md), e a base com tudo junto é `partidas_todas_competicoes.csv`.
- A Community Shield não foi incluída.
- A quantidade de partidas por clube e temporada representa uma medida coletiva da carga de jogos, não a exposição individual de cada jogador.

O processamento foi realizado pelos scripts `gerar_base_facup.py`, `gerar_base_eflcup.py` e `consolidar_bases_inglaterra.py`.
