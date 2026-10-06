import pandas as pd
import joblib  # <-- Librería clave para cargar el modelo pre-entrenado

print("1. Cargando bases de datos y fusionando...")
# Archivos procesados con las características de las 197 parcelas
df_base = pd.read_csv('../data/processed/Dataset_Machine_Learning_2025_final.csv')
df_espacial = pd.read_csv('../data/processed/Variables_Clima_Topografia_Extraidas_Final.csv')
df_enriquecido = pd.merge(df_base, df_espacial, on='ID_POLIGONO', how='inner')

columna_objetivo = 'RENDIMIENTO_T_HA'

# 2. Cargar el modelo optimizado de tu compañero
print("2. Cargando el modelo optimizado desde el archivo .pkl...")
ruta_modelo = '../model/Archivo.pkl'  # <-- Cambia esto por la ruta real del archivo de tu compañero
mejor_modelo = joblib.load(ruta_modelo)

print("\n3. Generando tabla de auditoría con las predicciones del modelo...")
# Preparamos variables numéricas de TODAS las parcelas (197)
columnas_excluir = ['ID_POLIGONO', 'CONJUNTO', columna_objetivo]
X_total = df_enriquecido.drop(columns=columnas_excluir, errors='ignore').select_dtypes(include=['number']).fillna(0)

# Importante: Asegúrate de que las columnas de X_total sean exactamente las mismas
# que tu compañero usó cuando entrenó el modelo. Si las columnas varían, el .pkl fallará.

# El modelo cargado predice todas las parcelas (incluyendo las 59 parcelas ocultas de predicción)
predicciones_totales = mejor_modelo.predict(X_total)

# Crear la tabla maestra de auditoría
df_maestro = pd.DataFrame({
    'ID_POLIGONO': df_enriquecido['ID_POLIGONO'],
    'CONJUNTO_ORIGINAL': df_enriquecido['CONJUNTO'],
    'Real_Ton_Ha': df_enriquecido[columna_objetivo],
    'Prediccion_Ton_Ha': predicciones_totales
})

# Etiquetar los grupos (Se simplificó al no tener y_test)
def etiquetar_grupo(fila):
    if fila['CONJUNTO_ORIGINAL'] == 'PREDICCION':
        return 'PREDICCION OFICIAL FIRA'
    else:
        return 'ENTRENAMIENTO (Histórico)'

df_maestro['GRUPO'] = df_maestro.apply(etiquetar_grupo, axis=1)

# Guardar auditoría
nombre_excel = '../data/outputModel/Auditoria_Parcelas_Optimizada.csv'
df_maestro.drop(columns=['CONJUNTO_ORIGINAL']).to_csv(nombre_excel, index=False)
print(f"-> Auditoría guardada en '{nombre_excel}'")


print("\n4. Generando archivo de ENTREGA FINAL...")
# Cargar la plantilla exacta para usarla como molde
df_plantilla = pd.read_csv('../data/processed/Fake.csv')

# Extraer únicamente el ID y la predicción de las 59 parcelas correspondientes a PREDICCION
df_predicciones = df_maestro[df_maestro['GRUPO'] == 'PREDICCION OFICIAL FIRA'][['ID_POLIGONO', 'Prediccion_Ton_Ha']]

# Unir con la plantilla usando 'how=left' para respetar su orden exacto y filas
df_final = pd.merge(df_plantilla.drop(columns=['RENDIMIENTO_T_HA']),
                    df_predicciones,
                    on='ID_POLIGONO',
                    how='left')

# Renombrar y reordenar para copiar exactamente el formato exigido para el CSV
df_final = df_final.rename(columns={'Prediccion_Ton_Ha': 'RENDIMIENTO_T_HA'})
df_final = df_final[['ID_POLIGONO', 'AREA_HA', 'RENDIMIENTO_T_HA', 'CONJUNTO']]

# Guardar el documento oficial
nombre_entrega = '../data/outputModel/agrodata_prediccion.csv'
df_final.to_csv(nombre_entrega, index=False)

print(f"¡Éxito total! Archivo de entrega guardado como: '{nombre_entrega}'")
print("\n--- VISTA PREVIA DE TU ENTREGA OFICIAL PARA FIRA ---")
print(df_final.head(10).to_string(index=False))