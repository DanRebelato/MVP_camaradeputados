"""
Coleta de dados - MVP Câmara dos Deputados

Baixa deputados, partidos, despesas (CEAP, via arquivo consolidado anual) e
proposições de uma amostra de deputados, salvando em dados_coletados/*.csv.

Requer: pip install requests pandas
Uso: python coleta.py
"""

import requests
import pandas as pd
import time
import os
import io
import zipfile

BASE_URL = "https://dadosabertos.camara.leg.br/api/v2"
HEADERS = {"Accept": "application/json"}
OUTPUT_DIR = "dados_coletados"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Quantos deputados incluir na amostra de despesas/proposições.
# Aumente esse número se quiser um conjunto de dados maior (mais lento).
TAMANHO_AMOSTRA = 40
ANOS_DESPESAS = [2025, 2026]


def get_paginated(endpoint, params=None, max_pages=50):
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
        time.sleep(0.2)
    return resultados


def baixar_despesas_ano(ano):
    """Baixa o arquivo consolidado de despesas (CEAP) de um ano inteiro,
    direto do portal da Câmara (não é a API REST — é o arquivo em lote,
    que é a fonte oficial recomendada para esse tipo de dado)."""
    url = f"https://www.camara.leg.br/cotas/Ano-{ano}.csv.zip"
    print(f"    Baixando arquivo consolidado de {ano}... ({url})")
    resp = requests.get(url, timeout=120)
    resp.raise_for_status()
    with zipfile.ZipFile(io.BytesIO(resp.content)) as z:
        nome_csv = z.namelist()[0]
        with z.open(nome_csv) as f:
            # Esse arquivo usa ; como separador e vem com um cabeçalho de metadados extra
            df = pd.read_csv(f, sep=";", encoding="utf-8", skiprows=0, low_memory=False, on_bad_lines="skip")
    return df


def main():
    print("1/4 - Baixando lista de deputados...")
    deputados = get_paginated("/deputados", params={"ordem": "ASC", "ordenarPor": "nome", "idLegislatura": 56})
    df_deputados = pd.DataFrame(deputados)
    df_deputados["_ingestion_ts"] = pd.Timestamp.utcnow().isoformat()
    df_deputados.to_csv(f"{OUTPUT_DIR}/deputados.csv", index=False)
    print(f"    {len(df_deputados)} deputados salvos.")

    print("2/4 - Baixando lista de partidos...")
    partidos = get_paginated("/partidos")
    df_partidos = pd.DataFrame(partidos)
    df_partidos["_ingestion_ts"] = pd.Timestamp.utcnow().isoformat()
    df_partidos.to_csv(f"{OUTPUT_DIR}/partidos.csv", index=False)
    print(f"    {len(df_partidos)} partidos salvos.")

    # Amostra ALEATÓRIA (não os primeiros em ordem alfabética) — isso evita pegar,
    # por coincidência, um grupo de deputados sem despesas registradas.
    amostra = df_deputados.sample(n=min(TAMANHO_AMOSTRA, len(df_deputados)), random_state=42)
    ids_amostra = set(amostra["id"].astype(int))

    print(f"3/4 - Baixando despesas (arquivo consolidado por ano, filtrando os {len(amostra)} deputados da amostra)...")
    partes = []
    for ano in ANOS_DESPESAS:
        try:
            df_ano = baixar_despesas_ano(ano)
            # A coluna que identifica o deputado nesse arquivo costuma ser "ideCadastro"
            col_id = "ideCadastro" if "ideCadastro" in df_ano.columns else df_ano.columns[df_ano.columns.str.contains("dep", case=False)][0]
            df_ano_filtrado = df_ano[df_ano[col_id].isin(ids_amostra)].copy()
            df_ano_filtrado["anoConsulta"] = ano
            partes.append(df_ano_filtrado)
            print(f"    Ano {ano}: {len(df_ano_filtrado)} registros da amostra (de {len(df_ano)} no total).")
        except Exception as e:
            print(f"    Falha ao baixar/processar o ano {ano}: {e}")
    df_despesas = pd.concat(partes, ignore_index=True) if partes else pd.DataFrame()
    df_despesas["_ingestion_ts"] = pd.Timestamp.utcnow().isoformat()
    df_despesas.to_csv(f"{OUTPUT_DIR}/despesas.csv", index=False)
    print(f"    {len(df_despesas)} registros de despesas salvos no total.")

    print(f"4/4 - Baixando proposições de {len(amostra)} deputados (amostra)...")
    proposicoes_raw = []
    for i, row in amostra.iterrows():
        dep_id = row["id"]
        try:
            props = get_paginated("/proposicoes", params={"idDeputadoAutor": dep_id, "ano": 2025})
            for p in props:
                p["idDeputadoAutor"] = dep_id
            proposicoes_raw.extend(props)
        except Exception as e:
            print(f"    Falha deputado {dep_id}: {e}")
    df_proposicoes = pd.DataFrame(proposicoes_raw)
    df_proposicoes["_ingestion_ts"] = pd.Timestamp.utcnow().isoformat()
    df_proposicoes.to_csv(f"{OUTPUT_DIR}/proposicoes.csv", index=False)
    print(f"    {len(df_proposicoes)} proposições salvas.")

    print("\nPronto! Arquivos na pasta:", os.path.abspath(OUTPUT_DIR))


if __name__ == "__main__":
    main()
