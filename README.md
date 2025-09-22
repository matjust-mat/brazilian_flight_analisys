# brazilian_flight_analisys
Análise dos voos feitos no Brasil entre 2000 e 2002.

### Jornada de Sanitização dos Códigos de Aeroporto (BR)

O script `sanitize_additional_data.py` entra no arquivo bruto, encontra os registros do país certo, limpa o que está “ruído” e entrega uma tabela enxuta, pronta para análise.

Abrimos o CSV original com pandas. Cuidamos para reconhecer valores “nulos” que vêm como texto ("null"), além dos ausentes padrão.

A coluna `iso_country` é normalizada para maiúsculas. Ela decide quem fica na história: só registros com valor igual à `BR`.

Algumas colunas aparecem quase vazias, com espaços, null, nan ou none. Medimos a “utilidade” de cada coluna: se menos de 5% dos valores forem válidos, a coluna sai de cena.

Gravamos o resultado em um novo CSV, separando por `;` para facilitar a abertura em planilhas locais.

#### Como rodar
```python 
sanitize_additional_data.py \
  --input "./data/flat-ui__data-Sun Sep 21 2025.csv" \
  --outdir "./sanitized_data" \
  --outfile "sanitized_airpot_codes.csv"
```

#### Erros comuns (e como sair deles)

FileNotFoundError: o caminho de --input está errado ou com espaços sem aspas.

“Faltou iso_country”: o CSV não segue o esquema esperado. Verifique as colunas.

Separador do arquivo de saída: se preferir vírgula, troque sep=';' por sep=','.

#### Epílogo

No final, você tem um recorte confiável do Brasil, sem colunas que só atrapalham. Pronto para responder perguntas como: onde estão os aeroportos? quais possuem códigos IATA? que campos valem a pena explorar?...