# Documentação — Coleta e Tratamento dos Dados de Lesões

## 1. Objetivo

Preparar a base histórica de lesões de jogadores para o estudo da relação entre partidas disputadas pelos clubes e tempo de afastamento por lesões, considerando Premier League e Ligue 1, entre as temporadas 2015/16 e 2024/25.

## 2. Redução do espaço amostral

A base atualizada do Transfermarkt (`player_injuries_updated_20260929.csv`) possuía **168.290 registros**, abrangendo diversas temporadas e competições.

O tratamento foi realizado em etapas:

| Etapa | Registros |
|---|---:|
| Base original completa | 168.290 |
| Registros nas dez temporadas selecionadas | 122.646 |
| Registros associados a jogadores presentes nas duas ligas e temporadas de interesse | 10.386 |

Assim, o espaço amostral foi reduzido em aproximadamente **93,8%** em relação à base original, mantendo os registros pertinentes ao recorte do estudo.

## 3. Cruzamento e identificação dos clubes

Foram utilizadas bases complementares do repositório:

- `player_performances.txt`: identificação dos jogadores, temporadas, competições e clubes associados ao desempenho.
- `transfer_history.txt`: histórico de transferências.
- `player_profiles`: informações complementares dos jogadores.

Os cruzamentos utilizaram principalmente `player_id` e `season_name`.

Na etapa de associação inicial dos clubes, os resultados foram:

| Situação | Registros |
|---|---:|
| Clubes associados inicialmente | 10.125 |
| Registros pendentes de revisão | 261 |
| Total | 10.386 |

Os registros pendentes foram separados para evitar atribuições sem evidências suficientes.

## 4. Arquivos e scripts

**Bases geradas:**
- `data/interim/lesoes_filtradas.csv`: registros após os filtros aplicados.
- `data/interim/lesoes_com_clube.csv`: base com associação inicial de clubes.
- `data/interim/lesoes_pendentes.csv`: registros que necessitam de revisão.

**Scripts desenvolvidos:**
- `analisar_competicoes.py`
- `analisar_ligas.py`
- `analisar_tabelas.py`
- `analise_lesoes.py`
- `classificar_lesoes.py`
- `gerar_base_lesoes.py`
- `investigar_pendentes.py`
- `motivos_lesoes.py`
- `cruzar_jogadores.py`

## 5. Continuidade do trabalho

A associação inicial não garante, por si só, que o clube identificado era aquele em que o jogador estava na data de início da lesão.

Essa validação, considerando `from_date`, `end_date` e `transfer_date` com o histórico de desempenho e de transferências, foi feita na etapa de integração.

Dos 261 registros pendentes na associação inicial, 258 foram resolvidos na etapa de integração (ver `docs/integracao_lesoes.md`) e 3 permaneceram sem clube atribuído.
