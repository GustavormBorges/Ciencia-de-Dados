# Carga de jogos e lesões no futebol: existe uma relação?

Projeto de **Introdução à Ciência de Dados** (UFPB, prof. Yuri Malheiros).

## Integrantes

- Gustavo Ramos de Melo Borges
- Samuel Chaves Morais de Lima
- Vitória Maria da Silva
- Yasmin Sousa Batista

## Tema do projeto

O projeto investiga se clubes que disputam mais partidas por temporada têm jogadores afastados por lesão por mais tempo. A análise cobre as temporadas de **2015/16 a 2024/25** da **Premier League** (Inglaterra) e da **Ligue 1** (França).

## Abordagem de coleta dos dados

- Datasets públicos (Football-Data.co.uk e Transfermarkt).
- Web scraping: download e leitura de páginas da RSSSF e da Wikipedia (competições europeias e copas francesas).

## Dados no Google Drive

[Pasta do projeto no Google Drive](https://drive.google.com/drive/folders/1appc788RuEs2cBCcn6SrUFIHQNCBNhw2?usp=sharing) (acesso somente leitura). Cada integrante guarda os dados da sua parte em uma subpasta.

---

## Descrição do conjunto de dados

O conjunto de dados reúne, para cada clube da Premier League e da Ligue 1 em cada temporada de 2015/16 a 2024/25, **a quantidade de partidas disputadas** e **as lesões dos jogadores**. São 396 combinações de clube e temporada (200 da Premier League e 196 da Ligue 1). A Ligue 1 teve 20 clubes até 2022/23 e 18 a partir de 2023/24.

As partidas somam três grupos de competições: a liga (Premier League ou Ligue 1), as copas nacionais (FA Cup e EFL Cup na Inglaterra; Coupe de France, Coupe de la Ligue e Trophée des Champions na França) e as competições da UEFA (Champions League, Europa League e Conference League, incluindo qualificatórias). No total são 17.961 participações de clubes em partidas. Não entram a Supercopa da UEFA, a Community Shield e o Mundial de Clubes.

As lesões vêm do Transfermarkt. Cada lesão tem data de início e fim e, quando o jogador trocou de clube durante o afastamento, o período foi dividido entre os clubes. A base final tem 9.386 registros de lesão e 364.270 dias de ausência somados nas dez temporadas.

## Processo de coleta

1. **Partidas de liga.** Foram baixados manualmente, em [Football-Data.co.uk](https://football-data.co.uk/downloadm.php), os arquivos das 10 temporadas e usados apenas `E0.csv` (Premier League) e `F1.csv` (Ligue 1). O script `contar_partidas.py` conta as partidas de cada clube.
2. **Copas inglesas.** FA Cup e EFL Cup foram obtidas do repositório engsoccerdata, do OpenFootball e da RSSSF. As fontes foram comparadas e as divergências documentadas em `excecoes_facup.csv`.
3. **Competições europeias e copas francesas.** Scripts (`baixar_fontes_europa_franca.py` e `baixar_fontes_wikipedia.py`) baixam as páginas da RSSSF e da Wikipedia, e leitores (`leitor_rsssf_europa.py` e `leitor_copas_franca.py`) extraem os jogos. A conferência usou o total de jogos de cada fase, a soma dos placares e a comparação com o OpenFootball. Um erro da RSSSF foi corrigido em `excecoes_europa.csv`.
4. **Lesões.** Os arquivos `player_injuries_updated_20260929.csv`, `player_performances.txt` e `transfer_history.txt` vêm do dataset público [salimt/football-datasets](https://github.com/salimt/football-datasets), que reúne dados do Transfermarkt. O repositório foi baixado manualmente, como ZIP pelo GitHub, em 06/11/2026; não foi usada API nem script de coleta. Os arquivos estão nas pastas `datalake/transfermarkt/player_injuries/`, `datalake/transfermarkt/player_performances/` e `datalake/transfermarkt/transfer_history/`. No ZIP, `player_performances.txt` e `transfer_history.txt` vieram como ponteiros do Git LFS (arquivos de poucas linhas, sem os dados), então foram baixados individualmente pela opção Raw do GitHub. Os três arquivos ficam na pasta `Dados originais - Transfermarkt` do Drive. O script `gerar_base_lesoes.py` filtra as ligas e temporadas do projeto e associa cada período de lesão ao clube do jogador.
5. **Base final.** `consolidar_base_completa.py` junta liga, copas e Europa por clube e temporada, e `integrar_bases.py` acrescenta as lesões.

## Dicionário de dados

### Base final: `data/processed/base_integrada_completa.csv`

Uma linha por clube e temporada (396 linhas). Exemplo: Manchester City em 2018/19.

| Coluna | Descrição | Exemplo |
|---|---|---|
| `liga` | Campeonato do clube na temporada | Premier League |
| `temporada` | Temporada, no formato ano inicial/ano final | 2018/2019 |
| `clube` | Nome do clube, padronizado como no Football-Data | Man City |
| `partidas_liga` | Partidas na Premier League ou na Ligue 1 | 38 |
| `partidas_facup` | Partidas na FA Cup | 6 |
| `partidas_eflcup` | Partidas na EFL Cup | 6 |
| `partidas_coupe_de_france` | Partidas na Coupe de France | 0 |
| `partidas_coupe_de_la_ligue` | Partidas na Coupe de la Ligue (extinta após 2019/20) | 0 |
| `partidas_trophee_des_champions` | Partidas no Trophée des Champions | 0 |
| `partidas_copas_nacionais` | Soma das copas nacionais | 12 |
| `partidas_champions` | Partidas na Champions League, com qualificatórias | 10 |
| `partidas_europa_league` | Partidas na Europa League, com qualificatórias | 0 |
| `partidas_conference_league` | Partidas na Conference League, com qualificatórias | 0 |
| `partidas_europa` | Soma das três competições da UEFA | 10 |
| `partidas_europa_qualificatorias` | Parte de `partidas_europa` disputada em qualificatórias | 0 |
| `total_partidas` | Liga + copas nacionais + competições europeias | 60 |
| `quantidade_lesoes` | Quantidade de lesões de jogadores do clube na temporada | 59 |
| `dias_ausencia` | Soma dos dias de afastamento dessas lesões | 1600 |

O arquivo `partidas_todas_competicoes.csv` tem as mesmas colunas, menos as duas de lesões.

### Lesões por clube: `lesoes_distribuidas.txt`

Uma linha por período de lesão associado a um clube das duas ligas. Exemplo: uma lesão cirúrgica de um jogador do AS Monaco em 2019/20.

| Coluna | Descrição | Exemplo |
|---|---|---|
| `from_date` | Data de início da lesão | 2019-10-18 |
| `end_date` | Data de fim da lesão | 2019-12-12 |
| `id_lesao` | Identificador da lesão; se ela foi dividida entre dois clubes, o número se repete | 1573 |
| `player_id` | Identificador do jogador no Transfermarkt | 1667 |
| `season_name` | Temporada da lesão, no formato do Transfermarkt | 19/20 |
| `injury_reason` | Motivo da lesão, como informado pela fonte (em inglês) | surgery |
| `from_date_clube` | Início do período da lesão atribuído ao clube | 2019-10-18 |
| `end_date_clube` | Fim do período da lesão atribuído ao clube | 2019-12-12 |
| `days_missed_original` | Dias de afastamento da lesão inteira, como na fonte | 56.0 |
| `days_missed_clube` | Dias de afastamento dentro do período do clube | 56 |
| `games_missed_total_lesao` | Jogos perdidos na lesão inteira, como na fonte (não é dividido entre clubes) | 8 |
| `clube_id` | Identificador do clube no Transfermarkt | 162 |
| `clube_identificado` | Nome do clube | AS Monaco |
| `liga_identificada` | Liga do clube | Ligue 1 |
| `status_clube` | Situação da associação do período a um clube das ligas | Identificado |

O dicionário de `partidas_por_clube.csv` e das demais bases está em [docs/](docs/).

## Documentação detalhada

| Documento | Assunto |
|---|---|
| [docs/partidas_liga.md](docs/partidas_liga.md) | partidas da Premier League e da Ligue 1 |
| [docs/copas_inglaterra.md](docs/copas_inglaterra.md) | FA Cup e EFL Cup |
| [docs/europa_e_copas_francesas.md](docs/europa_e_copas_francesas.md) | competições da UEFA e copas francesas |
| [docs/lesoes.md](docs/lesoes.md) | coleta e tratamento das lesões |
| [docs/integracao_lesoes.md](docs/integracao_lesoes.md) | integração, validação e como reproduzir |

## Limitações

- A quantidade de partidas é uma medida do clube, e não a exposição de cada jogador.
- A Ligue 1 2019/20 foi encerrada em março de 2020 pela covid-19: cada clube tem 27 ou 28 jogos de liga.
- Europa League 2015/16 a 2019/20, qualificatórias e Coupe de la Ligue vêm de uma única fonte (RSSSF).
- Supercopa da UEFA, Community Shield e Mundial de Clubes não foram incluídos.
- As lesões dependem do registro do Transfermarkt. A associação inicial de clubes deixou 261 registros para revisão; eles foram reavaliados na etapa de integração, com o histórico de desempenho e de transferências: 258 foram resolvidos e 3 não foram atribuídos a nenhum clube.

## Primeiras observações (preliminares)

Estas observações são iniciais e não permitem uma conclusão: a base tem 396 linhas, cobre apenas duas ligas e mede a carga por clube, não por jogador.

- Clubes com muitos jogos nem sempre ficam mais tempo com jogadores afastados: o Man City em 2022/23 disputou 60 partidas e somou 452 dias de ausência, enquanto o Brentford em 2023/24 disputou 42 e somou 2.856 dias.
- A média de dias por lesão varia muito (cerca de 119 no Brentford em 2023/24 e 22 no Man City em 2022/23). Isso sugere que poucas lesões longas podem pesar mais nos dias de ausência do que o número de jogos, o que é uma hipótese a testar.
- A contagem de lesões aumenta de forma acentuada de 2017/18 para 2018/19 em vários clubes, sem aumento de jogos (Arsenal de 35 para 59, Chelsea de 25 para 53, Liverpool de 30 para 60). É preciso verificar se houve mudança no registro do Transfermarkt.

## Próximos passos

- Análise no nível do jogador (a avaliar: depende de minutos jogados e das datas das lesões).
- Carga recente: partidas nas semanas anteriores a cada lesão.
- Comparar dentro da mesma liga e temporada, usando taxas (lesões por 10 jogos e dias por lesão).
- Controlar elenco, posição e gravidade da lesão.

## Como reproduzir

Instale as dependências com `pip install -r requirements.txt` e rode, na raiz do repositório e nesta ordem:

| Etapa | Scripts |
|---|---|
| 1. Partidas de liga | `contar_partidas.py` |
| 2. Copas inglesas | `gerar_base_facup.py`, `gerar_base_eflcup.py`, `consolidar_bases_inglaterra.py` |
| 3. Europa e copas francesas | `baixar_fontes_europa_franca.py`, `baixar_fontes_wikipedia.py`, `gerar_base_europa.py`, `gerar_base_franca.py` |
| 4. Lesões | `gerar_base_lesoes.py`, `validar_base_lesoes.py`, `comparar_clubes.py`, `integrar_bases.py`, `validar_integracao.py` |
| 5. Base final | `consolidar_base_completa.py` |

As fontes brutas das etapas 2 e 3 ficam em pastas `fontes-*` ao lado do repositório, e os três arquivos de lesões de origem devem ser baixados do Drive para a raiz do repositório.

## Estrutura do repositório

```
Ciencia-de-Dados/
├── data/
│   ├── raw/                  CSVs originais da Football-Data.co.uk
│   └── processed/            bases geradas pelos scripts
├── docs/                     documentação de cada etapa
├── *.py                      scripts de coleta, tratamento e validação
├── excecoes_*.csv            correções feitas às fontes
├── lesoes_*.txt              bases intermediárias de lesões
├── requirements.txt
├── README.md
└── LICENSE
```
