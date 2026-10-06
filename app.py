import pandas as pd
import streamlit as st
import geopandas as gpd
import folium
from streamlit_folium import st_folium

# Configuración inicial de la página
st.set_page_config(
    page_title="AgroCebada 2026",
    page_icon="🌾",
    layout="wide",  # Aprovecha todo el ancho de la pantalla
)

st.title("🌾 Plataforma de Estimación de Rendimiento de Cebada")
st.markdown("---")


# 1. Cargar datos con caché para que la app sea rápida
@st.cache_data
def cargar_datos():
  # Lee la tabla de auditoría generada por tu Random Forest
  return pd.read_csv("./data/outputModel/Auditoria_Parcelas_Optimizada.csv")


df_auditoria = cargar_datos()

# 2. Barra lateral para selección de parcela
st.sidebar.header("Opciones de Consulta")
parcelas_disponibles = df_auditoria["ID_POLIGONO"].unique()
id_seleccionado = st.sidebar.selectbox(
    "Selecciona el ID de Parcela:", parcelas_disponibles
)

# 3. Filtrar datos de la parcela seleccionada
datos_parcela = df_auditoria[
    df_auditoria["ID_POLIGONO"] == id_seleccionado
].iloc[0]

# 4. Mostrar información principal en columnas
col_a, col_b, col_c = st.columns(3)

with col_a:
  st.info(f"**Identificador:** {id_seleccionado}")
  st.write(f"**Conjunto:** {datos_parcela['GRUPO']}")

with col_b:
  pred = datos_parcela["Prediccion_Ton_Ha"]
  st.metric(label="Rendimiento Predicho", value=f"{pred:.2f} t/ha")

with col_c:
  real = datos_parcela["Real_Ton_Ha"]
  if pd.isna(real):
    st.metric(label="Rendimiento Real Histórico", value="Oculto (Predicción)")
  else:
    error_abs = abs(real - pred)
    st.metric(
        label="Rendimiento Real Histórico",
        value=f"{real:.2f} t/ha",
        delta=f"-{error_abs:.2f} diff",
    )

st.markdown("---")
st.subheader("🗺️ Ubicación Geográfica de la Parcela")


# 5. Función con caché para cargar el mapa una sola vez de forma rápida
@st.cache_data
def cargar_geometrias():
    # Cambia esta ruta por la ubicación real de tu archivo .shp
    ruta_shp = './data/raw/Parcelas_Reto_AGC_CONJUNTO_70_30/Parcelas_Reto_AGC_CONJUNTO.shp'
    gdf = gpd.read_file(ruta_shp)

    # Folium requiere que las coordenadas estén en Lat/Lon (WGS84 - EPSG:4326)
    gdf = gdf.to_crs(epsg=4326)
    return gdf


gdf_parcelas = cargar_geometrias()

# 6. Filtrar únicamente el polígono que el usuario seleccionó
parcela_geo = gdf_parcelas[gdf_parcelas['ID_POLIGON'] == id_seleccionado]

# Asegúrate de usar el nombre de columna corto que descubriste en el paso anterior (ej. 'ID_POLIGON')
nombre_columna_id = 'ID_POLIGON'

# 3. Obtener el punto central de la parcela seleccionada para que la cámara viaje hacia ella
if not parcela_geo.empty:
    centroide = parcela_geo.geometry.centroid.iloc[0]
    lat_centro = centroide.y
    lon_centro = centroide.x
    zoom_inicial = 13  # Nivel de zoom alejado para ver a los vecinos
else:
    lat_centro, lon_centro = 19.4326, -99.1332
    zoom_inicial = 10

# 4. Crear el mapa interactivo base
mapa = folium.Map(location=[lat_centro, lon_centro], zoom_start=zoom_inicial, tiles="CartoDB positron")

# 5. Dibujar TODAS las 197 parcelas con estilo condicional
folium.GeoJson(
    gdf_parcelas,
    style_function=lambda feature: {
        # Si el ID de esta parcela coincide con el seleccionado, píntalo verde; si no, píntalo gris claro
        'fillColor': '#28a745' if feature['properties'][nombre_columna_id] == id_seleccionado else '#cccccc',
        'color': '#1e7e34' if feature['properties'][nombre_columna_id] == id_seleccionado else '#999999',
        'weight': 3 if feature['properties'][nombre_columna_id] == id_seleccionado else 1,
        'fillOpacity': 0.8 if feature['properties'][nombre_columna_id] == id_seleccionado else 0.4
    },
    # Mostrar el ID de la parcela al pasar el mouse por encima
    tooltip=folium.features.GeoJsonTooltip(
        fields=[nombre_columna_id],
        aliases=['Parcela:']
    )
).add_to(mapa)

# 6. Renderizar el mapa dentro de Streamlit
st_folium(mapa, width=1200, height=500)

# 11. Vista de tabla general
st.subheader("📋 Resumen General de Parcelas")
st.dataframe(df_auditoria, use_container_width=True)