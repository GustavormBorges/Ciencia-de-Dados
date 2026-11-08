# Carga de jogos e lesões no futebol: existe uma relação?

Projeto de **Introdução à Ciência de Dados** (UFPB, prof. Yuri Malheiros).

## Integrantes

- Gustavo Ramos de Melo Borges
- Samuel Chaves Morais de Lima
- Vitória Maria da Silva
- Yasmin Sousa Batista

## Tema

O projeto investiga se clubes que disputam mais partidas por temporada têm jogadores afastados por lesão por mais tempo. A análise cobre as temporadas de **2015/16 a 2024/25** da **Premier League** (Inglaterra) e da **Ligue 1** (França).

## Abordagem de coleta dos dados

- Datasets públicos (Football-Data.co.uk e Transfermarkt)
- Web scraping: download e leitura de páginas da RSSSF e da Wikipedia (competições europeias e copas francesas)

## Dados no Google Drive

[Pasta do projeto no Google Drive](https://drive.google.com/drive/folders/1appc788RuEs2cBCcn6SrUFIHQNCBNhw2?usp=sharing) (acesso somente leitura).

## Resultado: base final

Cada linha é um clube em uma temporada (**396 linhas**: 200 da Premier League e 196 da Ligue 1). Para cada uma há o total de partidas disputadas e as lesões.

| Arquivo (`data/processed/`) | Conteúdo |
|---|---|
| `partidas_todas_competicoes.csv` | partidas por clube e temporada: liga + copas nacionais + competições europeias |
| `base_integrada_completa.csv` | a tabela acima com `quantidade_lesoes` e `dias_ausencia` |

| Liga | Partidas de liga | Copas nacionais | Competições europeias |
|---|---:|---:|---:|
| Premier League | 7.600 | 1.177 | 763 |
| Ligue 1 | 7.102 | 762 | 557 |

O total por clube e temporada vai de 30 jogos (Metz, 2019/20, temporada encurtada pela covid) a 63 (por exemplo, Monaco em 2016/17 e Liverpool em 2015/16). O dicionário das colunas está em [docs/europa_e_copas_francesas.md](docs/europa_e_copas_francesas.md).

## Documentação

| Documento | Assunto |
|---|---|
| [docs/partidas_liga.md](docs/partidas_liga.md) | partidas da Premier League e da Ligue 1 (Football-Data.co.uk) |
| [docs/copas_inglaterra.md](docs/copas_inglaterra.md) | FA Cup e EFL Cup |
| [docs/europa_e_copas_francesas.md](docs/europa_e_copas_francesas.md) | Champions, Europa League, Conference, Coupe de France, Coupe de la Ligue e Trophée des Champions |
| [docs/lesoes.md](docs/lesoes.md) | coleta e tratamento da base de lesões (Transfermarkt) |
| [docs/integracao_lesoes.md](docs/integracao_lesoes.md) | integração de partidas e lesões, validação e como reproduzir |

## Como reproduzir

Instale as dependências na raiz do repositório (`pip install -r requirements.txt`) e rode os scripts nesta ordem:

| Etapa | Scripts |
|---|---|
| 1. Partidas de liga | `contar_partidas.py` |
| 2. Copas inglesas | `gerar_base_facup.py`, `gerar_base_eflcup.py`, `consolidar_bases_inglaterra.py` |
| 3. Europa e copas francesas | `baixar_fontes_europa_franca.py`, `baixar_fontes_wikipedia.py`, `gerar_base_europa.py`, `gerar_base_franca.py` |
| 4. Lesões | `gerar_base_lesoes.py`, `validar_base_lesoes.py`, `comparar_clubes.py`, `integrar_bases.py`, `validar_integracao.py` |
| 5. Base final | `consolidar_base_completa.py` |

As fontes brutas das etapas 2 e 3 ficam em pastas `fontes-*` ao lado do repositório (fora dele), e os arquivos de lesões de origem devem ser baixados do Drive. Os detalhes estão em cada documento de `docs/`.

## Estrutura do repositório

```
Ciencia-de-Dados/
├── data/
│   ├── raw/                  CSVs originais da Football-Data.co.uk
│   └── processed/            bases geradas pelos scripts
├── docs/                     documentação de cada etapa
├── *.py                      scripts de coleta, tratamento e validação
├── excecoes_*.csv            correções feitas às fontes (FA Cup e Europa)
├── lesoes_*.txt              bases intermediárias de lesões
├── requirements.txt
├── README.md
└── LICENSE
```
