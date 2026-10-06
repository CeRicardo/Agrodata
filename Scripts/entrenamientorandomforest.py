import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score

print("Iniciando el entrenamiento del Bosque Aleatorio...")

df = pd.read_csv('Dataset_Machine_Learning_2025.csv')

# Aislar las toneladas de rendimiento
columna_objetivo = 'RENDIMIENTO_T_HA'

# Limpiar las columnas de texto e identificadores para dejar solo los índices satelitales numéricos
X = df.drop(columns=['ID_POLIGONO', 'CONJUNTO', 'Unnamed: 4', columna_objetivo], errors='ignore')
y = df[columna_objetivo]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

modelo_rf = RandomForestRegressor(n_estimators=200, random_state=42)
print("Construyendo los árboles de decisión y buscando patrones...")
modelo_rf.fit(X_train, y_train)

predicciones = modelo_rf.predict(X_test)
mae = mean_absolute_error(y_test, predicciones)
r2 = r2_score(y_test, predicciones)

print("\n--- RESULTADOS DEL EXAMEN ---")
print(f"Error Absoluto Medio (MAE): {mae:.3f} toneladas por hectárea")
print(f"Precisión R2: {r2:.3f}")

importancias = pd.DataFrame({
    'Variable': X.columns,
    'Importancia': modelo_rf.feature_importances_
}).sort_values(by='Importancia', ascending=False)

print("\n--- LAS 5 VARIABLES MÁS DETERMINANTES ---")
print(importancias.head(5).to_string(index=False))