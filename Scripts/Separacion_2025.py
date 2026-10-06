import pandas as pd

print("Aplicando filtro oficial del ciclo agrícola (Abril - Octubre 2025)...")
df_tiempo = pd.read_csv('Linea_Tiempo_Maestra.csv')

# Asegurar formato de fecha
df_tiempo['fecha_captura'] = pd.to_datetime(df_tiempo['fecha_captura'])

# Definir el marco de tiempo oficial establecido por FIRA
fecha_inicio = pd.to_datetime('2025-04-01')
fecha_fin = pd.to_datetime('2025-10-31')

# Recortar la base de datos
df_ciclo_oficial = df_tiempo[(df_tiempo['fecha_captura'] >= fecha_inicio) & 
                             (df_tiempo['fecha_captura'] <= fecha_fin)].copy()

# Guardar la nueva tabla limpia
df_ciclo_oficial.to_csv('Linea_Tiempo_2025_Oficial.csv', index=False)

print(f"¡Filtro exitoso! Tu archivo pasó de {len(df_tiempo)} filas a {len(df_ciclo_oficial)} filas.")
print("Este archivo 'Linea_Tiempo_2025_Oficial.csv' es el que usaremos para entrenar.")