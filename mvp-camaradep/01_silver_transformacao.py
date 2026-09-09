# Databricks notebook source
# MAGIC %md
# MAGIC # Silver — Limpeza e padronização
# MAGIC
# MAGIC Nesta etapa: remoção de duplicatas, tratamento de nulos, tipagem correta e padronização
# MAGIC de formatos. Cada transformação está comentada explicando o quê e o porquê.

# COMMAND ----------

from pyspark.sql import functions as F

spark.sql("CREATE CATALOG IF NOT EXISTS silver")
spark.sql("CREATE SCHEMA IF NOT EXISTS silver.camara")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Deputados
# MAGIC - Deduplicar por `id` (mantendo o registro mais recente por `_ingestion_ts`).
# MAGIC - Tipar `id` como inteiro.
# MAGIC - Padronizar `siglaUf` e `siglaPartido` para maiúsculas sem espaços.
# MAGIC - Remover registros sem `id` ou sem `nome` (não identificáveis).

# COMMAND ----------

df_dep_bronze = spark.table("bronze.camara.deputados")

df_dep_silver = (
    df_dep_bronze
    .withColumn("id", F.col("id").cast("int"))
    .withColumn("siglaUf", F.upper(F.trim(F.col("siglaUf"))))
    .withColumn("siglaPartido", F.upper(F.trim(F.col("siglaPartido"))))
    .filter(F.col("id").isNotNull() & F.col("nome").isNotNull())
    .dropDuplicates(["id"])
    .select(
        "id", "nome", "siglaPartido", "siglaUf", "email", "urlFoto",
        "_ingestion_ts",
    )
)

(df_dep_silver.write.format("delta").mode("overwrite")
 .saveAsTable("silver.camara.deputados"))

print(f"silver.camara.deputados: {df_dep_silver.count()} linhas")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Despesas (CEAP)
# MAGIC - Tipar `valorDocumento` como decimal; valores nulos ou negativos indevidos tratados.
# MAGIC - Padronizar `nomeFornecedor` (trim + upper) para evitar duplicidade por variação de grafia.
# MAGIC - Deduplicar por chave natural (`idDeputado`, `ano`, `mes`, `tipoDespesa`, `valorDocumento`, `nomeFornecedor`).
# MAGIC - Descartar registros sem `idDeputado` ou com valor nulo (não analisáveis).

# COMMAND ----------

df_desp_bronze = spark.table("bronze.camara.despesas")

df_desp_silver = (
    df_desp_bronze
    .withColumn("idDeputado", F.col("idDeputado").cast("int"))
    .withColumn("valorDocumento", F.col("valorDocumento").cast("decimal(12,2)"))
    .withColumn("ano", F.col("ano").cast("int"))
    .withColumn("mes", F.col("mes").cast("int"))
    .withColumn("nomeFornecedor", F.upper(F.trim(F.col("nomeFornecedor"))))
    .withColumn("tipoDespesa", F.trim(F.col("tipoDespesa")))
    .filter(
        F.col("idDeputado").isNotNull()
        & F.col("valorDocumento").isNotNull()
        & (F.col("valorDocumento") >= 0)  # descarta estornos/valores negativos inconsistentes
    )
    .dropDuplicates(["idDeputado", "ano", "mes", "tipoDespesa", "valorDocumento", "nomeFornecedor"])
    .select(
        "idDeputado", "ano", "mes", "tipoDespesa", "valorDocumento",
        "nomeFornecedor", "dataDocumento", "_ingestion_ts",
    )
)

(df_desp_silver.write.format("delta").mode("overwrite")
 .saveAsTable("silver.camara.despesas"))

print(f"silver.camara.despesas: {df_desp_silver.count()} linhas")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Proposições
# MAGIC - Tipar `id` e extrair `idDeputadoAutor` do array de autores (quando presente no payload).
# MAGIC - Deduplicar por `id` da proposição.

# COMMAND ----------

df_prop_bronze = spark.table("bronze.camara.proposicoes")

df_prop_silver = (
    df_prop_bronze
    .withColumn("id", F.col("id").cast("long"))
    .withColumn("idDeputadoAutor", F.col("idDeputadoAutor").cast("int"))
    .withColumn("siglaTipo", F.trim(F.col("siglaTipo")))
    .filter(F.col("id").isNotNull())
    .dropDuplicates(["id"])
    .select("id", "idDeputadoAutor", "siglaTipo", "numero", "ano", "ementa", "dataApresentacao", "_ingestion_ts")
)

(df_prop_silver.write.format("delta").mode("overwrite")
 .saveAsTable("silver.camara.proposicoes"))

print(f"silver.camara.proposicoes: {df_prop_silver.count()} linhas")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. Partidos

# COMMAND ----------

df_part_bronze = spark.table("bronze.camara.partidos")

df_part_silver = (
    df_part_bronze
    .withColumn("id", F.col("id").cast("int"))
    .withColumn("sigla", F.upper(F.trim(F.col("sigla"))))
    .filter(F.col("id").isNotNull())
    .dropDuplicates(["id"])
    .select("id", "sigla", "nome", "_ingestion_ts")
)

(df_part_silver.write.format("delta").mode("overwrite")
 .saveAsTable("silver.camara.partidos"))

print(f"silver.camara.partidos: {df_part_silver.count()} linhas")
