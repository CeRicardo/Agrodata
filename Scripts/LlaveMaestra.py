import pandas as pd

# 1. Cargar ambos archivos limpios de ambos satélites (BASICO y PRO)
print("Cargando historiales...")
df_basico = pd.read_csv('BASICO_indices_historial.csv')
df_pro = pd.read_csv('PRO_sin_nubes_totales.csv')


# formato que indica como viene las fechas
df_basico['fecha_captura'] = pd.to_datetime(df_basico['fecha_captura'], format='%d/%m/%Y')
df_pro['fecha_captura'] = pd.to_datetime(df_pro['fecha_captura'], format='%d/%m/%Y')

# 3. Unir ambas tablas
# La clave para unirlos es que coincida la Parcela y el Dia exacto.
df_fusion = pd.merge(df_basico, df_pro, on=['ID_POLIGONO', 'fecha_captura'], how='outer')

# 4. Ordenar el resultado para que quede como una historia real:
df_fusion = df_fusion.sort_values(by=['ID_POLIGONO', 'fecha_captura']).reset_index(drop=True)

# 5. Guardar la línea de tiempo maestra
df_fusion.to_csv('Linea_Tiempo_Maestra.csv', index=False)

print("¡Fusión completada! Revisa el archivo 'Linea_Tiempo_Maestra.csv'")