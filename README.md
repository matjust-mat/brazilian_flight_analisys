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

---

### Análise dos voos feitos no Brasil entre 2000 e 2002.

A Jornada de Sanitização dos Arquivos VRA

O script `sanitize_year.py` é nossa primeira linha de defesa ao lidar com os arquivos brutos dos voos brasileiros, com o objetivo de gerar dados limpos e úteis para análise.

#### O Processo de Limpeza

Ao longo dessa jornada de sanitização, cada arquivo de voo, oriundo de diversos meses, passa por um processo de purificação. O `sanitize_year.py` busca os 12 campos fundamentais, como informações de aeroporto e companhia aérea, garantindo que cada coluna seja transformada e padronizada corretamente. A codificação *(mojibake)* que afeta os cabeçalhos de algumas colunas é corrigida, o que ajuda a garantir a uniformidade do dataset.

#### O Que Está Sendo Feito?

**Leitura dos Arquivos Brutos:** Usamos pandas para abrir os arquivos CSV mensais. A função glob é usada para encontrar todos os arquivos correspondentes ao padrão informado.

**Filtragem e Normalização:** Os campos da ANAC, como "empresa aérea" e "código do voo", são normalizados. Corrigimos a codificação incorreta *(mojibake)* e garantimos que todos os valores nulos ou inválidos sejam tratados, deixando o conjunto de dados mais robusto para análises posteriores.

**Seleção de Colunas Relevantes:** Apenas as colunas essenciais são mantidas no arquivo final, eliminando ruídos que poderiam prejudicar as análises.

**Gravação do Arquivo Final:** Após todo o processamento de todos os 12 meses, um único arquivo anual é salvo em formato CSV (com separador `;`), já pronto para ser processado ou importado para qualquer ferramenta de análise de dados.

##### Como Rodar o Script?

Depois de garantir que você tem o arquivo correto, basta rodar o seguinte comando:

```python 
sanitize_year.py \
  --inputs "./folder/file_pattern*.csv" \
  --out "./folder/folder"
```

##### Passo a Passo para Entender a Jornada

**Entrada Bruta:** O arquivo de entrada contém dados de múltiplos meses com ruídos e inconsistências.

**Limpeza e Seleção:** O script remove as colunas inúteis, resolve problemas de codificação e mantém apenas as colunas relevantes para análise de atrasos nos voos.

**Saída Final:** O resultado é um arquivo `vra_clean_base.csv`, onde todos os dados estão no formato correto e sem informações desnecessárias.