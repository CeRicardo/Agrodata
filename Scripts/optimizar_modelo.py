import pandas as pd
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score

df = pd.read_csv('Dataset_Machine_Learning_2025.csv')
columna_objetivo = 'RENDIMIENTO_T_HA'

# Limpiar las columnas y preparar X / y
X = df.drop(columns=['ID_POLIGONO', 'CONJUNTO', 'Unnamed: 4', columna_objetivo], errors='ignore')
y = df[columna_objetivo]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 1. Definir el modelo base vacío
rf = RandomForestRegressor(random_state=42)

# 2. Definir la cuadrícula de configuraciones a probar
# Python probará todas las combinaciones posibles de estos números
param_grid = {
    'n_estimators': [100, 200, 300, 400],      # ¿Cuántos árboles plantar?
    'max_depth': [None, 5, 10, 15],            # ¿Qué tan profundas pueden ser las ramas?
    'min_samples_split': [2, 5, 10],           # Mínimo de parcelas para tomar una decisión
    'min_samples_leaf': [1, 2, 4]              # Mínimo de parcelas en la respuesta final
}

# 3. Configurar el optimizador
# cv=5 significa que hará 5 simulaciones de examen por cada configuración
# n_jobs=-1 usa todos los núcleos de tu procesador para ir más rápido
optimizador = GridSearchCV(estimator=rf, param_grid=param_grid, 
                           cv=5, n_jobs=-1, scoring='neg_mean_absolute_error')

print("Iniciando la optimización intensiva. Probando cientos de combinaciones...")
print("Esto puede tardar unos segundos o minutos dependiendo de tu computadora.\n")

# 4. Entrenar el optimizador
optimizador.fit(X_train, y_train)

# 5. Extraer el mejor modelo encontrado
mejor_modelo = optimizador.best_estimator_

# 6. Evaluar el mejor modelo con el examen final (X_test)
predicciones = mejor_modelo.predict(X_test)
mae = mean_absolute_error(y_test, predicciones)
r2 = r2_score(y_test, predicciones)

print("--- LA MEJOR CONFIGURACIÓN ENCONTRADA ---")
for parametro, valor in optimizador.best_params_.items():
    print(f"{parametro}: {valor}")

print("\n--- RESULTADOS DEL MODELO OPTIMIZADO ---")
print(f"Error Absoluto Medio (MAE): {mae:.3f} toneladas por hectárea")
print(f"Precisión R2: {r2:.3f}")