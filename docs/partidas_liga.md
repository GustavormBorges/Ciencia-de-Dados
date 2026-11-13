# Partidas de liga (Premier League e Ligue 1)

## Descrição do conjunto de dados

Resultados de partidas da Premier League e da Ligue 1 entre as temporadas 2015/16 e 2024/25, obtidos no site [Football-Data.co.uk](https://football-data.co.uk/downloadm.php). Cada linha dos CSVs originais representa uma partida, com mandante, visitante, placar, estatísticas do jogo e cotações de apostas.

A partir deles foi construída uma tabela com **a quantidade de partidas que cada clube disputou em cada temporada**, que será cruzada com os dados de lesões. No total são 7.351 partidas (3.800 da Premier League e 3.551 da Ligue 1), resumidas em 396 linhas de clube por temporada.

## Processo de coleta

1. O site disponibiliza um arquivo `data.zip` por temporada, com um CSV para cada divisão de cada país. Foram baixados os zips das 10 temporadas.
2. De cada zip foram usados apenas dois arquivos: `E0.csv` (Premier League) e `F1.csv` (Ligue 1).
3. Os arquivos foram renomeados com a temporada (`15-16.csv`, `16-17.csv`, ...) e guardados em `data/raw/premier-league/` e `data/raw/ligue-1/`, sem nenhuma alteração no conteúdo.

## Tratamento

O script `contar_partidas.py`, escrito em Python com a biblioteca `pandas`:

1. lê as colunas `HomeTeam` e `AwayTeam` de cada CSV;
2. descarta linhas sem times;
3. conta as aparições de cada clube, como mandante ou como visitante;
4. grava o resultado em `data/processed/partidas_por_clube.csv`.

Para reproduzir, execute na raiz do repositório:

```bash
python scripts/01_partidas_liga/contar_partidas.py
```

## Dicionário de dados (`data/processed/partidas_por_clube.csv`)

| Coluna | Descrição | Exemplo |
|---|---|---|
| `liga` | Campeonato | Premier League |
| `temporada` | Temporada, no formato ano inicial/ano final | 2015/2016 |
| `clube` | Nome do clube, como aparece na fonte (em inglês e abreviado) | Man United |
| `partidas` | Quantidade de partidas disputadas pelo clube na temporada, em casa e fora | 38 |

## Limitações e observações

- **Só jogos de liga.** Esta tabela (`partidas_por_clube.csv`) conta apenas a liga. As copas nacionais e as competições europeias estão em [copas_inglaterra.md](copas_inglaterra.md) e [europa_e_copas_francesas.md](europa_e_copas_francesas.md), e a soma de tudo está em `partidas_todas_competicoes.csv`.
- **Ligue 1 2019/20 incompleta.** A temporada foi encerrada em março de 2020 por causa da pandemia de covid-19. Há apenas 279 partidas e cada clube aparece com 27 ou 28 jogos, em vez de 38.
- **Ligue 1 com menos clubes.** A liga passou de 20 para 18 clubes em 2023/24, por isso 2023/24 e 2024/25 têm 306 partidas e 34 jogos por clube.
- **Nomes de clubes.** Estão em inglês e abreviados (por exemplo, "Man United", "Paris SG"). É preciso padronizá-los antes de cruzar com a base de lesões.
- **Formato de datas.** Os CSVs originais misturam `dd/mm/aaaa` e `dd/mm/aa`. A tabela final não usa datas.
- **Colunas.** O número de colunas dos CSVs originais varia entre temporadas, mas `HomeTeam` e `AwayTeam` existem em todos.
