import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
from io import BytesIO
import requests

# --- Paleta de Colores ---
# Definición de colores en formato RGB (0-1) para Matplotlib
color_primario_1_rgb = (14/255, 69/255, 74/255) # 0E454A (Oscuro)
color_primario_2_rgb = (31/255, 255/255, 95/255) # 1FFF5F (Verde vibrante)
color_primario_3_rgb = (255/255, 255/255, 255/255) # FFFFFF (Blanco)

# Colores del logo de Sustrend para complementar
color_sustrend_1_rgb = (0/255, 155/255, 211/255) # 009BD3 (Azul claro)
color_sustrend_2_rgb = (0/255, 140/255, 207/255) # 008CCF (Azul medio)
color_sustrend_3_rgb = (0/255, 54/255, 110/255) # 00366E (Azul oscuro)

# Selección de colores para los gráficos
colors_for_charts = [color_primario_1_rgb, color_primario_2_rgb, color_sustrend_1_rgb, color_sustrend_3_rgb]

# --- Configuración de la página de Streamlit ---
st.set_page_config(layout="wide")

st.title('✨ Visualizador de Impactos - Proyecto P3')
st.subheader('Transformación de descartes hortofrutícolas')
st.markdown("""
    Ajusta los parámetros para explorar cómo las proyecciones de impacto ambiental y económico del proyecto
    varían con diferentes escenarios de volumen procesado, tasa de recuperación, y precio de mercado.
""")

# --- Datos del Proyecto (Línea Base) ---
# Datos línea base (según ficha TTGF ANEXO PT1_Avance 1.docx.pdf y Ficha_Tecnica_P3.docx)
# Se asume que estos son valores de una línea base de "no intervención" o "práctica común".
base_material = 55.35 # Material valorizado (ton/año)
base_gei = 44.28 # GEI evitados (tCO₂e/año)
base_ingresos = 0 # Asumimos 0 ingresos de valorización en la línea base si el material se desecha.

# --- 2. Widgets Interactivos para Parámetros (Streamlit) ---
st.sidebar.header('Parámetros de Simulación')

volumen_total = st.sidebar.slider(
    'Volumen Total Procesado (ton/año):',
    min_value=50,
    max_value=500,
    value=90,
    step=10,
    help='Volumen total de descartes hortofrutícolas procesados anualmente.'
)

tasa_recuperacion = st.sidebar.slider(
    'Tasa de Recuperación del proceso (%):',
    min_value=0.20,
    max_value=0.70,
    value=0.615,
    step=0.01,
    format='%.1f%%',
    help='Porcentaje de material recuperado de los descartes procesados. (Rendimiento actual: 61.5%)'
)

factor_emision = st.sidebar.slider(
    'Factor de Emisión GEI (relleno sanitario) (tCO₂e/ton):',
    min_value=0.5,
    max_value=1.5,
    value=0.8,
    step=0.1,
    help='Factor de emisión de GEI asociado al desvío de residuos de relleno sanitario.'
)

factor_sustitucion = st.sidebar.slider(
    'Factor de Sustitución de insumos sintéticos (%):',
    min_value=0.10,
    max_value=0.30,
    value=0.18,
    step=0.01,
    format='%.1f%%',
    help='Porcentaje de ingredientes sintéticos reemplazados por el material valorizado.'
)

precio_mercado = st.sidebar.slider(
    'Precio de Mercado del ingrediente (USD/ton):',
    min_value=3000,
    max_value=10000,
    value=5400,
    step=500,
    help='Precio de venta estimado por tonelada del nuevo ingrediente natural.'
)

# --- 3. Cálculos de Indicadores ---
material_valorizado = volumen_total * tasa_recuperacion
gei_evitado = material_valorizado * factor_emision
ingredientes_reemplazados = material_valorizado * factor_sustitucion
ingresos_estimados = material_valorizado * precio_mercado
valor_materia_prima = volumen_total * 1000 * 0.75 # USD, usando precio bajo 0.75 USD/kg
empleos_generados = 2 # Dato fijo del script original
simbiosis_industrial = 5 # Dato fijo del script original

st.header('Resultados Proyectados Anuales:')

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(label="♻️ **Material Valorizado**", value=f"{material_valorizado:.2f} ton/año")
    st.caption("Cantidad de descartes reincorporados a la cadena de valor.")
with col2:
    st.metric(label="🌍 **GEI Evitados**", value=f"{gei_evitado:.2f} tCO₂e/año")
    st.caption("Reducción de emisiones de gases de efecto invernadero por desvío de residuos.")
with col3:
    st.metric(label="🌱 **Ingredientes Sintéticos Reemplazados**", value=f"{ingredientes_reemplazados:.2f} ton/año")
    st.caption("Cantidad de insumos sintéticos sustituidos por el ingrediente natural.")

col4, col5 = st.columns(2)

with col4:
    st.metric(label="💰 **Ingresos Estimados**", value=f"USD {ingresos_estimados:,.2f}/año")
    st.caption("Ingresos generados por la venta del ingrediente valorizado.")
with col5:
    st.metric(label="🤝 **Simbiosis Industrial**", value=f"{simbiosis_industrial} interacciones")
    st.caption("Alianzas colaborativas generadas con otras industrias.")

# st.write(f"Costo estimado materia prima (Frutexsa → PatagoniaFresh): USD {valor_materia_prima:,.2f} /año")
# st.write(f"Empleos generados: {empleos_generados}")

st.markdown("---")

st.header('📊 Análisis Gráfico de Impactos')

# --- Visualización (Gráficos 2D con Matplotlib) ---
fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(20, 7), facecolor=color_primario_3_rgb)
fig.patch.set_facecolor(color_primario_3_rgb)

labels = ['Línea Base', 'Proyección']
bar_width = 0.6
x = np.arange(len(labels))

# --- Gráfico 1: GEI Evitados (tCO₂e/año) ---
gei_values = [base_gei, gei_evitado]
bars1 = ax1.bar(x, gei_values, width=bar_width, color=[colors_for_charts[0], colors_for_charts[1]])
ax1.set_ylabel('tCO₂e/año', fontsize=12, color=colors_for_charts[3])
ax1.set_title('GEI Evitados', fontsize=14, color=colors_for_charts[3], pad=20)
ax1.set_xticks(x)
ax1.set_xticklabels(labels, rotation=15, color=colors_for_charts[0])
ax1.yaxis.set_tick_params(colors=colors_for_charts[0])
ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)
ax1.tick_params(axis='x', length=0)
max_gei_val = max(gei_values)
ax1.set_ylim(bottom=0, top=max(max_gei_val * 1.15, 1))
for bar in bars1:
    yval = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2, yval + 0.05 * yval, round(yval, 2), ha='center', va='bottom', color=colors_for_charts[0])

# --- Gráfico 2: Material Valorizado (ton/año) ---
material_values = [base_material, material_valorizado]
bars2 = ax2.bar(x, material_values, width=bar_width, color=[colors_for_charts[2], colors_for_charts[3]])
ax2.set_ylabel('Toneladas/año', fontsize=12, color=colors_for_charts[0])
ax2.set_title('Material Valorizado', fontsize=14, color=colors_for_charts[3], pad=20)
ax2.set_xticks(x)
ax2.set_xticklabels(labels, rotation=15, color=colors_for_charts[0])
ax2.yaxis.set_tick_params(colors=colors_for_charts[0])
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)
ax2.tick_params(axis='x', length=0)
max_material_val = max(material_values)
ax2.set_ylim(bottom=0, top=max(max_material_val * 1.15, 1))
for bar in bars2:
    yval = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2, yval + 0.05 * yval, round(yval, 2), ha='center', va='bottom', color=colors_for_charts[0])

# --- Gráfico 3: Ingresos Estimados (USD/año) ---
ingresos_values = [base_ingresos, ingresos_estimados]
bars3 = ax3.bar(x, ingresos_values, width=bar_width, color=[colors_for_charts[1], colors_for_charts[0]])
ax3.set_ylabel('USD/año', fontsize=12, color=colors_for_charts[3])
ax3.set_title('Ingresos Estimados', fontsize=14, color=colors_for_charts[3], pad=20)
ax3.set_xticks(x)
ax3.set_xticklabels(labels, rotation=15, color=colors_for_charts[0])
ax3.yaxis.set_tick_params(colors=colors_for_charts[0])
ax3.spines['top'].set_visible(False)
ax3.spines['right'].set_visible(False)
ax3.tick_params(axis='x', length=0)
max_ingresos_val = max(ingresos_values)
ax3.set_ylim(bottom=0, top=max(max_ingresos_val * 1.15, 1000))
for bar in bars3:
    yval = bar.get_height()
    ax3.text(bar.get_x() + bar.get_width()/2, yval + 0.05 * yval, f"${yval:,.0f}", ha='center', va='bottom', color=colors_for_charts[0])

plt.tight_layout(rect=[0, 0.05, 1, 0.95])
st.pyplot(fig)

# --- Funcionalidad de descarga de cada gráfico ---
st.markdown("---")
st.subheader("Descargar Gráficos Individualmente")

# Función auxiliar para generar el botón de descarga
def download_button(fig, filename_prefix, key):
    buf = BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", dpi=300)
    st.download_button(
        label=f"Descargar {filename_prefix}.png",
        data=buf.getvalue(),
        file_name=f"{filename_prefix}.png",
        mime="image/png",
        key=key
    )

# Crear figuras individuales para cada gráfico para poder descargarlas
# Figura 1: GEI Evitados
fig_gei, ax_gei = plt.subplots(figsize=(8, 6), facecolor=color_primario_3_rgb)
ax_gei.bar(x, gei_values, width=bar_width, color=[colors_for_charts[0], colors_for_charts[1]])
ax_gei.set_ylabel('tCO₂e/año', fontsize=12, color=colors_for_charts[3])
ax_gei.set_title('GEI Evitados', fontsize=14, color=colors_for_charts[3], pad=20)
ax_gei.set_xticks(x)
ax_gei.set_xticklabels(labels, rotation=15, color=colors_for_charts[0])
ax_gei.yaxis.set_tick_params(colors=colors_for_charts[0])
ax_gei.spines['top'].set_visible(False)
ax_gei.spines['right'].set_visible(False)
ax_gei.tick_params(axis='x', length=0)
ax_gei.set_ylim(bottom=0, top=max(max_gei_val * 1.15, 1))
for bar in ax_gei.patches:
    yval = bar.get_height()
    ax_gei.text(bar.get_x() + bar.get_width()/2, yval + 0.05 * yval, round(yval, 2), ha='center', va='bottom', color=colors_for_charts[0])
plt.tight_layout()
download_button(fig_gei, "GEI_Evitados", "download_gei")
plt.close(fig_gei)

# Figura 2: Material Valorizado
fig_material, ax_material = plt.subplots(figsize=(8, 6), facecolor=color_primario_3_rgb)
ax_material.bar(x, material_values, width=bar_width, color=[colors_for_charts[2], colors_for_charts[3]])
ax_material.set_ylabel('Toneladas/año', fontsize=12, color=colors_for_charts[0])
ax_material.set_title('Material Valorizado', fontsize=14, color=colors_for_charts[3], pad=20)
ax_material.set_xticks(x)
ax_material.set_xticklabels(labels, rotation=15, color=colors_for_charts[0])
ax_material.yaxis.set_tick_params(colors=colors_for_charts[0])
ax_material.spines['top'].set_visible(False)
ax_material.spines['right'].set_visible(False)
ax_material.tick_params(axis='x', length=0)
ax_material.set_ylim(bottom=0, top=max(max_material_val * 1.15, 1))
for bar in ax_material.patches:
    yval = bar.get_height()
    ax_material.text(bar.get_x() + bar.get_width()/2, yval + 0.05 * yval, round(yval, 2), ha='center', va='bottom', color=colors_for_charts[0])
plt.tight_layout()
download_button(fig_material, "Material_Valorizado", "download_material")
plt.close(fig_material)

# Figura 3: Ingresos Estimados
fig_ingresos, ax_ingresos = plt.subplots(figsize=(8, 6), facecolor=color_primario_3_rgb)
ax_ingresos.bar(x, ingresos_values, width=bar_width, color=[colors_for_charts[1], colors_for_charts[0]])
ax_ingresos.set_ylabel('USD/año', fontsize=12, color=colors_for_charts[3])
ax_ingresos.set_title('Ingresos Estimados', fontsize=14, color=colors_for_charts[3], pad=20)
ax_ingresos.set_xticks(x)
ax_ingresos.set_xticklabels(labels, rotation=15, color=colors_for_charts[0])
ax_ingresos.yaxis.set_tick_params(colors=colors_for_charts[0])
ax_ingresos.spines['top'].set_visible(False)
ax_ingresos.spines['right'].set_visible(False)
ax_ingresos.tick_params(axis='x', length=0)
ax_ingresos.set_ylim(bottom=0, top=max(max_ingresos_val * 1.15, 1000))
for bar in ax_ingresos.patches:
    yval = bar.get_height()
    ax_ingresos.text(bar.get_x() + bar.get_width()/2, yval + 0.05 * yval, f"${yval:,.0f}", ha='center', va='bottom', color=colors_for_charts[0])
plt.tight_layout()
download_button(fig_ingresos, "Ingresos_Estimados", "download_ingresos")
plt.close(fig_ingresos)

st.markdown("---")
st.markdown("### Información Adicional:")
st.markdown(f"- **Estado de Avance y Recomendaciones:** El proyecto P3 ha alcanzado un avance significativo en el desarrollo experimental de un ingrediente natural a partir de descartes hortofrutícolas, validando su potencial funcional y nutricional para sustituir ingredientes sintéticos en alimentos. La iniciativa se encuentra actualmente en fase de validación tecnológica intermedia (TRL 6–7), con pruebas realizadas a escala piloto y primeras aproximaciones a procesos industriales de transformación.")

st.markdown("---")
# Texto de atribución centrado
st.markdown("<div style='text-align: center;'>Visualizador Creado por el equipo Sustrend SpA en el marco del Proyecto TT GREEN Foods</div>", unsafe_allow_html=True)

# Aumentar el espaciado antes de los logos
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# --- Mostrar Logos ---
col_logos_left, col_logos_center, col_logos_right = st.columns([1, 2, 1])

with col_logos_center:
    sustrend_logo_url = "https://drive.google.com/uc?id=1vx_znPU2VfdkzeDtl91dlpw_p9mmu4dd"
    ttgreenfoods_logo_url = "https://drive.google.com/uc?id=1uIQZQywjuQJz6Eokkj6dNSpBroJ8tQf8"

    try:
        sustrend_response = requests.get(sustrend_logo_url)
        sustrend_response.raise_for_status()
        sustrend_image = Image.open(BytesIO(sustrend_response.content))

        ttgreenfoods_response = requests.get(ttgreenfoods_logo_url)
        ttgreenfoods_response.raise_for_status()
        ttgreenfoods_image = Image.open(BytesIO(ttgreenfoods_response.content))

        st.image([sustrend_image, ttgreenfoods_image], width=100)
    except requests.exceptions.RequestException as e:
        st.error(f"Error al cargar los logos desde las URLs. Por favor, verifica los enlaces: {e}")
    except Exception as e:
        st.error(f"Error inesperado al procesar las imágenes de los logos: {e}")

st.markdown("<div style='text-align: center; font-size: small; color: gray;'>Viña del Mar, Valparaíso, Chile</div>", unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.markdown(f"<div style='text-align: center; font-size: smaller; color: gray;'>Versión del Visualizador: 1.8</div>", unsafe_allow_html=True)
st.sidebar.markdown(f"<div style='text-align: center; font-size: x-small; color: lightgray;'>Desarrollado con Streamlit</div>", unsafe_allow_html=True)
