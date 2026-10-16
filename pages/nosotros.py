import streamlit as st

# Configuración principal de la página web
# Define el título en la pestaña del navegador, el ícono y el diseño centrado
st.set_page_config(page_title="Sobre Nosotros | AgroData", layout="centered")

# Creación del menú de navegación lateral (Sidebar)
with st.sidebar:
    st.title("Menú - AgroData")
    # Enlaces para navegar entre las distintas páginas de la aplicación
    st.page_link("app.py", label="Inicio", icon="🏠")
    st.page_link("pages/resumen.py", label="Resumen General", icon= "📄")
    st.page_link("pages/nosotros.py", label="Nosotros", icon="👥")

# Título principal de la sección
st.title("Sobre Nosotros")
st.markdown("---") # Separador visual horizontal

# Sección 1: Misión de la plataforma
st.subheader("Nuestra Misión")
st.write("""
Buscamos empoderar a los productores de cebada en la región de **Puebla, Tlaxcala e Hidalgo** acercando el poder de la inteligencia artificial al campo. Nuestro objetivo es traducir datos complejos en **recomendaciones claras, sencillas y directas** que cualquier agricultor pueda entender y aplicar, ayudándoles a asegurar el futuro de sus parcelas y a tomar las mejores decisiones para sus cosechas.
""")

# Sección 2: Contexto sobre el origen del proyecto y el concurso FIRA 2026
st.subheader("El Proyecto")
st.write("""
Esta iniciativa nació como respuesta a los retos planteados por el **concurso Fira 2026**. Sabemos que la agricultura enfrenta cada vez más incertidumbre climática y operativa. Por ello, desarrollamos un sistema basado en modelos de *Machine Learning* que analiza datos históricos y actuales para **predecir escenarios futuros, detectar riesgos a tiempo y sugerir medidas preventivas**. No solo entregamos predicciones; entregamos tranquilidad y herramientas prácticas para mejorar el rendimiento agrícola.
""")

st.markdown("---") # Separador visual horizontal

# Sección 3: Información sobre los desarrolladores y sus roles
st.subheader("El Equipo")
st.write("""
Somos un grupo de 4 estudiantes universitarios que creemos en el trabajo multidisciplinario como la mejor forma de resolver problemas reales. 

Combinamos la tecnología con el conocimiento profundo de la tierra:
\n💻 **3 estudiantes de Ingeniería en Ciencias de la Computación**, encargados de desarrollar los algoritmos de predicción, procesar los datos y construir esta plataforma.
 \nRicardo Cerón Loeza\n
Brayan Jafet Galindo Desion\n
Irvin Hernandez Carmona
\n🌱 **1 estudiante de Ingeniería Agronómica**, encargado de asegurar que cada recomendación del modelo tenga sentido biológico y técnico en el campo, garantizando que la información sea verdaderamente útil para el agricultor.
\n José Angel Morales Ramos
""")

# Sección 4: Llamado a la acción y contacto
st.markdown("<br>", unsafe_allow_html=True) # Espacio en blanco usando etiqueta HTML
# Caja de mensaje destacado (info) para animar a los usuarios a contactar al equipo
st.info("**¿Tienes dudas o sugerencias?** Contáctanos para conocer más sobre cómo nuestros modelos pueden ayudar a proteger y mejorar tu cultivo de cebada.")