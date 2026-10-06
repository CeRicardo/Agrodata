import pandas as pd

print("Transformando la serie de tiempo en columnas mensuales para las 197 parcelas...")

# 1. Cargar la serie de tiempo oficial y el archivo maestro que contiene TODAS las 197 parcelas (Entrenamiento y Predicción)
df_ciclo = pd.read_csv('Linea_Tiempo_2025_Oficial.csv')

df_master = pd.read_csv('ID_area_rendimiento_70_30_Reto_AgroCebada.csv')

# 2. Asegurar el formato de fecha y extraer el número del mes
df_ciclo['fecha_captura'] = pd.to_datetime(df_ciclo['fecha_captura'])
df_ciclo['mes'] = df_ciclo['fecha_captura'].dt.month

# 3. Seleccionar EXACTAMENTE las 7 variables que solicitaste
columnas_interes = [
    'ndvi_promedio_y', # NDVI (Alta resolución Planet)
    'evi_promedio_y',  # EVI (Alta resolución Planet)
    'lai_promedio_y',  # LAI (Alta resolución Planet)
    'ndwi_promedio',   # NDWI (Sentinel)
    'msi_promedio',    # MSI (Sentinel)
    'emsi_promedio',   # EMSI (Sentinel)
    'vi6t_promedio'    # VI6T (Landsat)
]

# 4. Calcular el promedio de cada índice por Parcela y por Mes
df_mensual = df_ciclo.groupby(['ID_POLIGONO', 'mes'])[columnas_interes].mean().reset_index()

# 5. Aplanar (Pivotar): Convertir los meses en columnas
df_aplanado = df_mensual.pivot(index='ID_POLIGONO', columns='mes', values=columnas_interes)

# 6. Renombrar las columnas para que sean legibles (ej. ndvi_promedio_y_mes_4)
df_aplanado.columns = [f'{indice}_mes_{mes}' for indice, mes in df_aplanado.columns]
df_aplanado = df_aplanado.reset_index()

# 7. Rellenar con 0 los huecos donde no hubo fotos satelitales en un mes específico
df_aplanado = df_aplanado.fillna(0)

# 8. Cruzar la historia aplanada con el archivo maestro que tiene las 197 parcelas usando 'how=left'
dataset_final = pd.merge(df_master, df_aplanado, on='ID_POLIGONO', how='left')

# 9. Guardar la matriz final completa con las 197 parcelas
dataset_final.to_csv('Dataset_Machine_Learning_2025_final.csv', index=False)

print("¡Matriz creada con éxito con tus 7 variables y las 197 parcelas!")
print(f"Dimensiones finales: {dataset_final.shape[0]} filas y {dataset_final.shape[1]} columnas.")
print("Archivo guardado: 'Dataset_Machine_Learning_2025.csv'")