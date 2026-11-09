import pandas as pd

# 1. Cargar archivo saltando metadatos iniciales
df = pd.read_csv('O3-export.csv', encoding='latin1', skiprows=2)

# 2. Eliminar la fila de subtotal general
df = df[df['Mes'] != 'Total'].copy()

# 3. Limpiar nombres de columnas (snake_case)
df.columns = (
    df.columns
    .str.strip()
    .str.lower()
    .str.replace(' ', '_')
    .str.replace(r'[\*\(\)\$]', '', regex=True)
    .str.replace('__', '_')
)

# 4. Limpiar consumo y facturación (casteo a float)
columnas_dinero = ['facturación_por_consumo_', 'facturación_total_', 'total']
for col in columnas_dinero:
    df[col] = (df[col]
               .astype(str)
               .str.replace(r'[ \(\)\$]', '', regex=True) # Remueve " ($)"
               .str.replace(',', '')                    # Remueve separador de miles
               .astype(float))

df['consumo_total_kwh'] = (df['consumo_total_kwh']
                           .astype(str)
                           .str.replace('kwh', '', case=False)
                           .str.replace(',', '')
                           .astype(float))

# 5. Separar ID de la Empresa y Nombre de la Empresa
df[['id_empresa', 'nombre_empresa']] = df['empresa'].str.split(' - ', n=1, expand=True)
df = df.drop(columns=['empresa'])

# 6. Formatear la columna Mes a datetime
meses_es_en = {'ene': 'Jan', 'feb': 'Feb', 'mar': 'Mar', 'abr': 'Apr', 'may': 'May', 'jun': 'Jun', 
               'jul': 'Jul', 'ago': 'Aug', 'sep': 'Sep', 'oct': 'Oct', 'nov': 'Nov', 'dic': 'Dec'}
df['mes'] = df['mes'].replace(meses_es_en, regex=True).str.replace(' / ', '-', regex=False)
df['mes'] = pd.to_datetime(df['mes'], format='%b-%Y')

print(df.head())