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

---

### A Jornada de Engenharia de Features

Depois que os dados foram devidamente sanitizados e transformados, nossa próxima etapa é adicionar engrenagens a essa máquina de dados. O script `vra_features.py` entra em cena para transformar os dados brutos já limpos em uma versão muito mais útil para análise de atrasos nos voos.

#### A Jornada de Engenharia de Features

O objetivo de *engenharia de features* é pegar os dados já tratados e extrair informações adicionais, que podem revelar padrões ocultos. Aqui, geramos novas colunas a partir de dados temporais, como a diferença de horários de partida e chegada, que podem nos ajudar a entender os atrasos com maior profundidade.

#### O Que Está Sendo Feito?

**Criação de Novas Colunas:** Com o script `vra_features.py`, geramos novas variáveis que são cruciais para análise:

- **Atrasos em minutos:** As diferenças de horário entre a partida prevista e a real, assim como a chegada prevista e a real, são calculadas e registradas em minutos. Esse valor é um dos principais indicadores de performance dos voos.

- **Status Normalizado:** As colunas de status de voo são convertidas para um formato mais útil. Elas são normalizadas para identificar facilmente se o voo foi cancelado ou realizado, ou se há algum tipo de informação ausente.

- **Atrasos Significativos:** Criamos uma coluna de marcação se o voo teve atraso superior a 30 minutos. Isso nos permite separar voos com atrasos significativos daqueles que ocorreram pontualmente, facilitando o agrupamento e análise.

- **Colunas Temporais:** Adicionamos detalhes como ano, mês, dia da semana, hora e período do dia (manhã, tarde, noite). Isso ajuda a correlacionar os atrasos com fatores temporais, como o comportamento do tráfego aéreo ao longo da semana ou do dia.

- **Identificador de Rota:** Criamos uma coluna que identifica a rota do voo usando os códigos ICAO dos aeroportos de origem e destino. Isso é essencial para responder a perguntas como "Quais rotas têm mais atrasos?"

#### Como Esses Dados São Úteis?

Essas novas *features* criadas são cruciais para que possamos responder perguntas mais específicas sobre os atrasos dos voos no Brasil. A seguir, exploramos algumas questões que podem ser respondidas a partir das novas colunas e dados:

##### Quais aeroportos são mais afetados por atrasos?

Com a coluna de atraso (`atraso`), podemos identificar aeroportos com altos níveis de atrasos acumulados. Utilizando a coluna `origin_icao`, conseguimos determinar quais aeroportos de origem têm mais problemas de atraso.

##### Como os atrasos variam ao longo do ano, mês ou dia da semana?

As colunas `year`, `month`, `weekday`, e `hour` nos fornecem uma visão detalhada sobre o comportamento dos atrasos ao longo do tempo. Podemos analisar os atrasos mensais ou identificar padrões como quais dias da semana têm mais atrasos.

##### Quais companhias aéreas apresentam mais atrasos?

Com a coluna `airline_icao`, podemos identificar rapidamente quais companhias aéreas têm mais registros de voos atrasados. Ao adicionar a coluna atraso, conseguimos quantificar e comparar o nível de atraso das companhias.

##### Quais períodos do dia têm mais atrasos?

A coluna `periodo_dia` nos ajuda a segmentar os atrasos de acordo com o período do dia (manhã, tarde, noite, madrugada). Com essa informação, podemos descobrir se há mais problemas de atraso pela manhã, quando o tráfego de voos é maior, ou à noite, quando a logística aérea pode ser mais desafiadora.

##### Qual a taxa de atraso por voo em cada aeroporto e cada companhia aérea?

A taxa de atraso pode ser calculada com base nas colunas `total_voos` e `voos_atrasados`. Isso nos ajuda a ver não só a quantidade de voos atrasados, mas também a proporção de voos afetados por atrasos em cada aeroporto ou companhia.

#### O Que Você Conquista Ao Final

Com os dados sanitizados e as features criadas, temos agora um dataset pronto para análise, onde cada voo está documentado de forma rica, com detalhes sobre seus atrasos e comportamento temporal.

Além disso, agora podemos analisar tendências de atrasos ao longo do tempo e identificar os principais causadores desses atrasos, seja por companhia aérea, aeroporto de origem, período do dia, ou dia da semana.

##### Exemplo de Como Rodar o Script de Engenharia de Features

Após rodar a sanitização com `sanitize_year.py`, rodamos a parte da engenharia de features:

```python 
vra_features.py --clean_csv "./sanitized_data/2002/vra_clean_base.csv" --out "./aggregated_data/2002"
```

O script gera o arquivo `vra_clean_with_features.csv` com todos os dados enriquecidos.