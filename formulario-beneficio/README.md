# Formulario Beneficio Socios — Club Atlético Platense

Formulario web (Streamlit) con la identidad del Brandbook CAP26 para pedir la entrada de invitado.
La persona carga sus datos y los de su madre; la solicitud solo se guarda si su DNI está en el
padrón de socios que sube el club. Todo queda en una planilla de Google Sheets.

## Qué hace

- **Formulario** (`/`): nombre y apellido, WhatsApp, mail y DNI de la persona; nombre y apellido, DNI,
  mail y WhatsApp de la madre; consentimiento *"Al aceptar me comprometo a utilizar la entrada de
  invitado para el fin asignado."* Si el DNI no está en el padrón muestra *"No estás apto/a como
  socio/a para recibir el beneficio"* y no guarda nada. Un mismo DNI no puede inscribirse dos veces.
- **Administración** (`/admin`, con contraseña): subir el padrón (.xlsx, .csv o .txt con DNIs),
  ver las solicitudes, abrir la planilla y descargar un Excel.

## Google Sheets

La app usa una planilla con dos hojas que crea sola si no existen:

| Hoja | Contenido |
| --- | --- |
| `Inscripciones` | Una fila por solicitud (fecha, datos de la persona, datos de la madre, consentimiento) |
| `Padron` | Columna A con los DNIs de socios; C2 con la fecha de la última carga |

Configuración (una vez):

1. En [Google Cloud Console](https://console.cloud.google.com/) crear un proyecto y habilitar
   **Google Sheets API**.
2. En *IAM y administración → Cuentas de servicio* crear una cuenta de servicio y descargar su
   clave en formato JSON.
3. Crear una planilla vacía en Google Sheets y **compartirla como Editor** con el mail de la cuenta de
   servicio (`...@...iam.gserviceaccount.com`).
4. Copiar el ID de la planilla (la parte de la URL entre `/d/` y `/edit`).
5. Completar los secrets (ver `.streamlit/secrets.toml.example`): `admin_password`,
   `[sheets] spreadsheet_id` y el contenido del JSON bajo `[gcp_service_account]`.

Sin esos secrets la app funciona en **modo prueba** guardando en `data/` (la página de admin lo avisa).
No publicar en ese modo: el disco de Streamlit Cloud se borra cuando la app se reinicia.

## Publicar en Streamlit Community Cloud

1. New app → este repo → *Main file path*: `app.py`.
2. En *Settings → Secrets* pegar los secrets del paso anterior.
3. Entrar a `/admin`, subir el padrón y tocar "Reemplazar padrón con este archivo".

## Correr local

```bash
pip install -r requirements.txt
cp .streamlit/secrets.toml.example .streamlit/secrets.toml   # completar los valores
streamlit run app.py
```

Abrir http://localhost:8501 (formulario) y http://localhost:8501/admin (administración).

## Marca

Según el Brandbook CAP26 (*Escudo & Aplicaciones*), todo en `core/marca.py`:

| Elemento | Valor |
| --- | --- |
| Marrón principal (fondo) | `#4a2e15` |
| Marrón secundario (paneles) | `#342011` |
| Dorado (estrella, acentos, botones) | `#bea15e` |
| Escudo + logotipo | `assets/logo_cap.svg`, vectorial, tomado del brandbook |
| Títulos y números (Awesome Serif Italic) | Playfair Display Italic |
| Rótulos (Knockout) | Oswald Light, mayúsculas espaciadas |
| Textos (logotipo) | Montserrat |

Awesome Serif y Knockout son tipografías comerciales; se usan sus equivalentes de Google Fonts.

## Estructura

```
app.py                  navegación (formulario + admin)
vistas/formulario.py    formulario público
vistas/admin.py         carga de padrón y descarga de inscripciones
core/validacion.py      normalización de DNI, lectura del padrón, validación de campos
core/almacenamiento.py  Google Sheets (y modo prueba local)
core/config.py          secrets y elección del almacenamiento
core/marca.py           colores, tipografías y componentes visuales
assets/                 logo y escudo del brandbook
tests/                  pytest
```

## Tests

```bash
python -m pytest -q
```
