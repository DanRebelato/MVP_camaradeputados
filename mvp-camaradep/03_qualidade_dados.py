# Databricks notebook source
# /// script
# [tool.databricks.environment]
# environment_version = "5"
# ///
# MAGIC %md
# MAGIC # Qualidade de Dados (Etapa 4.5)
# MAGIC
# MAGIC Checagem de completude, consistência, unicidade, acurácia e outliers nas tabelas
# MAGIC Bronze (dado como chegou), para justificar as transformações feitas na Silver.

# COMMAND ----------

from pyspark.sql import functions as F

def relatorio_nulos(df, nome_tabela):
    total = df.count()
    print(f"\n--- Completude: {nome_tabela} ({total} linhas) ---")
    for c in df.columns:
        nulos = df.filter(F.col(c).isNull()).count()
        pct = round(100 * nulos / total, 2) if total else 0
        if nulos > 0:
            print(f"  {c}: {nulos} nulos ({pct}%)")

# COMMAND ----------

# MAGIC %md ## Deputados

# COMMAND ----------

df_dep = spark.table("bronze.camara.deputados")
relatorio_nulos(df_dep, "deputados")

# Unicidade: id deveria ser único
dup_ids = df_dep.groupBy("id").count().filter("count > 1").count()
print(f"IDs de deputado duplicados: {dup_ids}")

# COMMAND ----------

# MAGIC %md ## Despesas

# COMMAND ----------

df_desp = spark.table("bronze.camara.despesas")
relatorio_nulos(df_desp, "despesas")

# Acurácia: valores negativos ou zerados
neg = df_desp.filter(F.col("vlrDocumento") < 0).count()
zero = df_desp.filter(F.col("vlrDocumento") == 0).count()
print(f"Despesas com valor negativo: {neg}")
print(f"Despesas com valor zero: {zero}")

# Outliers: valores muito acima do 99º percentil
p99 = df_desp.approxQuantile("vlrDocumento", [0.99], 0.01)[0]
outliers = df_desp.filter(F.col("vlrDocumento") > p99 * 3).count()
print(f"Percentil 99 do valor de despesa: {p99}")
print(f"Despesas > 3x o percentil 99 (possíveis outliers): {outliers}")

# Consistência: meses fora do intervalo 1-12
mes_invalido = df_desp.filter(~F.col("numMes").between(1, 12)).count()
print(f"Registros com mês inválido: {mes_invalido}")

# COMMAND ----------

# MAGIC %md ## Proposições

# COMMAND ----------

df_prop = spark.table("bronze.camara.proposicoes")
relatorio_nulos(df_prop, "proposicoes")

dup_prop = df_prop.groupBy("id").count().filter("count > 1").count()
print(f"IDs de proposição duplicados: {dup_prop}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Resumo dos problemas encontrados e tratamento aplicado
# MAGIC
# MAGIC Preencha esta seção após rodar as células acima, com os números reais do seu conjunto de dados. Exemplo de estrutura:
# MAGIC
# MAGIC | Problema encontrado | Tabela | Tratamento aplicado (camada Silver) |
# MAGIC |---|---|---|
# MAGIC | Nulos em `valorDocumento` | despesas | Registros descartados (não analisáveis) |
# MAGIC | Duplicatas por variação de grafia em `nomeFornecedor` | despesas | Padronização com `trim` + `upper` antes da deduplicação |
# MAGIC | Valores negativos em `valorDocumento` | despesas | Filtrados (representam estornos, fora do escopo da análise) |
# MAGIC | IDs duplicados por reingestão | deputados / proposições | `dropDuplicates` por chave natural |