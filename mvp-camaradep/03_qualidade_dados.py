# Databricks notebook source
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
# MAGIC | Problema encontrado | Tabela | Tratamento aplicado (camada Silver) |
# MAGIC |---|---|---|
# MAGIC | 316 IDs de deputado duplicados (de 1.073 registros) | deputados | `dropDuplicates` por `id` |
# MAGIC | Campo `email` 100% nulo (1.073/1.073) | deputados | Mantido como está — não é usado nas análises |
# MAGIC | Campos quase totalmente nulos (`cpf` 100%, `txtTrecho` 100%, `numRessarcimento` 100%, `datPagamentoRestituicao` 100%, `vlrRestituicao` 100%, `txtPassageiro` 99,82%, `txtDescricaoEspecificacao` 55,24%) | despesas | Descartados na seleção da Silver — campos específicos de passagens aéreas/restituições que não entram no modelo |
# MAGIC | Valores negativos, zerados ou outliers extremos (>3x o percentil 99) | despesas | Nenhum encontrado (0 casos) |
# MAGIC | Mês fora do intervalo 1–12 | despesas | Nenhum encontrado (0 casos) |
# MAGIC | 140 IDs de proposição duplicados (de 6.009 registros) | proposicoes | `dropDuplicates` por `id` |
# MAGIC | Campo `ementa` com 1,07% de nulos | proposicoes | Mantido como está — proporção baixa |
