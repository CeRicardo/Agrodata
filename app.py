import pandas as pd
import streamlit as st
import geopandas as gpd
import folium
from groq import Groq
from streamlit_folium import st_folium

# Inicialización del cliente de Groq utilizando la clave segura almacenada en los secretos de Streamlit
cliente_groq = Groq(api_key=st.secrets["GROQ_API_KEY"])

# Configuración global de la página web
st.set_page_config(
    page_title="AgroData - Fira 2026",
    layout="wide", # Permite que el contenido ocupe todo el ancho de la pantalla
)

st.title("Inicio - Predicción de Rendimiento")

# Decorador para almacenar en caché las geometrías y evitar recargar el archivo espacial en cada interacción
@st.cache_data
def cargar_geometrias():
    ruta_shp = './data/raw/Parcelas_Reto_AGC_CONJUNTO_70_30/Parcelas_Reto_AGC_CONJUNTO.shp'
    gdf = gpd.read_file(ruta_shp)
    # Transformación obligatoria al sistema de coordenadas WGS84 (Lat/Lon) para compatibilidad con Folium web
    gdf = gdf.to_crs(epsg=4326)
    return gdf

# Decorador para almacenar en caché la lectura de archivos CSV
@st.cache_data
def cargar_datos(url):
  return pd.read_csv(url)

# Carga de los conjuntos de datos principales
prediccion = cargar_datos("./data/outputModel/Auditoria_Parcelas_Optimizada.csv")
variables_causantes = cargar_datos("./data/outputModel/Top_5_Variables_Por_Parcela.csv")

# Configuración del menú de navegación lateral
with st.sidebar:
    st.title("Menú - AgroData")
    st.page_link("app.py", label="Inicio", icon="🏠")
    st.page_link("pages/resumen.py", label="Resumen General", icon= "📄")
    st.page_link("pages/nosotros.py", label="Nosotros", icon="👥")

# Interfaz de selección de parcela
st.subheader("Por favor selecciona una parcela: ")
parcelas_disponibles = prediccion["ID_POLIGONO"].unique()
id_seleccionado = st.selectbox("ID de Parcelas disponibles:", parcelas_disponibles)

# Extracción de las 5 variables con mayor impacto para la parcela seleccionada
variables_parcela = variables_causantes[variables_causantes["ID_POLIGONO"] == id_seleccionado].iloc[0]

st.subheader("Información general de la parcela:")

# Inicialización de la variable de estado para guardar la explicación de la IA y evitar que se borre al recargar
if "explicacion_ia" not in st.session_state:
    st.session_state["explicacion_ia"] = ""

# Botón para detonar el análisis agronómico mediante IA
if st.button("Analizar causas de rendimiento", type="primary"):
    with st.spinner("Consultando al agrónomo virtual (Llama 3)..."):
        # Construcción del prompt inyectando las variables específicas de la parcela actual
        prompt = f"""
        Actúa como un ingeniero agrónomo experto. 
        En un cultivo de cebada, las variables '{variables_parcela['Top_1']}, {variables_parcela['Top_2']}, {variables_parcela['Top_3']}, {variables_parcela['Top_4']}, {variables_parcela['Top_5']}' tuvieron un mayor peso durante el crecimiento del cultivo, lo cual provocó un mal rendimiento.
        Genera un texto breve (máximo 2 párrafos) explicando:
        1. Por qué estos valores dañaron el cultivo.
        2. Dos recomendaciones prácticas y de bajo costo para el siguiente ciclo.
        """

        # Llamada a la API de Groq solicitando la respuesta en fragmentos (stream)
        respuesta = cliente_groq.chat.completions.create(
            messages=[
                {"role": "user", "content": prompt}
            ],
            model="openai/gpt-oss-120b", # Nota: Asegúrate de usar un identificador válido de Groq (ej. llama3-8b-8192)
            stream=True
        )

        st.success("Análisis completado:")

        # Función generadora para procesar el flujo de texto en tiempo real
        def parsear_stream(stream_response):
            for chunk in stream_response:
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content

        # Impresión de la respuesta palabra por palabra y captura del texto completo
        texto_generado = st.write_stream(parsear_stream(respuesta))

        # Almacenamiento del texto final en la memoria de la sesión
        st.session_state["explicacion_ia"] = texto_generado

# Si el análisis ya se realizó previamente, se muestra desde la memoria para sobrevivir recargas (ej. interacción del mapa)
elif st.session_state["explicacion_ia"] != "":
    st.success("Análisis completado:")
    st.write(st.session_state["explicacion_ia"])

# Extracción de los datos de predicción para la parcela seleccionada
datos_parcela = prediccion[
    prediccion["ID_POLIGONO"] == id_seleccionado
].iloc[0]

# Creación de 3 columnas alineadas verticalmente para distribuir el mapa y las métricas
col_a, col_b, col_c = st.columns(3, vertical_alignment="center")

with col_a:
    st.subheader("Mapa")

    gdf_parcelas = cargar_geometrias()
    # Filtrado de la geometría correspondiente a la parcela actual
    parcela_geo = gdf_parcelas[gdf_parcelas['ID_POLIGON'] == id_seleccionado]
    nombre_columna_id = 'ID_POLIGON'

    # Cálculo dinámico del centro del mapa y nivel de zoom basado en si se encontró o no el polígono
    if not parcela_geo.empty:
        centroide = parcela_geo.geometry.centroid.iloc[0]
        lat_centro = centroide.y
        lon_centro = centroide.x
        zoom_inicial = 13
    else:
        lat_centro, lon_centro = 19.4326, -99.1332 # Coordenadas por defecto (Centro de México)
        zoom_inicial = 10

    # Inicialización del mapa interactivo con capa satelital de Esri
    mapa = folium.Map(
        location=[lat_centro, lon_centro],
        zoom_start=zoom_inicial,
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        attr='Esri'
    )

    # Renderizado de todas las parcelas con coloreado condicional (verde para la seleccionada, gris para el resto)
    folium.GeoJson(
        gdf_parcelas,
        style_function=lambda feature: {
            'fillColor': '#28a745' if feature['properties'][nombre_columna_id] == id_seleccionado else '#cccccc',
            'color': '#1e7e34' if feature['properties'][nombre_columna_id] == id_seleccionado else '#999999',
            'weight': 3 if feature['properties'][nombre_columna_id] == id_seleccionado else 1,
            'fillOpacity': 0.8 if feature['properties'][nombre_columna_id] == id_seleccionado else 0.4
        },
        tooltip=folium.features.GeoJsonTooltip(
            fields=[nombre_columna_id],
            aliases=['Parcela:']
        )
    ).add_to(mapa)

    # Incrustación del mapa de Folium dentro de la aplicación Streamlit
    st_folium(mapa, width=350, height=350)

with col_b:
  # Tarjeta métrica que muestra el rendimiento estimado por el modelo
  pred = datos_parcela["Prediccion_Ton_Ha"]
  st.metric(label="Rendimiento Predicho", value=f"{pred:.2f} t/ha")

with col_c:
  # Tarjeta métrica que compara la predicción con el rendimiento real, si existe
  real = datos_parcela["Real_Ton_Ha"]
  if pd.isna(real):
    # Si el valor real es nulo (parcelas del conjunto de predicción oficial), se oculta la métrica
    st.metric(label="Rendimiento Real Histórico", value="Oculto (Predicción)")
  else:
    # Si hay valor real, se calcula y muestra el margen de error absoluto
    error_abs = abs(real - pred)
    st.metric(
        label="Rendimiento Real Histórico",
        value=f"{real:.2f} t/ha",
        delta=f"-{error_abs:.2f} diff",
    )