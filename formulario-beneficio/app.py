from pathlib import Path

import streamlit as st

RAIZ = Path(__file__).resolve().parent

st.set_page_config(page_title="Beneficio Socios | Club Atlético Platense", page_icon=str(RAIZ / "assets" / "escudo.png"), layout="centered")

navegacion = st.navigation(
    [
        st.Page(RAIZ / "vistas" / "formulario.py", title="Formulario", default=True),
        st.Page(RAIZ / "vistas" / "admin.py", title="Administración", url_path="admin"),
    ],
    position="hidden",
)
navegacion.run()
