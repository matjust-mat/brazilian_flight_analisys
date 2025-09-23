import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Configurar o estilo dos gráficos
sns.set(style="whitegrid")
plt.figure(figsize=(10, 6))

# Carregar os dados
file_paths = [
    "featured/2000/vra_clean_with_features.csv",
    "featured/2001/vra_clean_with_features.csv",
    "featured/2002/vra_clean_with_features.csv"
]
df = pd.concat([pd.read_csv(fp, low_memory=False) for fp in file_paths], ignore_index=True)

# Convertendo as colunas de data e hora
df['dep_scheduled'] = pd.to_datetime(df['dep_scheduled'], errors='coerce')
df['dep_actual'] = pd.to_datetime(df['dep_actual'], errors='coerce')
df['arr_scheduled'] = pd.to_datetime(df['arr_scheduled'], errors='coerce')
df['arr_actual'] = pd.to_datetime(df['arr_actual'], errors='coerce')

# Calculando os atrasos em minutos
df['dep_delay_min'] = (df['dep_actual'] - df['dep_scheduled']).dt.total_seconds() / 60
df['arr_delay_min'] = (df['arr_actual'] - df['arr_scheduled']).dt.total_seconds() / 60

# Filtrando os voos com atraso na decolagem (dep_delay_min > 0)
df_delays = df[df['dep_delay_min'] > 0]

# 1. Aeroporto com mais atrasos no geral
airport_delays = df_delays.groupby('origin_icao').size().reset_index(name='num_delays')
airport_most_delays = airport_delays.sort_values(by='num_delays', ascending=False).head(1)
print("Aeroporto com mais atrasos no geral:")
print(airport_most_delays)

# 2. Aeroporto que aumentou ou diminuiu o número de atrasos (por ano)
airport_year_delays = df_delays.groupby(['origin_icao', 'year']).size().reset_index(name='num_delays')
airport_year_delays['delay_diff'] = airport_year_delays.groupby('origin_icao')['num_delays'].diff()

# Filtrando aeroportos que aumentaram ou diminuíram os atrasos
increased_delays_airports = airport_year_delays[airport_year_delays['delay_diff'] > 0]
decreased_delays_airports = airport_year_delays[airport_year_delays['delay_diff'] < 0]

print("\nAeroporto que aumentou os atrasos:")
print(increased_delays_airports)

print("\nAeroporto que diminuiu os atrasos:")
print(decreased_delays_airports)

# 3. Atrasos aumentaram ou diminuíram no período (por ano)
yearly_delays = df_delays.groupby('year').size().reset_index(name='num_delays')
yearly_delays['delay_diff'] = yearly_delays['num_delays'].diff()

# Filtrando os anos com aumento ou diminuição de atrasos
increased_delays = yearly_delays[yearly_delays['delay_diff'] > 0]
decreased_delays = yearly_delays[yearly_delays['delay_diff'] < 0]

print("\nAtrasos aumentaram ou diminuíram no período (por ano):")
print(f"Aumentaram: {increased_delays}")
print(f"Diminuição: {decreased_delays}")

# 4. Dias da semana com mais atrasos (a cada ano)
weekday_delays = df_delays.groupby(['year', 'weekday']).size().reset_index(name='num_delays')
weekday_delays_max = weekday_delays.loc[weekday_delays.groupby('year')['num_delays'].idxmax()]

print("\nDias da semana com mais atrasos (a cada ano):")
print(weekday_delays_max)

# 5. Período do dia com mais atrasos (a cada ano)
periodo_dia_delays = df_delays.groupby(['year', 'periodo_dia']).size().reset_index(name='num_delays')
periodo_dia_delays_max = periodo_dia_delays.loc[periodo_dia_delays.groupby('year')['num_delays'].idxmax()]

print("\nPeríodo do dia com mais atrasos (a cada ano):")
print(periodo_dia_delays_max)

# 6. Companhia que mais atrasa (a cada ano)
airline_delays = df_delays.groupby(['year', 'airline_icao']).size().reset_index(name='num_delays')
airline_max_delays = airline_delays.loc[airline_delays.groupby('year')['num_delays'].idxmax()]

print("\nCompanhia que mais atrasa (a cada ano):")
print(airline_max_delays)
