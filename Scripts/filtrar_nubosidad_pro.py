import pandas as pd

# 1. Cargar el archivo de datos satelitales PRO
df_pro = pd.read_csv('Conjunto_datos_PRO_AgroCebada.csv')

# 2. Filtrar los datos
# Nos quedamos estrictamente con las filas donde la nubosidad es menor a 100
df_pro_limpio = df_pro[df_pro['porcentaje_nubosidad'] < 100]

# 3. Exportar el resultado a un nuevo archivo CSV para no borrar el original
df_pro_limpio.to_csv('PRO_sin_nubes_totales.csv', index=False)

print("Proceso completado. Se ha creado el archivo 'PRO_sin_nubes_totales.csv'")