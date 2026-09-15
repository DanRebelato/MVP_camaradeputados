# MVP de Engenharia de Dados — Comportamento Legislativo dos Deputados Federais

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
federais, gasto de cota parlamentar (CEAP), produtividade legislativa e perfil por
partido/UF. Usando a API de Dados Abertos da Câmara dos Deputados.

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

<img width="646" height="297" alt="PRINT 1" src="https://github.com/user-attachments/assets/7d8db0aa-1b69-4e83-aef7-8755685cd52b" />
— Screenshot das tabelas Bronze persistidas no Unity Catalog.

---

## Modelagem e Catálogo de Dados (Etapa 4.3)

Modelo em **Star Schema** na camada Gold: `dim_deputado`, `dim_partido`, `dim_tempo`
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

`[PREENCHER]` — screenshot da saída do notebook.

| Problema encontrado | Tabela | Tratamento aplicado (camada Silver) |
|---|---|---|
| 316 IDs de deputado duplicados (de 1.073 registros) | deputados | `dropDuplicates` por `id` |
| Campo `email` 100% nulo (1.073/1.073) | deputados | Mantido como está — não é usado nas análises |
| Campos quase totalmente nulos (`cpf` 100%, `txtTrecho` 100%, `numRessarcimento` 100%, `datPagamentoRestituicao` 100%, `vlrRestituicao` 100%, `txtPassageiro` 99,82%, `txtDescricaoEspecificacao` 55,24%) | despesas | Descartados na seleção da Silver — são campos específicos de passagens aéreas/restituições, que não se aplicam à maioria das despesas e não entram no modelo |
| Valores negativos, zerados ou outliers extremos (>3x o percentil 99) | despesas | Nenhum encontrado (0 casos) — dado já veio limpo nesse aspecto |
| Mês fora do intervalo 1–12 | despesas | Nenhum encontrado (0 casos) |
| 140 IDs de proposição duplicados (de 6.009 registros) | proposicoes | `dropDuplicates` por `id` |
| Campo `ementa` com 1,07% de nulos | proposicoes | Mantido como está — proporção baixa, não compromete a análise |

---

## Análise de Dados (Etapa 4.5)

Cada uma das 5 perguntas de negócio é respondida em
[`04_analise.py`](04_analise.py) via consultas SQL sobre a camada Gold.

`[PREENCHER]` — Para cada pergunta: screenshot do resultado + discussão do que o número
significa no contexto do problema (ex.: "a análise mostra que X, o que sugere Y").

### Pergunta 1 — Gasto por partido e UF
Os maiores gastos totais concentram-se em PSL-PR (R$ 787.890), PSD-BA (R$ 764.280) e DEM-BA
(R$ 719.827). Mas o gasto médio por despesa conta outra história: PRB-AM tem média de
R$ 29.357 por despesa — muito acima do restante —, indicando poucas despesas de valor alto,
não um volume grande de gastos pequenos. Já PSL-PR gasta muito, mas em despesas de ticket
médio baixo (R$ 1.333).

`[PREENCHER]` — screenshot do resultado dessa consulta.

### Pergunta 2 — Categorias de despesa por partido
As categorias variam bastante conforme o partido. O DEM concentra gastos em "Manutenção de
escritório" (R$ 388.772) e "Locação de veículos" (R$ 331.278) — despesas estruturais
recorrentes. Já o PR gasta majoritariamente em "Divulgação da atividade parlamentar"
(R$ 504.749, mais da metade do total do partido) — um perfil voltado a comunicação e
visibilidade, não a estrutura.

`[PREENCHER]` — screenshot do resultado dessa consulta.

### Pergunta 3 — Proposições x gasto de cota parlamentar
A correlação encontrada foi de **0,308** — positiva, mas fraca a moderada. Gastar mais da
cota não anda necessariamente junto com produzir mais proposições. O caso mais evidente é
Silas Câmara (PRB-AM): 4.489 proposições — disparado o maior número da amostra — com gasto
moderado (R$ 645.846), mostrando que dá pra ser hiperprodutivo legislativamente sem gastar
proporcionalmente mais.

`[PREENCHER]` — screenshot do resultado dessa consulta e do cálculo de correlação.

### Pergunta 4 — Produção legislativa por partido/UF
A produção é extremamente concentrada: PRB-AM lidera com 4.489 proposições, mas isso é
puxado por um único deputado (Silas Câmara), não por um padrão do partido ou do estado.
Tirando esse outlier, os números caem para a casa das dezenas ou centenas — a produtividade
legislativa parece mais uma característica individual do que um traço de partido/UF.

`[PREENCHER]` — screenshot do resultado dessa consulta.

### Pergunta 5 — Gasto médio mensal por região
Sudeste (R$ 169.353/mês) e Nordeste (R$ 149.244/mês) têm gasto médio mensal bem acima de Sul
(R$ 80.248), Centro-Oeste (R$ 59.337) e Norte (R$ 58.713) — uma diferença de quase 3x entre
as pontas. Isso pode refletir tanto o custo de vida/deslocamento nessas regiões quanto o
tamanho da amostra por região (a amostra é pequena, então isso pesa no resultado).

`[PREENCHER]` — screenshot do resultado dessa consulta.

### Discussão geral
Os dados sugerem que o comportamento legislativo dos deputados na amostra não segue um
padrão único ligado a partido ou UF — ele varia mais por perfil individual do parlamentar
(como fica claro no caso de Silas Câmara) do que por filiação partidária ou geografia. A
correlação fraca entre proposições e gasto (0,308) reforça que gasto de cota parlamentar e
produção legislativa são fenômenos relativamente independentes. As diferenças regionais de
gasto (Pergunta 5) são o padrão mais consistente encontrado, e provavelmente merecem uma
leitura combinada com custo de vida/deslocamento regional — um ponto para investigar em
trabalhos futuros. Vale registrar que esses resultados vêm de uma amostra de 40 deputados
(não o total de 513), então servem como indício, não como conclusão definitiva sobre o
comportamento da Câmara como um todo.

---

## Autoavaliação

As cinco perguntas definidas na Etapa 2 foram respondidas com dados reais, então o objetivo
principal foi atingido. A maior ressalva é o tamanho da amostra: por limitações de tempo e
de infraestrutura (detalhadas abaixo), o pipeline processa 40 dos 513 deputados em exercício,
não o total. Os padrões encontrados (ex.: a fraca correlação entre proposições e gasto, ou a
concentração de produção legislativa em poucos deputados) são indícios consistentes com essa
amostra, mas não podem ser generalizados para a Câmara como um todo sem rodar o pipeline com
mais dados.

A maior dificuldade não foi a modelagem ou o Spark em si, foi a coleta. O Databricks Free
Edition não tem acesso à internet externa no compute Serverless, então chamar a API da Câmara
direto de dentro de um notebook simplesmente não funciona — precisei mover a coleta pra rodar
localmente e subir os CSVs por upload. Depois, descobri que o próprio endpoint de despesas da
API REST (`/deputados/{id}/despesas`) está retornando vazio para 2024 em diante, mesmo para
deputados com gasto real e público — inclusive testei com o presidente da Câmara e o resultado
foi zero. A solução foi trocar de fonte: usar o arquivo consolidado por ano que a própria
Câmara disponibiliza (`Ano-{ano}.csv.zip`), que tem uma estrutura de colunas diferente da API
e exigiu ajustar o mapeamento de campos nas camadas Silver, Gold e de qualidade de dados.

Trabalhos futuros: rodar a coleta com todos os 513 deputados em vez da amostra de 40; incluir
dados de votações para enriquecer a análise de comportamento legislativo; cruzar o gasto
regional (Pergunta 5) com dados de custo de vida por UF, já que a diferença encontrada entre
regiões pode estar mais ligada a isso do que ao comportamento do parlamentar em si; e investigar
por que a busca de deputados por `idLegislatura=56` retornou 1.073 registros (mais que o
esperado — provavelmente inclui suplentes que passaram pelo cargo ao longo da legislatura),
pra decidir se vale filtrar só os titulares atuais.
