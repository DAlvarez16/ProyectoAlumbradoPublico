import pandas as pd
import unicodedata

def normalizar_texto(texto):
    """Convierte a mayúsculas, elimina espacios extra y quita tildes/acentos."""
    if pd.isna(texto):
        return texto
    texto = str(texto).upper().strip()
    texto = ''.join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')
    return texto

def procesar_datos_energia(ruta_energia, ruta_agricola):
    # ==========================================
    # 1. CONSTRUIR DICCIONARIO DE CÓDIGOS DANE
    # ==========================================
    df_agricola = pd.read_csv(ruta_agricola)
    diccionario_municipios = {}
    
    for _, fila in df_agricola.iterrows():
        nombre_normalizado = normalizar_texto(fila['Municipio'])
        if nombre_normalizado not in diccionario_municipios and pd.notna(fila['CodMunicipio']):
            # Limpiar el código quitando el punto decimal (ej: 13.006 -> '13006')
            codigo_limpio = str(fila['CodMunicipio']).replace('.', '')
            diccionario_municipios[nombre_normalizado] = codigo_limpio

    # ==========================================
    # 2. CARGA Y LIMPIEZA INICIAL DE ENERGÍA
    # ==========================================
    df_energia = pd.read_csv(ruta_energia, encoding='latin1', skiprows=2)
    
    # Eliminar fila de subtotal general
    df_energia = df_energia[df_energia['Mes'] != 'Total'].copy()
    
    # Limpiar nombres de columnas (snake_case)
    df_energia.columns = (
        df_energia.columns
        .str.strip()
        .str.lower()
        .str.replace(' ', '_')
        .str.replace(r'[\*\(\)\$]', '', regex=True)
        .str.replace('__', '_')
    )

    # ==========================================
    # 3. LIMPIEZA DE DATOS NUMÉRICOS
    # ==========================================
    # Limpiar y castear columnas de dinero
    columnas_dinero = ['facturación_por_consumo_', 'facturación_total_', 'total']
    for col in columnas_dinero:
        df_energia[col] = (df_energia[col]
                           .astype(str)
                           .str.replace(r'[ \(\)\$]', '', regex=True)
                           .str.replace(',', '')
                           .astype(float))

    # Limpiar y castear columna de consumo
    df_energia['consumo_total_kwh'] = (df_energia['consumo_total_kwh']
                                       .astype(str)
                                       .str.replace('kwh', '', case=False)
                                       .str.replace(',', '')
                                       .astype(float))

    # ==========================================
    # 4. EXTRACCIÓN Y TRANSFORMACIÓN DE TEXTO/FECHA
    # ==========================================
    # Separar Empresa en ID y Nombre
    df_energia[['id_empresa', 'nombre_empresa']] = df_energia['empresa'].str.split(' - ', n=1, expand=True)
    df_energia = df_energia.drop(columns=['empresa'])

    # Formatear columna de meses a tipo datetime nativo
    meses_es_en = {
        'ene': 'Jan', 'feb': 'Feb', 'mar': 'Mar', 'abr': 'Apr', 
        'may': 'May', 'jun': 'Jun', 'jul': 'Jul', 'ago': 'Aug', 
        'sep': 'Sep', 'oct': 'Oct', 'nov': 'Nov', 'dic': 'Dec'
    }
    df_energia['mes'] = df_energia['mes'].replace(meses_es_en, regex=True).str.replace(' / ', '-', regex=False)
    df_energia['mes'] = pd.to_datetime(df_energia['mes'], format='%b-%Y')

    # ==========================================
    # 5. INTEGRACIÓN DEL COMPONENTE DE ALMACENAMIENTO
    # ==========================================
    # Normalizar los nombres de los municipios para asegurar el cruce perfecto
    df_energia['municipio_norm'] = df_energia['municipio'].apply(normalizar_texto)
    
    # Mapear los códigos oficiales desde el diccionario
    df_energia['codigo_oficial'] = df_energia['municipio_norm'].map(diccionario_municipios)
    
    # Agregar el departamento requerido por el documento
    df_energia['departamento'] = 'Bolívar'
    
    # Eliminar la columna temporal
    df_energia = df_energia.drop(columns=['municipio_norm'])

    # Reordenar las columnas para dejar el dataset listo para insertar en SQL
    columnas_finales = [
        'codigo_oficial', 'municipio', 'departamento', 'mes', 
        'tipo_de_usuario', 'estrato', 'numero_de_suscriptores_', 
        'consumo_total_kwh', 'facturación_por_consumo_', 
        'facturación_total_', 'total', 'id_empresa', 'nombre_empresa'
    ]
    df_energia = df_energia[columnas_finales]

    return df_energia
