# Databricks notebook source
# /// script
# [tool.databricks.environment]
# environment_version = "5"
# ///
# MAGIC %md
# MAGIC # Gold — Modelagem em Star Schema
# MAGIC
# MAGIC Tabelas dimensão (`dim_*`) e tabelas fato (`fact_*`), prontas para responder
# MAGIC as perguntas de negócio da Etapa 2.

# COMMAND ----------

from pyspark.sql import functions as F

spark.sql("CREATE CATALOG IF NOT EXISTS gold")
spark.sql("CREATE SCHEMA IF NOT EXISTS gold.camara")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Mapa de região por UF (usado na Pergunta 5)

# COMMAND ----------

regiao_por_uf = {
    "AC": "Norte", "AP": "Norte", "AM": "Norte", "PA": "Norte", "RO": "Norte", "RR": "Norte", "TO": "Norte",
    "AL": "Nordeste", "BA": "Nordeste", "CE": "Nordeste", "MA": "Nordeste", "PB": "Nordeste",
    "PE": "Nordeste", "PI": "Nordeste", "RN": "Nordeste", "SE": "Nordeste",
    "DF": "Centro-Oeste", "GO": "Centro-Oeste", "MT": "Centro-Oeste", "MS": "Centro-Oeste",
    "ES": "Sudeste", "MG": "Sudeste", "RJ": "Sudeste", "SP": "Sudeste",
    "PR": "Sul", "RS": "Sul", "SC": "Sul",
}
mapa_regiao_df = spark.createDataFrame(
    [(uf, regiao) for uf, regiao in regiao_por_uf.items()], ["uf", "regiao"]
)

# COMMAND ----------

# MAGIC %md
# MAGIC ## dim_deputado

# COMMAND ----------

df_dep_silver = spark.table("silver.camara.deputados")

dim_deputado = (
    df_dep_silver
    .join(mapa_regiao_df, df_dep_silver.siglaUf == mapa_regiao_df.uf, "left")
    .select(
        F.col("id").alias("sk_deputado"),
        "nome",
        F.col("siglaPartido").alias("partido"),
        F.col("siglaUf").alias("uf"),
        "regiao",
        "email",
    )
)
dim_deputado.write.format("delta").mode("overwrite").saveAsTable("gold.camara.dim_deputado")

# COMMAND ----------

# MAGIC %md
# MAGIC ## dim_partido

# COMMAND ----------

dim_partido = (
    spark.table("silver.camara.partidos")
    .select(F.col("id").alias("sk_partido"), "sigla", "nome")
)
dim_partido.write.format("delta").mode("overwrite").saveAsTable("gold.camara.dim_partido")

# COMMAND ----------

# MAGIC %md
# MAGIC ## dim_tempo (a partir de ano/mês de despesas e proposições)

# COMMAND ----------

dim_tempo = (
    spark.table("silver.camara.despesas")
    .select("ano", "mes").distinct()
    .withColumn("sk_tempo", F.concat_ws("-", F.col("ano"), F.lpad(F.col("mes"), 2, "0")))
)
dim_tempo.write.format("delta").mode("overwrite").saveAsTable("gold.camara.dim_tempo")

# COMMAND ----------

# MAGIC %md
# MAGIC ## fact_despesas
# MAGIC Grão: uma linha por despesa individual de um deputado.

# COMMAND ----------

fact_despesas = (
    spark.table("silver.camara.despesas")
    .withColumn("sk_tempo", F.concat_ws("-", F.col("ano"), F.lpad(F.col("mes"), 2, "0")))
    .select(
        F.col("idDeputado").alias("sk_deputado"),
        "sk_tempo",
        "tipoDespesa",
        "valorDocumento",
        "nomeFornecedor",
        "dataDocumento",
    )
)
fact_despesas.write.format("delta").mode("overwrite").saveAsTable("gold.camara.fact_despesas")

# COMMAND ----------

# MAGIC %md
# MAGIC ## fact_proposicoes
# MAGIC Grão: uma linha por proposição apresentada. `sk_deputado` vem de `idDeputadoAutor`,
# MAGIC gravado durante a coleta em `/deputados/{id}/proposicoes` (ver notebook Bronze).

# COMMAND ----------

fact_proposicoes = (
    spark.table("silver.camara.proposicoes")
    .select(
        F.col("idDeputadoAutor").alias("sk_deputado"),
        "id", "siglaTipo", "numero", "ano", "ementa", "dataApresentacao",
    )
)
fact_proposicoes.write.format("delta").mode("overwrite").saveAsTable("gold.camara.fact_proposicoes")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Checagem final

# COMMAND ----------

for tbl in ["dim_deputado", "dim_partido", "dim_tempo", "fact_despesas", "fact_proposicoes"]:
    n = spark.table(f"gold.camara.{tbl}").count()
    print(f"gold.camara.{tbl}: {n} linhas")