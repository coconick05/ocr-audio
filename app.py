import streamlit as st
import os
import time
import glob
import cv2
import numpy as np
import pytesseract
from PIL import Image
from gtts import gTTS
from googletrans import Translator

# Estilo: todos los textos en fucsia
st.markdown(
    """
    <style>
    :root {
        --fucsia: #FF00FF;
    }

    /* Títulos, subtítulos y encabezados */
    h1, h2, h3, h4, h5, h6,
    [data-testid="stHeading"],
    [data-testid="stHeading"] h1,
    [data-testid="stHeading"] h2,
    [data-testid="stHeading"] h3 {
        color: var(--fucsia) !important;
    }

    /* Párrafos, markdown y st.write */
    .stMarkdown, .stMarkdown p, .stMarkdown li, .stMarkdown span,
    [data-testid="stMarkdownContainer"],
    [data-testid="stMarkdownContainer"] p,
    [data-testid="stMarkdownContainer"] li,
    [data-testid="stMarkdownContainer"] span {
        color: var(--fucsia) !important;
    }

    /* Etiquetas de widgets (selectbox, checkbox, uploader, etc.) */
    label, label p, label span, label div,
    [data-testid="stWidgetLabel"],
    [data-testid="stWidgetLabel"] p,
    [data-testid="stCheckbox"] label,
    [data-testid="stCheckbox"] span,
    [data-testid="stCheckbox"] p {
        color: var(--fucsia) !important;
    }

    /* Texto del selectbox (valor seleccionado y opciones) */
    [data-baseweb="select"] div,
    [data-baseweb="select"] span,
    [data-baseweb="select"] input,
    [data-baseweb="popover"] li,
    [data-baseweb="popover"] li div,
    [data-baseweb="popover"] li span {
        color: var(--fucsia) !important;
    }

    /* Uploader */
    [data-testid="stFileUploader"] section,
    [data-testid="stFileUploader"] small,
    [data-testid="stFileUploader"] span,
    [data-testid="stFileUploader"] p,
    [data-testid="stFileUploader"] div {
        color: var(--fucsia) !important;
    }

    /* Captions (por ejemplo, "Imagen cargada.") */
    [data-testid="stCaptionContainer"],
    [data-testid="stCaptionContainer"] p,
    [data-testid="stImageCaption"],
    figcaption {
        color: var(--fucsia) !important;
    }

    /* Mensajes de éxito, advertencia, etc. */
    [data-testid="stAlert"],
    [data-testid="stAlert"] p,
    [data-testid="stAlert"] div,
    [data-testid="stAlert"] span {
        color: var(--fucsia) !important;
    }

    /* Spinner */
    [data-testid="stSpinner"],
    [data-testid="stSpinner"] p {
        color: var(--fucsia) !important;
    }

    /* Botón */
    .stButton button, .stButton button p, .stButton button div {
        color: var(--fucsia) !important;
        border-color: var(--fucsia) !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("Lector y Traductor de Textos")

# Imagen debajo del título principal
if os.path.exists("sisisi.jpg"):
    st.image("sisisi.jpg", use_container_width=True)
else:
    st.warning("No se encontró la imagen sisisi.jpg en la carpeta de la app.")

st.subheader("Sube una imagen con texto, indica el idioma en el que está y el idioma al que quieres traducirlo")

translator = Translator()

try:
    os.mkdir("temp")
except FileExistsError:
    pass


def remove_files(n):
    mp3_files = glob.glob("temp/*mp3")
    if len(mp3_files) != 0:
        now = time.time()
        n_days = n * 86400
        for f in mp3_files:
            if os.stat(f).st_mtime < now - n_days:
                os.remove(f)
                print("Deleted ", f)


remove_files(7)

idiomas = {
    "Inglés": "en",
    "Español": "es",
    "Bengalí": "bn",
    "Coreano": "ko",
    "Mandarín": "zh-cn",
    "Japonés": "ja",
    "Francés": "fr",
}

tld_dict = {
    "Defecto": "com",
    "España": "com.mx",
    "Reino Unido": "co.uk",
    "Estados Unidos": "com",
    "Canadá": "ca",
    "Australia": "com.au",
    "Irlanda": "ie",
    "Sudáfrica": "co.za",
    "Francia": "fr",
}


def text_to_speech(text, output_language, tld):
    tts = gTTS(text, lang=output_language, tld=tld, slow=False)
    file_name = "audio_traducido"
    tts.save(f"temp/{file_name}.mp3")
    return file_name


bg_image = st.file_uploader("Cargar Imagen:", type=["png", "jpg", "jpeg"])

if bg_image is not None:
    st.image(bg_image, caption="Imagen cargada.", use_container_width=True)

    # Guardar la imagen en el sistema de archivos
    with open(bg_image.name, "wb") as f:
        f.write(bg_image.getbuffer())

    st.success(f"Imagen guardada como {bg_image.name}")

    img_cv = cv2.imread(bg_image.name)
    img_rgb = cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)
    texto_extraido = pytesseract.image_to_string(img_rgb)

    st.markdown("### Texto detectado en la imagen:")
    st.write(texto_extraido)

    st.markdown("### Configuración de traducción")

    in_lang = st.selectbox("¿En qué idioma está el texto de la imagen?", list(idiomas.keys()))
    out_lang = st.selectbox("¿A qué idioma quieres traducirlo?", list(idiomas.keys()))

    input_language = idiomas[in_lang]
    output_language = idiomas[out_lang]

    acento = st.selectbox("Selecciona el acento del audio", list(tld_dict.keys()))
    tld = tld_dict[acento]

    display_output_text = st.checkbox("Mostrar texto traducido")

    if st.button("Traducir y generar audio"):
        if texto_extraido.strip() == "":
            st.warning("No se detectó texto en la imagen. Prueba con otra foto más nítida.")
        else:
            traduccion = translator.translate(texto_extraido, src=input_language, dest=output_language)
            texto_traducido = traduccion.text

            nombre_archivo = text_to_speech(texto_traducido, output_language, tld)
            with open(f"temp/{nombre_archivo}.mp3", "rb") as audio_file:
                audio_bytes = audio_file.read()

            st.markdown("## Tu audio:")
            st.audio(audio_bytes, format="audio/mp3", start_time=0)

            if display_output_text:
                st.markdown("## Texto traducido:")
                st.write(texto_traducido)
