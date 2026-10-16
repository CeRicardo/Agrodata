import pandas as pd

# 1. Cargar el archivo
df = pd.read_csv('ID_area_rendimiento_70_30_Reto_AgroCebada.csv')

# 2. Filtrar la columna CONJUNTO
df_entrenamiento = df[df['CONJUNTO'] == 'ENTRENAMIENTO']

# 3. Exportar el resultado a un nuevo archivo CSV
df_entrenamiento.to_csv('solo_entrenamiento_filtrado.csv', index=False)

print("Proceso completado. Revisa tu carpeta para ver el archivo 'solo_entrenamiento_filtrado.csv'")