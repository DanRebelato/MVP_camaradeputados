# Catálogo de Dados

## Camada Gold — `gold.camara`

### `dim_deputado`
Uma linha por deputado em exercício.

| Campo | Tipo | Descrição | Domínio |
|---|---|---|---|
| sk_deputado | int | Chave surrogate (= id da Câmara) | > 0 |
| nome | string | Nome parlamentar do deputado | texto livre |
| partido | string | Sigla do partido atual | ex.: PT, PL, MDB |
| uf | string | UF de representação | 27 UFs válidas |
| regiao | string | Região do Brasil (derivada da UF) | Norte, Nordeste, Centro-Oeste, Sudeste, Sul |
| email | string | E-mail institucional | texto livre, pode ser nulo |

**Linhagem:** `bronze.camara.deputados` → `silver.camara.deputados` (dedup por id, padronização de UF/partido) → `dim_deputado` (enriquecido com região via mapeamento estático UF→região).

### `dim_partido`
| Campo | Tipo | Descrição | Domínio |
|---|---|---|---|
| sk_partido | int | Chave surrogate (= id do partido na Câmara) | > 0 |
| sigla | string | Sigla do partido | ex.: PT, PL |
| nome | string | Nome completo do partido | texto livre |

**Linhagem:** `bronze.camara.partidos` → `silver.camara.partidos` → `dim_partido`.

### `dim_tempo`
| Campo | Tipo | Descrição | Domínio |
|---|---|---|---|
| sk_tempo | string | Chave `AAAA-MM` | ex.: 2025-03 |
| ano | int | Ano | 2025–2026 |
| mes | int | Mês | 1–12 |

**Linhagem:** derivada de `silver.camara.despesas` (combinações distintas de ano/mês).

### `fact_despesas`
Grão: uma linha por despesa individual de cota parlamentar (CEAP).

| Campo | Tipo | Descrição | Domínio |
|---|---|---|---|
| sk_deputado | int | FK para `dim_deputado` | > 0 |
| sk_tempo | string | FK para `dim_tempo` | AAAA-MM |
| tipoDespesa | string | Categoria da despesa | ex.: Combustíveis, Passagens Aéreas |
| valorDocumento | decimal(12,2) | Valor do documento fiscal | ≥ 0 |
| nomeFornecedor | string | Nome do fornecedor (padronizado) | texto livre |
| dataDocumento | string | Data do documento fiscal | formato ISO |

**Linhagem:** `bronze.camara.despesas` (coleta via `/deputados/{id}/despesas`) → `silver.camara.despesas` (tipagem, remoção de nulos/negativos, dedup) → `fact_despesas`.

### `fact_proposicoes`
Grão: uma linha por proposição legislativa apresentada.

| Campo | Tipo | Descrição | Domínio |
|---|---|---|---|
| sk_deputado | int | FK para `dim_deputado` (autor) | > 0 |
| id | long | ID da proposição na Câmara | > 0 |
| siglaTipo | string | Tipo da proposição | ex.: PL, PEC, REQ |
| numero | int | Número da proposição | > 0 |
| ano | int | Ano de apresentação | 2025–2026 |
| ementa | string | Resumo do conteúdo da proposição | texto livre |
| dataApresentacao | string | Data de apresentação | formato ISO |

**Linhagem:** `bronze.camara.proposicoes` (coleta via `/proposicoes?idDeputadoAutor=`) → `silver.camara.proposicoes` (dedup por id, tipagem) → `fact_proposicoes`.

## Camadas Bronze e Silver
Espelham as mesmas tabelas com menos limpeza — ver notebooks `00_bronze_ingestao.py` e
`01_silver_transformacao.py` para o detalhe campo a campo de cada transformação aplicada.
