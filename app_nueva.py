import streamlit as st
import pandas as pd
import base64  

st.set_page_config(page_title="Moratoria Socios", layout="centered")

# --- 1. FONDO DE PANTALLA ---
nombre_imagen_fondo = "fondo.png" 

try:
    with open(nombre_imagen_fondo, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode("utf-8").replace("\n", "")
    
    css_fondo = f"""
    <style>
    .stApp, [data-testid="stAppViewContainer"] {{
        background-image: linear-gradient(rgba(43, 23, 8, 0.8), rgba(43, 23, 8, 0.8)), url("data:image/png;base64,{encoded_string}") !important;
        background-size: cover !important;
        background-position: center !important;
        background-attachment: fixed !important;
    }}
    [data-testid="stHeader"] {{
        background: transparent !important;
    }}
    </style>
    """
    st.markdown(css_fondo, unsafe_allow_html=True)

except FileNotFoundError:
    st.error("⚠️ Python no encuentra el archivo 'fondo.png'. Asegurate de que esté en la misma carpeta.")

# --- 2. CSS GENERAL (Letras, Botones y Cajas) ---
st.markdown("""
    <style>
    h1, h2, h3, p, span, label, div { color: #F2E3D5 !important; }
    .stTextInput input {
        background-color: #F2E3D5; color: #2B1708 !important; border-radius: 8px; border: 2px solid #8B5A2B; font-weight: bold;
    }
    .stButton>button {
        background-color: #8B5A2B; color: #F2E3D5 !important; border: none; border-radius: 8px; width: 100%; font-weight: bold; font-size: 18px;
    }
    .stButton>button:hover { background-color: #A06B35; color: #FFFFFF !important; }
    .stAlert { background-color: #3E2413; color: #F2E3D5; border: 1px solid #8B5A2B; }
    </style>
""", unsafe_allow_html=True)
# -----------------------------------------------

col_vacia1, col_escudo, col_vacia2 = st.columns([1, 1.5, 1])
with col_escudo:
    st.image("escudo.png", use_container_width=True)

st.markdown("<h1 style='text-align: center; color: #F2E3D5 !important;'>Moratoria Socios<br>Es el momento de volver</h1>", unsafe_allow_html=True)
st.markdown("---")

@st.cache_data
def cargar_datos():
    df_temp = pd.read_excel("base_moratoria.xlsx", dtype={'DNI': str})
    df_temp.columns = df_temp.columns.str.strip() 
    return df_temp

try:
    df = cargar_datos()
except FileNotFoundError:
    st.error("No se encontró el archivo base_moratoria.xlsx.")
    st.stop()

dni_ingresado = st.text_input("Ingresá tu DNI (sin puntos ni espacios):")
boton_consultar = st.button("Consultar")

if boton_consultar:
    if dni_ingresado:
        resultado = df[df['DNI'] == dni_ingresado]
        
        if not resultado.empty:
            # --- VISTA DE ÉXITO (DNI ENCONTRADO) ---
            socio_antiguo = int(resultado.iloc[0]['Numero de Socio Antiguo'])
            socio_nuevo = int(resultado.iloc[0]['Posible Nuevo numero de Socio'])
            
            # --- CABLES NORMALES DE NUEVO ---
            deuda_real = resultado.iloc[0]['Deuda Real']
            
            try:
                deuda_promocion = resultado.iloc[0]['Deuda en promoción']
            except KeyError:
                st.error(f"🚨 ERROR DE LECTURA: No encuentro la columna 'Deuda en promoción'.")
                st.stop()
            # --------------------------------

            st.markdown("### 🎫 Estado de tu Carnet")
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"""
                <div style='background-color:#3E2413; padding:15px; border-radius:10px; text-align:center; border: 1px solid #8B5A2B;'>
                    <b style='color:#F2E3D5 !important;'>Actual Número de Socio</b><br>
                    <span style='font-size:28px; font-weight:bold; color:#F2E3D5 !important;'>{socio_antiguo}</span>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                st.markdown(f"""
                <div style='background-color:#3E2413; padding:15px; border-radius:10px; text-align:center; border: 1px solid #8B5A2B;'>
                    <b style='color:#F2E3D5 !important;'>Posible Nuevo Número Depurado</b><br>
                    <span style='font-size:28px; font-weight:bold; color:#F2E3D5 !important;'>{socio_nuevo}</span>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("""
            <p style='text-align: center; font-size: 13px; color: #F2E3D5; opacity: 0.8; font-style: italic; margin-top: 10px;'>
                El Posible Nuevo Número de Socio Depurado puede diferir dependiendo de la cantidad de Socios que se adhieran a la moratoria.
            </p>
            """, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("### 💰 Estado de Cuenta")
            col3, col4 = st.columns(2)
            with col3:
                st.markdown(f"""
                <div style='padding:20px; text-align:center;'>
                    <span style='color:#F2E3D5 !important;'>Deuda Histórica Real</span><br>
                    <span style='font-size:22px; text-decoration: line-through; color:#A0A0A0 !important;'>${deuda_real:,.2f}</span>
                </div>
                """, unsafe_allow_html=True)
            with col4:
                st.markdown(f"""
                <div style='background-color:#F2E3D5 !important; padding:20px; border-radius:10px; text-align:center; box-shadow: 0px 4px 6px rgba(0,0,0,0.3);'>
                    <b style='color:#2B1708 !important;'>Deuda en Promoción</b><br>
                    <span style='font-size:30px; font-weight:bold; color:#2B1708 !important;'>${deuda_promocion:,.2f}</span>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("""
            <div style='background-color:#3E2413; padding:20px; border-radius:10px; text-align:center; border: 1px solid #8B5A2B;'>
                <span style='color:#F2E3D5 !important; font-size: 16px;'>
                    Podes regularizar tu situación presentandote en oficina de Socios, escribiendo a <b>moras@cap.org.ar</b> o completando el siguiente forms para que un colaborador te contacte:<br><br>
                    <a href='https://forms.gle/b4WqSNHfZv4xrLL99' target='_blank' style='color:#FFFFFF !important; font-weight:bold; text-decoration: underline; font-size: 18px;'>https://forms.gle/b4WqSNHfZv4xrLL99</a>
                </span>
            </div>
            """, unsafe_allow_html=True)

            # --- LOGO DE CIERRE (ÉXITO) ---
            st.markdown("<br><br>", unsafe_allow_html=True)
            col_cierra_vacia1, col_cierra_logo, col_cierra_vacia2 = st.columns([1, 2, 1])
            with col_cierra_logo:
                try:
                    st.image("logo_campana.png", use_container_width=True)
                except FileNotFoundError:
                    pass
            
        else:
            # --- VISTA DE ERROR (DNI NO ENCONTRADO / REBOTE) ---
            st.markdown("""
            <div style='background-color:#3E2413; padding:15px; border-radius:8px; border: 1px solid #8B5A2B; color: #F2E3D5;'>
                ⚠️ No encontramos un socio habilitado para la moratoria con ese DNI. Por favor, contactate en oficina de socios o al siguiente mail <u style='font-weight:bold;'>moras@cap.org.ar</u>
            </div>
            """, unsafe_allow_html=True)

            # --- LOGO DE CIERRE (ERROR) ---
            st.markdown("<br><br>", unsafe_allow_html=True)
            col_rebote_vacia1, col_rebote_logo, col_rebote_vacia2 = st.columns([1, 2, 1])
            with col_rebote_logo:
                try:
                    st.image("logo_campana.png", use_container_width=True)
                except FileNotFoundError:
                    pass
            
    else:
        st.warning("Por favor, ingresá tu número de DNI antes de hacer clic en Consultar.")
