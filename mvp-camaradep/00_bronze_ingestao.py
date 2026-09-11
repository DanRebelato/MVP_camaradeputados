# Databricks notebook source
# /// script
# [tool.databricks.environment]
# environment_version = "5"
# ///
# MAGIC %md
# MAGIC # Bronze — Ingestão a partir de arquivos enviados por upload
# MAGIC
# MAGIC Coleta feita localmente (`coleta_local/coleta.py`) e enviada por upload a um Volume
# MAGIC do Unity Catalog
# MAGIC
# MAGIC **Antes de rodar este notebook:**
# MAGIC 1. Rodar `coleta_local/coleta.py` localmente.
# MAGIC 2. No Databricks: Catalog > seu catálogo > Create Volume.
# MAGIC 3. Dentro do Volume: "Upload files", para subir os 4 CSVs gerados
# MAGIC    (`deputados.csv`, `partidos.csv`, `despesas.csv`, `proposicoes.csv`).
# MAGIC 4. Ajustar `VOLUME_PATH` abaixo para o caminho do Volume.

# COMMAND ----------

from datetime import datetime
from pyspark.sql import functions as F

# AJUSTE AQUI: caminho do seu Volume (Catalog Explorer mostra o caminho completo)
VOLUME_PATH = "/Volumes/workspace/default/mvp_camara"

INGESTAO_TS = datetime.utcnow().isoformat()

spark.sql("CREATE CATALOG IF NOT EXISTS bronze")
spark.sql("CREATE SCHEMA IF NOT EXISTS bronze.camara")

# COMMAND ----------

# MAGIC %md ## 1. Deputados

# COMMAND ----------

df_deputados_bronze = (
    spark.read.format("csv")
    .option("header", "true")
    .option("inferSchema", "true")
    .load(f"{VOLUME_PATH}/deputados.csv")
    .withColumn("_source", F.lit("/deputados"))
)
(df_deputados_bronze.write.format("delta").mode("overwrite")
 .option("overwriteSchema", "true")
 .saveAsTable("bronze.camara.deputados"))
print(f"bronze.camara.deputados: {df_deputados_bronze.count()} linhas")

# COMMAND ----------

# MAGIC %md ## 2. Partidos

# COMMAND ----------

df_partidos_bronze = (
    spark.read.format("csv")
    .option("header", "true")
    .option("inferSchema", "true")
    .load(f"{VOLUME_PATH}/partidos.csv")
    .withColumn("_source", F.lit("/partidos"))
)
(df_partidos_bronze.write.format("delta").mode("overwrite")
 .option("overwriteSchema", "true")
 .saveAsTable("bronze.camara.partidos"))
print(f"bronze.camara.partidos: {df_partidos_bronze.count()} linhas")

# COMMAND ----------

# MAGIC %md ## 3. Despesas

# COMMAND ----------

df_despesas_bronze = (
    spark.read.format("csv")
    .option("header", "true")
    .option("inferSchema", "true")
    .option("multiLine", "true")
    .option("escape", '"')
    .load(f"{VOLUME_PATH}/despesas.csv")
    .withColumn("_source", F.lit("/deputados/{id}/despesas"))
)
(df_despesas_bronze.write.format("delta").mode("overwrite")
 .option("overwriteSchema", "true")
 .saveAsTable("bronze.camara.despesas"))
print(f"bronze.camara.despesas: {df_despesas_bronze.count()} linhas")

# COMMAND ----------

# MAGIC %md ## 4. Proposições

# COMMAND ----------

df_proposicoes_bronze = (
    spark.read.format("csv")
    .option("header", "true")
    .option("inferSchema", "true")
    .option("multiLine", "true")
    .option("escape", '"')
    .load(f"{VOLUME_PATH}/proposicoes.csv")
    .withColumn("_source", F.lit("/proposicoes"))
)
(df_proposicoes_bronze.write.format("delta").mode("overwrite")
 .option("overwriteSchema", "true")
 .saveAsTable("bronze.camara.proposicoes"))
print(f"bronze.camara.proposicoes: {df_proposicoes_bronze.count()} linhas")

# COMMAND ----------

# MAGIC %md ## Checagem rápida

# COMMAND ----------

for tbl in ["deputados", "despesas", "proposicoes", "partidos"]:
    n = spark.table(f"bronze.camara.{tbl}").count()
    print(f"bronze.camara.{tbl}: {n} linhas")