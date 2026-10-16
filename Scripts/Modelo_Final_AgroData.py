import pandas as pd
from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score, mean_absolute_error

print("1. Cargando bases de datos y fusionando...")
df_base = pd.read_csv('../data/processed/Dataset_Machine_Learning_2025_final.csv')
df_espacial = pd.read_csv('../data/processed/Variables_Clima_Topografia_Extraidas_Final.csv')
df_enriquecido = pd.merge(df_base, df_espacial, on='ID_POLIGONO', how='inner')

columna_objetivo = 'RENDIMIENTO_T_HA'
df_entrenamiento = df_enriquecido[df_enriquecido['CONJUNTO'] == 'ENTRENAMIENTO'].copy()

# X e y contienen el 100% de los datos de entrenamiento
X = df_entrenamiento.drop(columns=['ID_POLIGONO', 'CONJUNTO', columna_objetivo], errors='ignore').select_dtypes(include=['number']).fillna(0)
y = df_entrenamiento[columna_objetivo]
ids_entrenamiento = df_entrenamiento['ID_POLIGONO']

# Dividir 80% de datos para entrenar y buscar configuración, 20% para el examen de error
X_train, X_test, y_train, y_test, ids_train, ids_test = train_test_split(
    X, y, ids_entrenamiento, test_size=0.2, random_state=42
)

print("2. Buscando la mejor configuración del modelo (Hyperparameter Tuning")
rf_base = RandomForestRegressor(random_state=42)

parametros_a_probar = {
    'n_estimators': [100, 200, 300, 500],            # Cantidad de árboles
    'max_depth': [None, 5, 10, 15, 20],              # Profundidad de cada árbol
    'min_samples_split': [2, 5, 10],                 # Mínimo de datos para ramificar
    'min_samples_leaf': [1, 2, 4],                   # Mínimo de datos en la hoja final
    'max_features': ['sqrt', 'log2', None]           # Cantidad de variables a mirar a la vez en el arbol
}

# Configuramos el buscador automático
buscador = RandomizedSearchCV(
    estimator=rf_base, 
    param_distributions=parametros_a_probar, 
    n_iter=30, 
    cv=3, 
    scoring='neg_mean_absolute_error', 
    random_state=42, 
    n_jobs=-1
)

# Entrenar y buscar el mejor modelo
buscador.fit(X_train, y_train)

print(f"\nMejor optimizacion encontrada:\n{buscador.best_params_}")

# Guardamos al modelo ganador 
mejor_modelo = buscador.best_estimator_

# Se muestra el R2 y MAE
predicciones_test = mejor_modelo.predict(X_test)
r2_test = r2_score(y_test, predicciones_test)
mae_test = mean_absolute_error(y_test, predicciones_test)

print("\n" + "="*50)
print("    RENDIMIENTO DEL MODELO OPTIMIZADO (EXAMEN 20%)")
print("="*50)
print(f" R² (Nivel de explicación): {r2_test:.4f}")
print(f" MAE (Error promedio):      {mae_test:.4f} Toneladas por Hectárea")
print("="*50 + "\n")

print("Re-entrenando al modelo campeón con el 100% de las 138 parcelas para máxima precisión...")
mejor_modelo.fit(X, y)

#Analisis de importancia de variables en % de cada una
importancias = mejor_modelo.feature_importances_
nombres_variables = X.columns

# Crear un DataFrame para ordenarlas de mayor a menor peso
df_importancias = pd.DataFrame({'Variable': nombres_variables, 'Importancia': importancias})
df_importancias = df_importancias.sort_values(by='Importancia', ascending=False)

print("\n" + "="*50)
print("   VARIABLES CON MAYOR PESO DENTRO DE LA ELECCION (LAS 5 MAS IMPORTANTS)")
print("="*50)
# Mostrar las 5 variables más importantes en formato de porcentaje
for indice, fila in df_importancias.head(5).iterrows():
    print(f" {fila['Variable']:<35} {fila['Importancia']*100:>5.2f}%")
print("="*50 + "\n")

print("\n4. Generando tabla de auditoría con las predicciones del modelo al 100%...")
# Preparamos variables de TODAS las parcelas (197)
X_total = df_enriquecido.drop(columns=['ID_POLIGONO', 'CONJUNTO', columna_objetivo], errors='ignore').select_dtypes(include=['number']).fillna(0)
X_total = X_total.reindex(columns=X_train.columns, fill_value=0)

predicciones_totales = mejor_modelo.predict(X_total)

# Crear la tabla de resultados final
df_maestro = pd.DataFrame({
    'ID_POLIGONO': df_enriquecido['ID_POLIGONO'],
    'CONJUNTO_ORIGINAL': df_enriquecido['CONJUNTO'],
    'Real_Ton_Ha': df_enriquecido[columna_objetivo],
    'Prediccion_Ton_Ha': predicciones_totales
})

# Etiquetar los grupos de predicciones
def etiquetar_grupo(fila):
    if fila['CONJUNTO_ORIGINAL'] == 'PREDICCION':
        return 'PREDICCION OFICIAL FIRA'
    elif fila['ID_POLIGONO'] in ids_test.values:
        return 'EXAMEN (Test Histórico)'
    else:
        return 'ENTRENAMIENTO (Train Histórico)'

df_maestro['GRUPO'] = df_maestro.apply(etiquetar_grupo, axis=1)




import shap
import numpy as np

print("\n--- NUEVO: Calculando variables de mayor peso POR PARCELA usando SHAP ---")
# 1. Crear el explicador SHAP con tu modelo ya re-entrenado
explicador = shap.TreeExplainer(mejor_modelo)

# 2. Calcular los valores SHAP para el 100% de las parcelas
valores_shap = explicador.shap_values(X_total)

lista_top_variables = []
nombres_columnas = X_total.columns

# 3. Iterar sobre cada parcela para extraer su Top 5
for i in range(len(X_total)):
    # Obtener el ID de la parcela actual
    id_parcela = df_maestro['ID_POLIGONO'].iloc[i]

    # Obtener el impacto absoluto de cada variable para esta parcela específica
    impacto_parcela = np.abs(valores_shap[i])

    # Obtener los índices de las 5 variables con mayor impacto (de mayor a menor)
    indices_top_5 = np.argsort(impacto_parcela)[-5:][::-1]

    # Obtener los nombres de esas variables
    top_5_nombres = nombres_columnas[indices_top_5].tolist()

    # Guardar en la lista (ID + las 5 variables)
    lista_top_variables.append([id_parcela] + top_5_nombres)

# 4. Convertir a DataFrame y guardar en CSV
df_top_parcelas = pd.DataFrame(
    lista_top_variables,
    columns=['ID_POLIGONO', 'Top_1', 'Top_2', 'Top_3', 'Top_4', 'Top_5']
)

ruta_top_csv = '../data/outputModel/Top_5_Variables_Por_Parcela.csv'
df_top_parcelas.to_csv(ruta_top_csv, index=False)

print(f"-> Top 5 variables por parcela guardado con éxito en: '{ruta_top_csv}'")
print(df_top_parcelas.head())





# Guardar la muestra/examen realizado 
nombre_excel = '../data/outputModel/Auditoria_Parcelas_Optimizada.csv'
df_maestro.drop(columns=['CONJUNTO_ORIGINAL']).to_csv(nombre_excel, index=False)
print(f"-> Auditoría guardada en '{nombre_excel}'")


print("\n5. Generando archivo de ENTREGA FINAL...")
# Cargar la plantilla exacta para usarla como molde y generar el archivo finañ
df_plantilla = pd.read_csv('../data/processed/Fake.csv')

# Extraer únicamente el ID y la predicción real de las 59 parcelas que debo predecir
df_predicciones = df_maestro[df_maestro['GRUPO'] == 'PREDICCION OFICIAL FIRA'][['ID_POLIGONO', 'Prediccion_Ton_Ha']]

# Unir con la plantilla usando 'how=left' para respetar su orden exacto y filas
df_final = pd.merge(df_plantilla.drop(columns=['RENDIMIENTO_T_HA']), 
                    df_predicciones, 
                    on='ID_POLIGONO', 
                    how='left')

# Renombrar y reordenar para copiar exactamente el formato de mi archivo Fake.csv (formato para el reto mostrado en teams)
df_final = df_final.rename(columns={'Prediccion_Ton_Ha': 'RENDIMIENTO_T_HA'})
df_final = df_final[['ID_POLIGONO', 'AREA_HA', 'RENDIMIENTO_T_HA', 'CONJUNTO']]

# Guardar
nombre_entrega = '../data/outputModel/agrodata_prediccion.csv'
df_final.to_csv(nombre_entrega, index=False)

print(f"Archivo final generado con exito con el nombre: '{nombre_entrega}'")
print("\n--- Vista previa ---")
print(df_final.head(10).to_string(index=False))