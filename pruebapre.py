import streamlit as st
import pandas as pd
from io import BytesIO
from PIL import Image
import matplotlib.pyplot as plt
import numpy as np

st.set_page_config(page_title="Análisis Granulométrico y SUCS", layout="wide")
st.title("Análisis Granulométrico y Clasificación SUCS")

# --- 1. Entrada de Datos ---
st.header("1. Entrada de Datos")

# Lista de tamices
tamices = [
    "3″", "2½″", "2″", "1½″", "1″", "3/4", "1/2", "3/8", "1/4", "N 4",
    "N 8", "N 10", "N 16", "N 20", "N 30", "N 40", "N 50", "N 80", "N 100", "N 200", "FONDO"
]

# Crear DataFrame editable con Peso y % Pasante Acumulado
df_entrada = pd.DataFrame({"TAMIZ": tamices, "PESO (g)": [None] * len(tamices), "% PASANTE ACUMULADO": [None] * len(tamices)})
df_entrada = st.data_editor(df_entrada, num_rows="fixed", use_container_width=True)

# --- 2. Cálculos Granulométricos ---
st.header("2. Cálculos Granulométricos")

peso_total = df_entrada["PESO (g)"].sum(skipna=True)

if peso_total > 0:
    df = df_entrada.copy()
    df["% RETENIDO"] = (df["PESO (g)"] / peso_total * 100).round(2)
    df["% ACUMULADO"] = df["% RETENIDO"].cumsum().round(2)
    df["% PASANTE"] = (100 - df["% ACUMULADO"]).round(2)
    st.dataframe(df[["TAMIZ", "PESO (g)", "% PASANTE ACUMULADO", "% PASANTE", "% RETENIDO", "% ACUMULADO"]], use_container_width=True) # Mostrar PESO y % PASANTE ACUMULADO
else:
    tiene_pasante = df_entrada["% PASANTE ACUMULADO"].notna().any()
    if tiene_pasante:
        df = pd.DataFrame({"TAMIZ": df_entrada["TAMIZ"]})
        df["% PASANTE ACUMULADO"] = pd.to_numeric(df_entrada["% PASANTE ACUMULADO"], errors='coerce').round(2)
        df["% PASANTE"] = df["% PASANTE ACUMULADO"].fillna(method='ffill').fillna(100.0).round(2)
        df["% RETENIDO"] = (df["% PASANTE"].shift(1, fill_value=100.0) - df["% PASANTE"]).round(2)
        df["% ACUMULADO"] = (100 - df["% PASANTE"]).cumsum().round(2)
        st.dataframe(df[["TAMIZ", "% PASANTE ACUMULADO", "% PASANTE", "% RETENIDO", "% ACUMULADO"]], use_container_width=True) # Mostrar % PASANTE ACUMULADO
    else:
        df = pd.DataFrame({"TAMIZ": tamices, "PESO (g)": [None] * len(tamices), "% PASANTE ACUMULADO": [None] * len(tamices)})
        st.info("Ingresa los pesos parciales o los porcentajes pasantes acumulados.")

# --- 3. Tabla Resumen Tamices 4 y 200 ---
st.header("3. Resumen Tamices N° 4 y N° 200")

tamiz_4_pasante = df.loc[(df["TAMIZ"] == "N 4"), "% PASANTE"].iloc[-1] if "N 4" in df["TAMIZ"].values else None
tamiz_200_pasante = df.loc[(df["TAMIZ"] == "N 200"), "% PASANTE"].iloc[-1] if "N 200" in df["TAMIZ"].values else None
retenido_tamiz_200 = 100 - tamiz_200_pasante if tamiz_200_pasante is not None else None
retenido_tamiz_4 = 100 - tamiz_4_pasante if tamiz_4_pasante is not None else None

if tamiz_4_pasante is not None and tamiz_200_pasante is not None:
    tabla_resumen = pd.DataFrame({
        "TAMIZ": ["N° 4", "N° 200"],
        "% PASANTE ACUMULADO": [tamiz_4_pasante, tamiz_200_pasante]
    })
    styled_tabla = tabla_resumen.style.apply(
        lambda x: ['background-color: #F0FFF0' if x.name == 0 else 'background-color: #FFF0F5' for i in x], axis=1
    )
    st.dataframe(styled_tabla, hide_index=True)

    # --- 4. Visualización de Fracciones Granulométricas (Diagrama Conceptual - Estilo Universitario) ---
    st.header("4. Visualización de Fracciones Granulométricas (Diagrama Conceptual)")
    if retenido_tamiz_200 is not None and tamiz_200_pasante is not None and retenido_tamiz_4 is not None:
        fig, ax = plt.subplots(figsize=(4, 4)) # Ajustar tamaño

        # --- Sección Tamiz 200 (Izquierda) ---
        ax.bar(x=0, height=retenido_tamiz_200 / 100, bottom=tamiz_200_pasante / 100, width=0.4, color='gold', edgecolor='black')
        ax.bar(x=0, height=tamiz_200_pasante / 100, bottom=0, width=0.4, color='lightgoldenrodyellow', edgecolor='black')
        ax.text(x=-0.2, y=0.95, s='SG', fontsize=8, ha='left', va='top')
        ax.text(x=-0.2, y=0.05, s='SF', fontsize=8, ha='left', va='bottom')
        ax.text(x=0, y=0.5, s='TAMIZ\n200', ha='center', va='center')
        ax.text(x=0, y=tamiz_200_pasante / 200, s=f'{tamiz_200_pasante:.0f}%', ha='center', va='center')
        ax.text(x=0, y=tamiz_200_pasante / 100 + retenido_tamiz_200 / 200, s=f'{retenido_tamiz_200:.0f}%', ha='center', va='center')

        # --- Sección Tamiz 4 (Derecha) ---
        altura_division = retenido_tamiz_200 / 100 / 2 if retenido_tamiz_200 is not None else 0

        ax.bar(x=1, height=retenido_tamiz_4 / 100, bottom=tamiz_200_pasante / 100 + (retenido_tamiz_200 - retenido_tamiz_4) / 100, width=0.4, color='lightgreen', edgecolor='black')
        ax.bar(x=1, height=(retenido_tamiz_200 - retenido_tamiz_4) / 100, bottom=tamiz_200_pasante / 100, width=0.4, color='mediumseagreen', edgecolor='black')
        ax.bar(x=1, height=tamiz_200_pasante / 100, bottom=0, width=0.4, color='lightgoldenrodyellow', edgecolor='black')
        ax.text(x=1.2, y=0.95, s='SG', fontsize=8, ha='right', va='top')
        ax.text(x=1.2, y=tamiz_200_pasante / 100 + altura_division / 2, s='SF', fontsize=8, ha='right', va='center')
        ax.text(x=1, y=0.5, s='TAMIZ\n4', ha='center', va='center')
        ax.text(x=1, y=tamiz_200_pasante / 200, s=f'{tamiz_200_pasante:.0f}%', ha='center', va='center')
        ax.text(x=1, y=tamiz_200_pasante / 100 + altura_division / 2, s=f'{retenido_tamiz_200 - retenido_tamiz_4:.0f}%' if retenido_tamiz_4 is not None else f'{retenido_tamiz_200 / 2:.0f}%', ha='center', va='center')
        ax.text(x=1, y=tamiz_200_pasante / 100 + altura_division + altura_division / 2, s=f'{retenido_tamiz_4:.0f}%' if retenido_tamiz_4 is not None else f'{retenido_tamiz_200 / 2:.0f}%', ha='center', va='center')


        ax.set_xticks([0, 1])
        ax.set_xticklabels([]) # Ocultar etiquetas del eje X
        ax.set_yticks([])
        ax.set_ylim(0, 1.1)
        ax.set_xlim(-0.5, 1.5)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.spines['left'].set_visible(False)

        st.pyplot(fig)
    else:
        st.info("No se pueden generar el diagrama conceptual sin los datos de los tamices N°4 y N°200.")

else:
    st.info("No se pueden mostrar los datos de los tamices N°4 y N°200 porque no están presentes en la tabla de granulometría.")

# --- 5. Datos Adicionales para Clasificación SUCS ---
st.header("5. Datos Adicionales para Clasificación SUCS")

Cu = st.number_input("Coeficiente de Uniformidad (Cu)", min_value=0.0, step=0.1, value=None, placeholder="Opcional")
Cc = st.number_input("Coeficiente de Curvatura (Cc)", min_value=0.0, step=0.1, value=None, placeholder="Opcional")
LL = st.number_input("Límite Líquido (LL)", min_value=0.0, step=0.1, value=None, placeholder="Opcional")
LP = st.number_input("Límite Plástico (LP)", min_value=0.0, step=0.1, value=None, placeholder="Opcional")

# Calcular IP e IPC si LL y LP están disponibles
IP = None
IPC = None
tipo_fino_plasticidad = None
if LL is not None and LP is not None:
    IP = LL - LP
    IPC = 0.73 * (LL - 20)
    st.subheader("Valores de Plasticidad")
    st.write(f"Índice de Plasticidad (IPR o IP): {IP:.2f}")
    st.write(f"Índice de Plasticidad de la Carta (IPC): {IPC:.2f}")

    if LL < 20:
        tipo_fino_plasticidad = "NP" # Non-Plastic
    elif IP >= 0.73 * (LL - 20):
        if LL < 50:
            tipo_fino_plasticidad = "CL"
        else:
            tipo_fino_plasticidad = "CH"
    elif IP > 0: # Para ML y MH necesitamos IP > 0 para ser plástico
        if LL < 50:
            tipo_fino_plasticidad = "ML"
        else:
            tipo_fino_plasticidad = "MH"
    else:
        tipo_fino_plasticidad = "NP"

    st.subheader("Clasificación de Finos (Carta de Plasticidad)")
    if tipo_fino_plasticidad:
        st.write(f"El suelo fino se clasifica como: {tipo_fino_plasticidad}")
    else:
        st.write("No se pudo clasificar el suelo fino según la Carta de Plasticidad.")

# --- 6. Carta de Plasticidad ---
st.header("6. Carta de Plasticidad")

if LL is not None and IP is not None:
    fig, ax = plt.subplots(figsize=(8, 6))

    # Definir las líneas de la Carta de Plasticidad
    ll_a = np.linspace(20, 100, 100)
    ip_a = 0.73 * (ll_a - 20)
    ll_u = np.linspace(8, 100, 100)
    ip_u = 0.9 * (ll_u - 8)
    ll_50 = [50] * 100
    ip_50_lower = np.linspace(0, 22, 100) # Ajuste aproximado
    ip_50_upper = np.linspace(0, 40, 100) # Ajuste aproximado

    # Graficar las líneas
    ax.plot(ll_a, ip_a, 'k-', label='Línea "A"')
    ax.plot(ll_u, ip_u, 'k--', label='Línea "U"')
    ax.plot(ll_50, ip_50_upper, 'k:', label='LL = 50')

    # Graficar el punto (LL, IP)
    ax.plot(LL, IP, 'ro', markersize=8, label='Suelo')

    # Etiquetar las regiones (aproximado)
    ax.text(30, 5, 'ML', fontsize=12)
    ax.text(70, 10, 'MH', fontsize=12)
    ax.text(30, 25, 'CL', fontsize=12)
    ax.text(70, 45, 'CH', fontsize=12)

    # Establecer límites y etiquetas
    ax.set_xlabel("Límite Líquido (LL)")
    ax.set_ylabel("Índice de Plasticidad (IP)")
    ax.set_xlim(10, 100)
    ax.set_ylim(0, 60)
    ax.grid(True)
    ax.legend()
    ax.set_title("Carta de Plasticidad de Casagrande")

    st.pyplot(fig)
else:
    st.info("Ingresa los valores de Límite Líquido (LL) y Límite Plástico (LP) para visualizar la Carta de Plasticidad.")

# --- 7. Clasificación SUCS ---
st.header("7. Clasificación SUCS")

clasificacion_final = ""

if tamiz_4_pasante is not None and tamiz_200_pasante is not None:
    # 🔹 Paso 1: Clasificar si es SUELO GRUESO o FINO
    if tamiz_200_pasante < 50:
        tipo_suelo = "Grueso"
    else:
        tipo_suelo = "Fino"

    if tipo_suelo == "Fino":
        clasificacion_final = "FINO - "
        # 🔹 Si es FINO:
        if LL is not None and IP is not None:  # Añadido para manejar casos sin LL y IP
            IPR = 0.73 * (LL - 20)
            if LL >= 50:
                if IP <= IPR:
                    clasificacion_final += "CH"
                else:
                    clasificacion_final += "MH"
            else:  # LL < 50
                if IP <= IPR:
                    clasificacion_final += "CL"
                else:
                    clasificacion_final += "ML"
        else:
            clasificacion_final += "Requiere LL y LP"

    elif tipo_suelo == "Grueso":
        # 🔹 Si es GRUESO:
        # Se subdivide según el % retenido del tamiz #4
        retenido_tamiz_4 = 100 - tamiz_4_pasante
        if retenido_tamiz_4 > (100 - tamiz_200_pasante) / 2:
            tipo_grueso = "GRAVA"
        else:
            tipo_grueso = "ARENA"

        clasificacion_final = f"{tipo_grueso} - "

        # Calcular % Finos
        FC = tamiz_200_pasante

        if FC < 5:
            if Cu is not None and Cc is not None:
                if (tipo_grueso == "GRAVA" and Cu > 4 and 1 <= Cc <= 3) or \
                   (tipo_grueso == "ARENA" and Cu > 6 and 1 <= Cc <= 3):
                    clasificacion_final += "W"
                else:
                    clasificacion_final += "P"
            else:
                clasificacion_final += "Requiere Cu y Cc"
        elif FC >= 12:
            if tipo_fino_plasticidad:
                clasificacion_final += tipo_fino_plasticidad
            else:
                clasificacion_final += "Requiere LL y LP"
        else:  # 5 <= FC < 12 (Doble clasificación)
            clasificacion_primaria = ""
            if Cu is not None and Cc is not None:
                if (tipo_grueso == "GRAVA" and Cu > 4 and 1 <= Cc <= 3) or \
                   (tipo_grueso == "ARENA" and Cu > 6 and 1 <= Cc <= 3):
                    clasificacion_primaria = "W-"
                else:
                    clasificacion_primaria = "P-"
            else:
                clasificacion_primaria = "Requiere Cu y Cc-"

            clasificacion_secundaria = ""
            if tipo_fino_plasticidad:
                clasificacion_secundaria = tipo_fino_plasticidad
            else:
                clasificacion_secundaria = "Requiere LL y LP"

            clasificacion_final += f"{clasificacion_primaria}{clasificacion_secundaria}"

    st.success(f"Clasificación SUCS: {clasificacion_final}")
else:
    st.warning("⚠️  No se puede realizar la clasificación SUCS sin los datos de los tamices N°4 y N°200.")