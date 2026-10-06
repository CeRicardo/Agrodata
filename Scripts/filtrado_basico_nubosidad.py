import pandas as pd

# 1. Cargar el archivo BASICO
print("Cargando datos masivos...")
df_basico = pd.read_csv('Conjunto_datos_BASICO_AgroCebada2026.csv')

# 2. Filtrar las lecturas totalmente nubladas (sin datos útiles)
df_limpio = df_basico[df_basico['porcentaje_nubosidad'] < 100].copy()

# 3. Seleccionar únicamente el ID de la parcela, LA FECHA y los índices subrayados
columnas_subrayadas = [
    'ID_POLIGONO',
    'fecha_captura',  # Fecha_cap
    'ndvi_promedio',  # NDVI
    'evi_promedio',   # EVI
    'lai_promedio',   # LAI
    'ndwi_promedio',  # NDWI
    'msi_promedio',   # MSI
    'emsi_promedio',  # EMSI
    'vi6t_promedio'   # VI6T
]
df_reducido = df_limpio[columnas_subrayadas]

# 4. Guardar el resultado en un nuevo archivo conservando el historial de tiempo
df_reducido.to_csv('BASICO_indices_historial.csv', index=False)

print("¡Proceso completado! Revisa tu carpeta para ver el archivo 'BASICO_indices_historial.csv'")