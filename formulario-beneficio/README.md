# Formulario Beneficio Socios — Club Atlético Platense

Formulario web (Streamlit) con la identidad de Platense. La persona carga sus datos y los de su madre;
la solicitud solo se guarda si su DNI está en el padrón de socios que sube el club.

## Qué hace

- **Formulario** (`/`): nombre y apellido, WhatsApp, mail y DNI de la persona; nombre y apellido, DNI,
  mail y WhatsApp de la madre; casilla de consentimiento. Si el DNI no figura en el padrón muestra
  *"No estás apto/a como socio/a para recibir el beneficio"* y no guarda nada.
- **Administración** (`/admin`, con contraseña): subir el padrón (.xlsx, .csv o .txt con DNIs),
  ver las solicitudes y descargarlas en Excel.

## Correr local

```bash
pip install -r requirements.txt
cp .streamlit/secrets.toml.example .streamlit/secrets.toml   # y cambiar la clave
streamlit run app.py
```

Abrir http://localhost:8501 (formulario) y http://localhost:8501/admin (administración).

## Publicar en Streamlit Community Cloud

1. New app → este repo → *Main file path*: `formulario-beneficio/app.py`.
2. En *Settings → Secrets* pegar `admin_password = "..."`.
3. Entrar a `/admin` y subir el padrón.

> Los datos (padrón e inscripciones) se guardan en `data/`. En Streamlit Cloud ese disco se borra
> cuando la app se reinicia: descargá el Excel seguido o pasá el guardado a Google Sheets.

## Estructura

```
app.py                 navegación (formulario + admin)
vistas/formulario.py   formulario público
vistas/admin.py        carga de padrón y descarga de inscripciones
core/validacion.py     normalización de DNI, lectura del padrón, validación de campos
core/almacenamiento.py padrón e inscripciones en data/
core/marca.py          colores, tipografías, escudo (ajustar acá según el Brandbook 26)
assets/                escudo, fondo y logo de campaña
tests/                 pytest
```

## Tests

```bash
python -m pytest -q
```
