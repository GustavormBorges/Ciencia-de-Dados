# Projeto de Introdução à Ciência de Dados

## Integrantes

- Gustavo Ramos de Melo Borges
- Samuel Chaves Morais de Lima
- Vitória Maria da Silva
- Yasmin Sousa Batista

## Tema do projeto

**Carga de jogos e lesões no futebol: existe uma relação?**

O projeto investiga se clubes que disputam mais partidas por temporada têm jogadores afastados por lesão por mais tempo. A análise cobre as temporadas de **2015/16 a 2024/25** da **Premier League** (Inglaterra) e da **Ligue 1** (França).

## Abordagem de coleta dos dados

- Datasets públicos

## Dados no Google Drive

Os dados coletados estão disponíveis na pasta do Google Drive do grupo (acesso somente leitura):

[Pasta do projeto no Google Drive](https://drive.google.com/drive/folders/1appc788RuEs2cBCcn6SrUFIHQNCBNhw2?usp=sharing)

## Estrutura do repositório

```
Ciencia-de-Dados/
├── data/
│   ├── raw/
│   │   ├── premier-league/        # CSVs originais, um por temporada (15-16.csv ... 24-25.csv)
│   │   └── ligue-1/               # CSVs originais, um por temporada
│   └── processed/
│       └── partidas_por_clube.csv # partidas por clube e temporada
├── contar_partidas.py             # gera a tabela de partidas por clube
├── README_TRATAMENTO_LESOES.md    # documentação dos dados de lesões
├── *.py, lesoes_*.txt             # scripts e bases de lesões
├── README.md
└── LICENSE
```

---

## Dados de partidas

### Descrição do conjunto de dados

Resultados de partidas da Premier League e da Ligue 1 entre as temporadas 2015/16 e 2024/25, obtidos no site [Football-Data.co.uk](https://football-data.co.uk/downloadm.php). Cada linha dos CSVs originais representa uma partida, com mandante, visitante, placar, estatísticas do jogo e cotações de apostas.

A partir deles foi construída uma tabela com **a quantidade de partidas que cada clube disputou em cada temporada**, que será cruzada com os dados de lesões. No total são 7.351 partidas (3.800 da Premier League e 3.551 da Ligue 1), resumidas em 396 linhas de clube por temporada.

### Processo de coleta

1. O site disponibiliza um arquivo `data.zip` por temporada, com um CSV para cada divisão de cada país. Foram baixados os zips das 10 temporadas.
2. De cada zip foram usados apenas dois arquivos: `E0.csv` (Premier League) e `F1.csv` (Ligue 1).
3. Os arquivos foram renomeados com a temporada (`15-16.csv`, `16-17.csv`, ...) e guardados em `data/raw/premier-league/` e `data/raw/ligue-1/`, sem nenhuma alteração no conteúdo.

### Tratamento

O script `contar_partidas.py`, escrito em Python com a biblioteca `pandas`:

1. lê as colunas `HomeTeam` e `AwayTeam` de cada CSV;
2. descarta linhas sem times;
3. conta as aparições de cada clube, como mandante ou como visitante;
4. grava o resultado em `data/processed/partidas_por_clube.csv`.

Para reproduzir, execute na raiz do repositório:

```bash
python contar_partidas.py
```

### Dicionário de dados (`data/processed/partidas_por_clube.csv`)

| Coluna | Descrição | Exemplo |
|---|---|---|
| `liga` | Campeonato | Premier League |
| `temporada` | Temporada, no formato ano inicial/ano final | 2015/2016 |
| `clube` | Nome do clube, como aparece na fonte (em inglês e abreviado) | Man United |
| `partidas` | Quantidade de partidas disputadas pelo clube na temporada, em casa e fora | 38 |

### Limitações e observações

- **Só jogos de liga.** Os dados não incluem copas nacionais nem competições europeias, que também contribuem para a carga de jogos dos clubes.
- **Ligue 1 2019/20 incompleta.** A temporada foi encerrada em março de 2020 por causa da pandemia de covid-19. Há apenas 279 partidas e cada clube aparece com 27 ou 28 jogos, em vez de 38.
- **Ligue 1 com menos clubes.** A liga passou de 20 para 18 clubes em 2023/24, por isso 2023/24 e 2024/25 têm 306 partidas e 34 jogos por clube.
- **Nomes de clubes.** Estão em inglês e abreviados (por exemplo, "Man United", "Paris SG"). É preciso padronizá-los antes de cruzar com a base de lesões.
- **Formato de datas.** Os CSVs originais misturam `dd/mm/aaaa` e `dd/mm/aa`. A tabela final não usa datas.
- **Colunas.** O número de colunas dos CSVs originais varia entre temporadas, mas `HomeTeam` e `AwayTeam` existem em todos.

---

## Tratamento e integração dos dados de lesões

### Tratamento dos dados

O tratamento dos dados de lesões foi realizado utilizando o arquivo `player_injuries_updated_20260929.csv`, com o auxílio dos arquivos `player_performances.txt` e `transfer_history.txt`.

O processamento foi realizado pelo script `gerar_base_lesoes.py`, seguindo as etapas:

1. Identificação dos jogadores com registros de desempenho nas competições estudadas.
2. Filtragem das competições pelos códigos `GB1` (Premier League da Inglaterra) e `FR1` (Ligue 1 da França).
3. Associação dos jogadores aos clubes de acordo com os registros de desempenho e histórico de transferências.
4. Divisão dos períodos de lesão quando havia transferência de clube durante o afastamento.
5. Separação dos períodos associados a clubes das ligas estudadas daqueles relacionados a clubes de outras competições.
6. Identificação e separação dos registros com datas incompletas.

### Tratamento das transferências

Quando um jogador mudou de clube durante um período de lesão, o período foi dividido de acordo com a data da transferência. Dessa forma, os dias de ausência puderam ser associados ao clube correspondente em cada intervalo.

Os períodos relacionados a clubes fora da Premier League e da Ligue 1 foram mantidos separadamente e não foram utilizados na base integrada.

### Tratamento das datas inválidas

Foram identificados três registros com datas incompletas:

- Um registro sem data de início.
- Dois registros sem data final.

Esses registros foram separados no arquivo `lesoes_datas_invalidas.txt` e não foram utilizados no cálculo dos dias de ausência, pois não havia informações suficientes para determinar seus períodos corretamente.

### Padronização dos clubes e temporadas

Os nomes dos clubes apresentavam diferenças entre as fontes de lesões e partidas. Para permitir a integração, foram criadas correspondências entre os nomes utilizados nas duas bases.

Também foi necessário padronizar as temporadas. Por exemplo, o formato `15/16`, utilizado nos registros de lesões, foi convertido para `2015/2016`, utilizado na base de partidas.

Após a padronização, as 396 combinações de liga, temporada e clube apresentaram correspondência entre as duas bases.

### Integração das bases

A integração foi realizada pelo script `integrar_bases.py`, utilizando os arquivos `lesoes_distribuidas.txt` e `data/processed/partidas_por_clube.csv`.

Os registros de lesões foram agrupados por liga, temporada e clube. Para cada combinação, foram calculados:

- **Quantidade de lesões:** número de registros distintos de lesões associados ao clube.
- **Dias de ausência:** soma dos dias de ausência dos jogadores associados ao clube.

Essas informações foram combinadas com a quantidade de partidas disputadas por cada clube na respectiva temporada.

O resultado foi salvo em `data/processed/base_integrada.csv`, contendo 396 linhas e as seguintes colunas:

| Coluna | Descrição |
|---|---|
| `liga` | Campeonato disputado |
| `temporada` | Temporada no formato ano inicial/ano final |
| `clube` | Nome padronizado do clube |
| `partidas` | Quantidade de partidas disputadas na temporada |
| `quantidade_lesoes` | Quantidade de registros distintos de lesões |
| `dias_ausencia` | Soma dos dias de ausência dos jogadores |

### Validação da integração

Após a integração, foi executado o script `validar_integracao.py` para verificar a consistência dos dados.

Os resultados obtidos foram:

| Verificação | Resultado |
|---|---:|
| Combinações de partidas | 396 |
| Combinações de lesões | 396 |
| Linhas na base integrada | 396 |
| Combinações sem correspondência | 0 |
| Combinações duplicadas | 0 |
| Dias na base de lesões utilizada na integração | 364.270 |
| Dias na base integrada | 364.270 |
| Diferença entre os totais | 0 |
| Linhas sem partidas válidas | 0 |
| Valores negativos | 0 |

A validação demonstrou que os dias de ausência foram preservados durante a integração e que não foram encontradas combinações duplicadas ou sem correspondência.

### Limitações do tratamento

- **Temporadas:** os registros de lesões foram associados à temporada informada na fonte original. Períodos que atravessam a mudança de temporada ainda não foram redistribuídos entre as duas temporadas.
- **Dias simultâneos:** os dias de ausência são somados individualmente por jogador. Portanto, quando dois jogadores ficam afastados simultaneamente por dez dias, são contabilizados vinte dias de ausência.
- **Datas incompletas:** os três registros com datas inválidas foram separados e não participaram do cálculo dos dias de ausência.
- **Partidas perdidas:** a quantidade de partidas perdidas informada na base original não foi distribuída entre clubes quando uma lesão atravessava uma transferência, pois não havia informação suficiente para atribuir essas partidas com precisão.

### Arquivos principais do tratamento

| Arquivo | Finalidade |
|---|---|
| `gerar_base_lesoes.py` | Processamento e distribuição dos períodos de lesão |
| `lesoes_distribuidas.txt` | Períodos associados a clubes das ligas estudadas |
| `lesoes_fora_das_ligas.txt` | Períodos associados a clubes fora das ligas estudadas |
| `lesoes_datas_invalidas.txt` | Registros com datas incompletas |
| `comparar_clubes.py` | Comparação das combinações entre as bases |
| `integrar_bases.py` | Integração dos dados de partidas e lesões |
| `validar_integracao.py` | Verificação da consistência da base integrada |
| `data/processed/base_integrada.csv` | Base final integrada |
## Como reproduzir o tratamento e a integração

### Requisitos

É necessário ter o Python instalado e utilizar o terminal na pasta principal do repositório.

Instale as dependências com:

```bash
pip install -r requirements.txt
```

### Arquivos de origem

Antes de executar os scripts, baixe os seguintes arquivos na pasta do Google Drive do projeto:

- `player_injuries_updated_20260929.csv`
- `player_performances.txt`
- `transfer_history.txt`

Coloque os três arquivos diretamente na pasta principal `Ciencia-de-Dados/`, junto aos scripts Python.

### Ordem de execução

Execute os comandos abaixo, na raiz do repositório:

**1. Gerar a quantidade de partidas por clube:**

```bash
python contar_partidas.py
```

**2. Processar os dados de lesões e distribuir os períodos entre os clubes:**

```bash
python gerar_base_lesoes.py
```

Esse processamento gera:
- `lesoes_distribuidas.txt`
- `lesoes_fora_das_ligas.txt`
- `lesoes_datas_invalidas.txt`

**3. Validar a base de lesões:**

```bash
python validar_base_lesoes.py
```

**4. Comparar os clubes presentes nas bases:**

```bash
python comparar_clubes.py
```

**5. Integrar os dados de partidas e lesões:**

```bash
python integrar_bases.py
```

O resultado será salvo em:

`data/processed/base_integrada.csv`

**6. Validar a integração:**

```bash
python validar_integracao.py
```

### Resultado esperado

Ao final, será gerada uma base integrada com 396 combinações de clube e temporada, contendo a quantidade de partidas, a quantidade de lesões e os dias de ausência.