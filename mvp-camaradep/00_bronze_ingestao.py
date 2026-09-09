# Databricks notebook source
# MAGIC %md
# MAGIC # Bronze — Ingestão a partir de arquivos enviados por upload
# MAGIC
# MAGIC **Por que este caminho, e não chamar a API direto daqui?** O compute Serverless do
# MAGIC Databricks Free Edition não tem acesso confiável à internet externa (limitação atual
# MAGIC da plataforma). Por isso, a coleta foi feita fora do Databricks — com o script
# MAGIC `coleta_local/coleta.py`, rodado no computador local — e os arquivos CSV resultantes
# MAGIC foram enviados via upload para um Volume do Unity Catalog. Esse é um dos dois caminhos
# MAGIC de coleta previstos no próprio enunciado do MVP ("baixe o dataset e faça upload").
# MAGIC
# MAGIC **Antes de rodar este notebook:**
# MAGIC 1. Rode `coleta_local/coleta.py` no seu computador (veja instruções no topo do arquivo).
# MAGIC 2. No Databricks, vá em Catalog > seu catálogo > Create Volume (ou use um já existente).
# MAGIC 3. Dentro do Volume, clique em "Upload files" e envie os 4 CSVs gerados
# MAGIC    (`deputados.csv`, `partidos.csv`, `despesas.csv`, `proposicoes.csv`).
# MAGIC 4. Ajuste `VOLUME_PATH` abaixo para o caminho do seu Volume.

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
 .option("mergeSchema", "true")
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
 .option("mergeSchema", "true")
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
 .option("mergeSchema", "true")
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
 .option("mergeSchema", "true")
 .saveAsTable("bronze.camara.proposicoes"))
print(f"bronze.camara.proposicoes: {df_proposicoes_bronze.count()} linhas")

# COMMAND ----------

# MAGIC %md ## Checagem rápida

# COMMAND ----------

for tbl in ["deputados", "despesas", "proposicoes", "partidos"]:
    n = spark.table(f"bronze.camara.{tbl}").count()
    print(f"bronze.camara.{tbl}: {n} linhas")
