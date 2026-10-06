import pandas as pd
from sklearn.ensemble import RandomForestRegressor

print("1. Cargando todas las fuentes de datos...")
# A. El archivo maestro con las 197 parcelas (Entrenamiento y Predicción)
df_main = pd.read_csv('ID_area_rendimiento_70_30_Reto_AgroCebada.csv')

# B. El archivo con el clima y la topografía extraída
df_espacial = pd.read_csv('Variables_Clima_Topografia_Extraidas_Final.csv')

# C. Tu archivo con los índices de vegetación (Dataset_Machine_Learning_2025.csv)
df_indices = pd.read_csv('Dataset_Machine_Learning_2025.csv')

print("2. Fusionando con 'how=left' para conservar todas las 197 parcelas...")
# Unimos el maestro con el clima/topografía conservando todas las filas de df_main
df_enriquecido = pd.merge(df_main, df_espacial, on='ID_POLIGONO', how='left', suffixes=('', '_esp'))

# Unimos también los índices de vegetación conservando todas las filas
df_enriquecido = pd.merge(df_enriquecido, df_indices, on='ID_POLIGONO', how='left', suffixes=('', '_orig'))

columna_objetivo = 'RENDIMIENTO_T_HA'

# 3. Separar en Entrenamiento (138 parcelas) y Predicción (59 parcelas) usando la columna CONJUNTO original
df_train = df_enriquecido[df_enriquecido['CONJUNTO'] == 'ENTRENAMIENTO'].copy()
df_pred = df_enriquecido[df_enriquecido['CONJUNTO'] == 'PREDICCION'].copy()

# Definir variables predictoras (X) eliminando metadatos y duplicados
cols_a_excluir = ['ID_POLIGONO', 'CONJUNTO', 'Unnamed: 4', 'Unnamed: 4_orig', columna_objetivo, 'RENDIMIENTO_T_HA_orig', 'RENDIMIENTO_T_HA_esp', 'AREA_HA_orig', 'AREA_HA_esp']
X_train = df_train.drop(columns=cols_a_excluir, errors='ignore')
y_train = df_train[columna_objetivo]

X_pred = df_pred.drop(columns=cols_a_excluir, errors='ignore')

# >>> FILTRO DE SEGURIDAD: Quedarnos ÚNICAMENTE con columnas numéricas <<<
X_train = X_train.select_dtypes(include=['number']).fillna(0)

# Asegurar que X_pred tenga exactamente las mismas columnas que X_train en el mismo orden
X_pred = X_pred.reindex(columns=X_train.columns, fill_value=0).select_dtypes(include=['number']).fillna(0)

print(f"-> Total de variables predictoras utilizadas: {X_train.shape[1]}")
print(f"-> Parcelas para entrenar el modelo: {len(X_train)}")
print(f"-> Parcelas a predecir para FIRA: {len(X_pred)}")

print("\n4. Entrenando el modelo Random Forest definitivo...")
modelo = RandomForestRegressor(
    n_estimators=200, 
    max_depth=10, 
    min_samples_leaf=1, 
    min_samples_split=2, 
    random_state=42
)
modelo.fit(X_train, y_train)

print("5. Generando predicciones oficiales para las 59 parcelas...")
predicciones = modelo.predict(X_pred)

# Asignar las predicciones al DataFrame de predicción
df_pred[columna_objetivo] = predicciones

# 6. Armar el archivo final de entrega exactamente con el formato requerido
df_entrega = df_pred[['ID_POLIGONO', 'AREA_HA', 'RENDIMIENTO_T_HA', 'CONJUNTO']].copy()

nombre_archivo = 'Agro_Data_prediccion.csv'
df_entrega.to_csv(nombre_archivo, index=False)

print(f"\n¡Éxito total! Archivo generado y guardado como: '{nombre_archivo}'")
print("\n--- VISTA PREVIA DE TUS PREDICCIONES ---")
print(df_entrega.head(10).to_string(index=False))