# Databricks notebook source
# /// script
# [tool.databricks.environment]
# environment_version = "5"
# ///
# MAGIC %md
# MAGIC # Análise de Dados (Etapa 4.5)
# MAGIC
# MAGIC Cada seção abaixo responde a uma das 5 perguntas de negócio definidas em `docs/01_objetivo.md`.
# MAGIC Rode cada célula, capture o screenshot do resultado (tabela ou gráfico) para colar no README.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Pergunta 1 — Gasto total de CEAP por partido e UF

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT d.partido, d.uf, ROUND(SUM(f.valorDocumento), 2) AS gasto_total,
# MAGIC        ROUND(AVG(f.valorDocumento), 2) AS gasto_medio_por_despesa
# MAGIC FROM gold.camara.fact_despesas f
# MAGIC JOIN gold.camara.dim_deputado d ON f.sk_deputado = d.sk_deputado
# MAGIC GROUP BY d.partido, d.uf
# MAGIC ORDER BY gasto_total DESC
# MAGIC LIMIT 20

# COMMAND ----------

# MAGIC %md
# MAGIC ## Pergunta 2 — Categorias de despesa mais representativas por partido

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT d.partido, f.tipoDespesa, ROUND(SUM(f.valorDocumento), 2) AS gasto_total
# MAGIC FROM gold.camara.fact_despesas f
# MAGIC JOIN gold.camara.dim_deputado d ON f.sk_deputado = d.sk_deputado
# MAGIC GROUP BY d.partido, f.tipoDespesa
# MAGIC ORDER BY d.partido, gasto_total DESC

# COMMAND ----------

# MAGIC %md
# MAGIC ## Pergunta 3 — Relação entre proposições apresentadas e gasto de cota parlamentar

# COMMAND ----------

# MAGIC %sql
# MAGIC WITH gasto AS (
# MAGIC   SELECT sk_deputado, SUM(valorDocumento) AS gasto_total
# MAGIC   FROM gold.camara.fact_despesas
# MAGIC   GROUP BY sk_deputado
# MAGIC ),
# MAGIC producao AS (
# MAGIC   SELECT sk_deputado, COUNT(*) AS total_proposicoes
# MAGIC   FROM gold.camara.fact_proposicoes
# MAGIC   GROUP BY sk_deputado
# MAGIC )
# MAGIC SELECT d.nome, d.partido, COALESCE(p.total_proposicoes, 0) AS total_proposicoes,
# MAGIC        COALESCE(g.gasto_total, 0) AS gasto_total
# MAGIC FROM gold.camara.dim_deputado d
# MAGIC LEFT JOIN gasto g ON d.sk_deputado = g.sk_deputado
# MAGIC LEFT JOIN producao p ON d.sk_deputado = p.sk_deputado
# MAGIC ORDER BY total_proposicoes DESC

# COMMAND ----------

# MAGIC %md
# MAGIC Para quantificar a relação, calcule a correlação entre as duas colunas:

# COMMAND ----------

df_corr = spark.sql("""
    WITH gasto AS (
      SELECT sk_deputado, SUM(valorDocumento) AS gasto_total
      FROM gold.camara.fact_despesas GROUP BY sk_deputado
    ),
    producao AS (
      SELECT sk_deputado, COUNT(*) AS total_proposicoes
      FROM gold.camara.fact_proposicoes GROUP BY sk_deputado
    )
    SELECT COALESCE(p.total_proposicoes, 0) AS total_proposicoes,
           COALESCE(g.gasto_total, 0) AS gasto_total
    FROM gold.camara.dim_deputado d
    LEFT JOIN gasto g ON d.sk_deputado = g.sk_deputado
    LEFT JOIN producao p ON d.sk_deputado = p.sk_deputado
""")
correlacao = df_corr.stat.corr("total_proposicoes", "gasto_total")
print(f"Correlação entre nº de proposições e gasto total: {correlacao:.3f}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Pergunta 4 — Produção legislativa por partido e UF

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT d.partido, d.uf, COUNT(*) AS total_proposicoes
# MAGIC FROM gold.camara.fact_proposicoes f
# MAGIC JOIN gold.camara.dim_deputado d ON f.sk_deputado = d.sk_deputado
# MAGIC GROUP BY d.partido, d.uf
# MAGIC ORDER BY total_proposicoes DESC
# MAGIC LIMIT 20

# COMMAND ----------

# MAGIC %md
# MAGIC ## Pergunta 5 — Gasto médio mensal por região do país

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT d.regiao,
# MAGIC        ROUND(SUM(f.valorDocumento) / COUNT(DISTINCT f.sk_tempo), 2) AS gasto_medio_mensal_regiao
# MAGIC FROM gold.camara.fact_despesas f
# MAGIC JOIN gold.camara.dim_deputado d ON f.sk_deputado = d.sk_deputado
# MAGIC GROUP BY d.regiao
# MAGIC ORDER BY gasto_medio_mensal_regiao DESC

# COMMAND ----------

# MAGIC %md
# MAGIC ## Discussão geral
# MAGIC
# MAGIC Preencha após rodar as consultas acima, conectando os resultados numéricos de volta
# MAGIC ao problema original (ex.: "os dados mostram que X, o que sugere Y sobre o comportamento
# MAGIC legislativo dos deputados").