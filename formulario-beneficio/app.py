import streamlit as st

st.set_page_config(page_title="Beneficio Socios | Club Atlético Platense", page_icon="assets/escudo.png", layout="centered")

navegacion = st.navigation(
    [
        st.Page("vistas/formulario.py", title="Formulario", default=True),
        st.Page("vistas/admin.py", title="Administración", url_path="admin"),
    ],
    position="hidden",
)
navegacion.run()
