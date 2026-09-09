# Databricks notebook source
# MAGIC %md
# MAGIC # Bronze — Ingestão bruta da API da Câmara dos Deputados
# MAGIC
# MAGIC Objetivo desta etapa: trazer os dados **exatamente como vêm da API**, sem transformação,
# MAGIC apenas adicionando metadados de controle (data de ingestão e fonte).
# MAGIC
# MAGIC Camada: `bronze` (catálogo/schema `bronze` no Unity Catalog).

# COMMAND ----------

import requests
import time
from datetime import datetime
from pyspark.sql import Row

BASE_URL = "https://dadosabertos.camara.leg.br/api/v2"
HEADERS = {"Accept": "application/json"}
INGESTAO_TS = datetime.utcnow().isoformat()

spark.sql("CREATE CATALOG IF NOT EXISTS bronze")
spark.sql("CREATE SCHEMA IF NOT EXISTS bronze.camara")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Função utilitária de paginação
# MAGIC A API da Câmara pagina resultados via `?pagina=N&itens=100`. Percorremos até a página vir vazia.

# COMMAND ----------

def get_paginated(endpoint, params=None, max_pages=200):
    params = dict(params or {})
    params.setdefault("itens", 100)
    pagina = 1
    resultados = []
    while pagina <= max_pages:
        params["pagina"] = pagina
        resp = requests.get(f"{BASE_URL}{endpoint}", params=params, headers=HEADERS, timeout=30)
        resp.raise_for_status()
        dados = resp.json().get("dados", [])
        if not dados:
            break
        resultados.extend(dados)
        pagina += 1
        time.sleep(0.2)  # boa cidadania com a API pública
    return resultados

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Deputados em exercício

# COMMAND ----------

deputados_raw = get_paginated("/deputados", params={"ordem": "ASC", "ordenarPor": "nome"})
print(f"Deputados coletados: {len(deputados_raw)}")

df_deputados_bronze = spark.createDataFrame([Row(**d) for d in deputados_raw])
df_deputados_bronze = (
    df_deputados_bronze
    .withColumn("_ingestion_ts", spark.sql(f"SELECT '{INGESTAO_TS}'").collect()[0][0])
    .withColumn("_source", spark.sql("SELECT '/deputados'").collect()[0][0])
)

(df_deputados_bronze.write.format("delta").mode("overwrite")
 .option("mergeSchema", "true")
 .saveAsTable("bronze.camara.deputados"))

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Despesas (CEAP) por deputado
# MAGIC Iteramos sobre a lista de deputados coletada acima. Ajuste `ANOS` conforme necessário.

# COMMAND ----------

ANOS = [2025, 2026]
despesas_raw = []

ids_deputados = [d["id"] for d in deputados_raw]

for i, dep_id in enumerate(ids_deputados):
    for ano in ANOS:
        try:
            despesas = get_paginated(f"/deputados/{dep_id}/despesas", params={"ano": ano})
            for d in despesas:
                d["idDeputado"] = dep_id
                d["anoConsulta"] = ano
            despesas_raw.extend(despesas)
        except Exception as e:
            print(f"Falha ao coletar despesas do deputado {dep_id} / ano {ano}: {e}")
    if (i + 1) % 50 == 0:
        print(f"{i + 1}/{len(ids_deputados)} deputados processados...")

print(f"Registros de despesas coletados: {len(despesas_raw)}")

# COMMAND ----------

df_despesas_bronze = spark.createDataFrame([Row(**d) for d in despesas_raw])
df_despesas_bronze = (
    df_despesas_bronze
    .withColumn("_ingestion_ts", spark.sql(f"SELECT '{INGESTAO_TS}'").collect()[0][0])
    .withColumn("_source", spark.sql("SELECT '/deputados/{id}/despesas'").collect()[0][0])
)

(df_despesas_bronze.write.format("delta").mode("overwrite")
 .option("mergeSchema", "true")
 .saveAsTable("bronze.camara.despesas"))

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Proposições de autoria dos deputados

# COMMAND ----------

proposicoes_raw = []
for i, dep_id in enumerate(ids_deputados):
    try:
        props = get_paginated("/proposicoes", params={
            "idDeputadoAutor": dep_id,
            "ano": 2025,
        })
        for p in props:
            p["idDeputadoAutor"] = dep_id
        proposicoes_raw.extend(props)
    except Exception as e:
        print(f"Falha ao coletar proposições do deputado {dep_id}: {e}")
    if (i + 1) % 50 == 0:
        print(f"{i + 1}/{len(ids_deputados)} deputados processados...")

print(f"Proposições coletadas: {len(proposicoes_raw)}")

df_proposicoes_bronze = spark.createDataFrame([Row(**p) for p in proposicoes_raw])
df_proposicoes_bronze = (
    df_proposicoes_bronze
    .withColumn("_ingestion_ts", spark.sql(f"SELECT '{INGESTAO_TS}'").collect()[0][0])
    .withColumn("_source", spark.sql("SELECT '/proposicoes'").collect()[0][0])
)

(df_proposicoes_bronze.write.format("delta").mode("overwrite")
 .option("mergeSchema", "true")
 .saveAsTable("bronze.camara.proposicoes"))

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. Partidos

# COMMAND ----------

partidos_raw = get_paginated("/partidos")
df_partidos_bronze = spark.createDataFrame([Row(**p) for p in partidos_raw])
df_partidos_bronze = (
    df_partidos_bronze
    .withColumn("_ingestion_ts", spark.sql(f"SELECT '{INGESTAO_TS}'").collect()[0][0])
    .withColumn("_source", spark.sql("SELECT '/partidos'").collect()[0][0])
)

(df_partidos_bronze.write.format("delta").mode("overwrite")
 .option("mergeSchema", "true")
 .saveAsTable("bronze.camara.partidos"))

# COMMAND ----------

# MAGIC %md
# MAGIC ## Checagem rápida

# COMMAND ----------

for tbl in ["deputados", "despesas", "proposicoes", "partidos"]:
    n = spark.table(f"bronze.camara.{tbl}").count()
    print(f"bronze.camara.{tbl}: {n} linhas")
