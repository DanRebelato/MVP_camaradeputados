# Contexto de Negócio e Perguntas (Etapa 2 e 4.1)

## Problema

Entender os fatores que influenciam o **comportamento legislativo dos deputados federais brasileiros** — em termos de gasto de cota parlamentar (CEAP), produtividade legislativa (proposições apresentadas) e perfil por partido/UF — usando a API de Dados Abertos da Câmara dos Deputados.

## Perguntas de negócio

1. Quais partidos e UFs concentram o maior gasto total de cota parlamentar (CEAP) por deputado?
2. Quais categorias de despesa são mais representativas no gasto dos deputados e como isso varia entre partidos?
3. Existe relação entre o volume de proposições apresentadas por um deputado e seu gasto com cota parlamentar?
4. Como se distribui a produção legislativa (número de proposições) entre partidos e UFs?
5. Existe diferença no gasto médio mensal de cota parlamentar entre deputados de diferentes regiões do país (agrupando UFs por região)?

## Fonte dos dados

**Dados Abertos da Câmara dos Deputados** — https://dadosabertos.camara.leg.br

- API REST (`/deputados`, `/partidos`, `/proposicoes`) para deputados, partidos e proposições.
- Arquivo consolidado por ano (`camara.leg.br/cotas/Ano-{ano}.csv.zip`) para despesas de cota parlamentar (CEAP) — canal oficial da Câmara para esse conjunto de dados.

## Licença de uso

Lei de Acesso à Informação (Lei nº 12.527/2011), uso livre com atribuição da fonte. https://dadosabertos.camara.leg.br/

## Escopo e recorte

- Deputados em exercício na legislatura atual (56ª).
- Amostra de 40 deputados para despesas (2025–2026) e proposições (2025) — dataset modesto, conforme previsto no enunciado.
