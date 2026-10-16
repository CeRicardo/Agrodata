import pandas as pd
import streamlit as st
import geopandas as gpd
import folium
from streamlit_folium import st_folium

# Configuración inicial de la página web (título de la pestaña y diseño a lo ancho)
st.set_page_config(page_title="Resumen | AgroData", layout="wide")

# Creación del menú de navegación lateral
with st.sidebar:
    st.title("Menú - AgroData")
    # Enlaces para moverse entre las diferentes pantallas de la aplicación
    st.page_link("app.py", label="Inicio", icon="🏠")
    st.page_link("pages/resumen.py", label="Resumen General", icon= "📄")
    st.page_link("pages/nosotros.py", label="Nosotros", icon="👥")

# Decorador de caché: guarda los datos en memoria para no recargar el CSV en cada interacción
@st.cache_data
def cargar_datos():
  # Lee el archivo resultante con las predicciones del modelo
  return pd.read_csv("./data/outputModel/Auditoria_Parcelas_Optimizada.csv")

# Carga la tabla de auditoría
df_auditoria = cargar_datos()

# Muestra la tabla de datos en la interfaz ocupando todo el ancho disponible
st.subheader("Resumen General de Parcelas")
st.dataframe(df_auditoria, use_container_width=True)

st.subheader("Mapa de todas las parcelas")

# Decorador de caché para el mapa: evita leer y transformar el archivo espacial repetidamente
@st.cache_data
def cargar_geometrias():
    # Ruta al archivo Shapefile original
    ruta_shp = './data/raw/Parcelas_Reto_AGC_CONJUNTO_70_30/Parcelas_Reto_AGC_CONJUNTO.shp'
    # Geopandas lee el archivo de polígonos
    gdf = gpd.read_file(ruta_shp)

    # Transformación obligatoria para mapas web (Folium requiere el sistema de coordenadas EPSG:4326 - Latitud/Longitud)
    gdf = gdf.to_crs(epsg=4326)
    return gdf

# 1. Cargar las geometrías de las parcelas
gdf_parcelas = cargar_geometrias()
# Nombre exacto de la columna que contiene el ID en el Shapefile
nombre_columna_id = 'ID_POLIGON'

# 2. Calcular el centroide global de TODAS las parcelas
# Esto promedia las latitudes y longitudes de todos los polígonos para saber dónde centrar la cámara del mapa
lat_centro = gdf_parcelas.geometry.centroid.y.mean()
lon_centro = gdf_parcelas.geometry.centroid.x.mean()

# 3. Definir el nivel de acercamiento inicial (Zoom 10 es ideal para abarcar una región amplia de varios estados)
zoom_inicial = 10

# 4. Crear el mapa base centrado en las coordenadas calculadas
mapa = folium.Map(
    location=[lat_centro, lon_centro],
    zoom_start=zoom_inicial,
    # Se utiliza un mapa base satelital de Esri para visualizar el terreno real
    tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
    attr='Esri'
)

# 5. Dibujar todos los polígonos sobre el mapa satelital
folium.GeoJson(
    gdf_parcelas,
    # Se define el estilo visual de cada parcela (relleno naranja, borde rojo y opacidad media)
    style_function=lambda feature: {
        'fillColor': '#ffaa00',
        'color': '#ff0000',
        'weight': 1,
        'fillOpacity': 0.6
    },
    # Tooltip: Ventana emergente que muestra el ID de la parcela al pasar el cursor por encima
    tooltip=folium.features.GeoJsonTooltip(
        fields=[nombre_columna_id],
        aliases=['Parcela:']
    )
).add_to(mapa)

# 6. Renderizar finalmente el mapa interactivo dentro de Streamlit con las dimensiones especificadas
st_folium(mapa, width=1200, height=500)