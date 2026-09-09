# Databricks notebook source
# /// script
# [tool.databricks.environment]
# environment_version = "5"
# ///
# MAGIC %md
# MAGIC # Bronze — Ingestão a partir de arquivos enviados por upload
# MAGIC
# MAGIC **Por que este caminho, e não chamar a API direto daqui?** O compute Serverless do
# MAGIC Databricks Free Edition não tem acesso confiável à internet externa (limitação atual
# MAGIC da plataforma). Por isso, a coleta foi feita fora do Databricks — com o script
# MAGIC `coleta_local/coleta.py`, rodado no computador local — e os arquivos CSV resultantes
# MAGIC foram enviados via upload para um Volume do Unity Catalog. Esse é um dos dois
