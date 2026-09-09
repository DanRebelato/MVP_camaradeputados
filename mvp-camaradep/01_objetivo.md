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

**API de Dados Abertos da Câmara dos Deputados** — https://dadosabertos.camara.leg.br/api/v2

- `/deputados` — lista de deputados em exercício (id, nome, partido, UF, e-mail, foto)
- `/deputados/{id}/despesas` — despesas de cota parlamentar (CEAP) por deputado: ano, mês, tipo de despesa, valor, fornecedor
- `/proposicoes` — proposições legislativas (filtráveis por autor)
- `/partidos` — lista de partidos

## Licença de uso

Dados publicados pela Câmara dos Deputados sob a **Licença Aberta / Lei de Acesso à Informação (Lei nº 12.527/2011)**, de uso livre para qualquer finalidade, inclusive comercial, com atribuição da fonte. Documentação oficial: https://dadosabertos.camara.leg.br/

## Escopo e recorte

- Deputados em exercício na legislatura atual (56ª legislatura).
- Despesas do ano corrente e do ano anterior (para ter volume suficiente sem sobrecarregar a coleta).
- Proposições de autoria dos deputados no mesmo período.
