# MVP de Engenharia de Dados — Comportamento Legislativo dos Deputados Federais

> Preencha os campos marcados com `[PREENCHER]` depois de rodar os notebooks no Databricks
> e coletar os screenshots pedidos pelo enunciado (itens 5.7 e 5.8).

## Estrutura do repositório

```
mvp-camara-deputados/
├── README.md
├── coleta.py                    # script de coleta local
├── 01_objetivo.md               # Etapas 2 e 4.1
├── 02_catalogo_dados.md         # Etapa 4.3
├── 00_bronze_ingestao.py        # Etapa 4.2 (Bronze)
├── 01_silver_transformacao.py   # Etapa 4.4 (Silver)
├── 02_gold_modelagem.py         # Etapa 4.3 (Gold / Esquema Estrela)
├── 03_qualidade_dados.py        # Etapa 4.5 (Qualidade)
└── 04_analise.py                # Etapa 4.5 (Análise / Respostas)
```

Ordem de execução no Databricks: `00` → `01` → `02` → `03` → `04`.

---

## Contexto de Negócio e Perguntas (Etapa 2 e 4.1)

Conteúdo completo em [`01_objetivo.md`](01_objetivo.md). Resumo:

**Problema:** entender os fatores que influenciam o comportamento legislativo dos deputados
federais — gasto de cota parlamentar (CEAP), produtividade legislativa e perfil por
partido/UF — usando a API de Dados Abertos da Câmara dos Deputados.

**Perguntas:**
1. Quais partidos e UFs concentram o maior gasto total de cota parlamentar (CEAP)?
2. Quais categorias de despesa são mais representativas por partido?
3. Existe relação entre proposições apresentadas e gasto de cota parlamentar?
4. Como se distribui a produção legislativa entre partidos e UFs?
5. Existe diferença no gasto médio mensal entre regiões do país?

**Fonte e licença:** Dados Abertos da Câmara dos Deputados, sob Lei de Acesso à Informação
(Lei nº 12.527/2011), uso livre com atribuição da fonte.

---

## Carga dos Dados (Etapa 4.2)

Coleta feita localmente com `coleta.py`:
- `/deputados` e `/partidos` via API REST
- Despesas (CEAP) via arquivo consolidado anual da Câmara (`Ano-{ano}.csv.zip`)
- Proposições via API REST, filtradas por autor

Os 4 CSVs resultantes são enviados por upload a um Volume do Unity Catalog e lidos pelo
notebook Bronze, que grava cada tabela em Delta com `_ingestion_ts` e `_source`.

Scripts: [`coleta.py`](coleta.py) · [`00_bronze_ingestao.py`](00_bronze_ingestao.py)

`[PREENCHER]` — Screenshot das tabelas Bronze persistidas no Unity Catalog.

---

## Modelagem e Catálogo de Dados (Etapa 4.3)

Modelo em **Esquema Estrela** na camada Gold: `dim_deputado`, `dim_partido`, `dim_tempo`
como dimensões; `fact_despesas` e `fact_proposicoes` como fatos.

Catálogo completo (todas as tabelas, campos, tipos e domínios) em
[`02_catalogo_dados.md`](02_catalogo_dados.md).

Script: [`02_gold_modelagem.py`](02_gold_modelagem.py)

`[PREENCHER]` — Screenshot do catálogo de dados no Unity Catalog / Data Explorer.

---

## Pipeline de Dados (Etapa 4.4)

Pipeline organizado em **três notebooks separados**, um por camada da Arquitetura
Medalhão, para manter cada responsabilidade isolada e fácil de depurar:

1. **Bronze** (`00_bronze_ingestao.py`): extração bruta da API, sem transformação.
2. **Silver** (`01_silver_transformacao.py`): tipagem, deduplicação, padronização e
   remoção de registros não analisáveis — com o porquê de cada decisão comentado no código.
3. **Gold** (`02_gold_modelagem.py`): modelagem em esquema estrela para consumo analítico.

Todas as tabelas são gravadas como tabelas **Delta** no Unity Catalog, uma catálogo por
camada (`bronze`, `silver`, `gold`).

`[PREENCHER]` — Screenshot confirmando a persistência das tabelas Gold na plataforma.

---

## Qualidade de Dados (Etapa 4.5)

Checagens de completude, unicidade, consistência e outliers feitas em
[`03_qualidade_dados.py`](03_qualidade_dados.py), sobre a camada Bronze
(para justificar as regras aplicadas na Silver).

`[PREENCHER]` — Tabela com os problemas encontrados e o tratamento aplicado (o notebook já
traz um template dessa tabela ao final, a ser preenchido com os números reais obtidos).

---

## Análise de Dados (Etapa 4.5)

Cada uma das 5 perguntas de negócio é respondida em
[`04_analise.py`](04_analise.py) via consultas SQL sobre a camada Gold.

`[PREENCHER]` — Para cada pergunta: screenshot do resultado + discussão do que o número
significa no contexto do problema (ex.: "a análise mostra que X, o que sugere Y").

### Pergunta 1 — `[PREENCHER]`
### Pergunta 2 — `[PREENCHER]`
### Pergunta 3 — `[PREENCHER]`
### Pergunta 4 — `[PREENCHER]`
### Pergunta 5 — `[PREENCHER]`

### Discussão geral
`[PREENCHER]` — conecte as respostas das 5 perguntas de volta ao problema original.

---

## Autoavaliação

`[PREENCHER]` após concluir o trabalho, cobrindo:
- Os objetivos traçados na Etapa 2 foram atingidos? Quais perguntas ficaram sem resposta e por quê?
- Principais dificuldades técnicas encontradas durante a execução.
- Trabalhos futuros para enriquecer o problema e a solução (ex.: incluir dados de votações,
  histórico de mais legislaturas, cruzar com dados socioeconômicos por UF).
