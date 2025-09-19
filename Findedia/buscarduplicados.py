import shutil
import os
import logging
from typing import Optional, Tuple
from dotenv import load_dotenv
from email_utils import buscar_y_leer_correo
from src.config import NON_DUPLICATES_TEMPLATE, TEMPLATES_DIR
import os

# --- Configuración de Logging ---
log_format = '%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
logging.basicConfig(level=logging.INFO, format=log_format)

# --- Carga de Variables de Entorno ---
load_dotenv()


def validacion_contenido(archivo_a_validar):
    try:
        template_path = os.path.join(TEMPLATES_DIR, NON_DUPLICATES_TEMPLATE)
        with open(template_path, "r", encoding="utf-8") as f:
            noduplicados = f.read()
    except FileNotFoundError:
        logging.info(f"no se encontro el archivo {template_path}")
        noduplicados = ""

    if noduplicados == archivo_a_validar:
        hay_duplicados = False
    else:
        hay_duplicados = True

    if hay_duplicados:
        mensaje = "Há registros duplicados."
        logging.info(f"mensaje '{mensaje}'")
        logging.info(f"contenido '{archivo_a_validar}'")
        insertar_contenido(mensaje=mensaje, archivo_a_validar=archivo_a_validar)
    else:
        mensaje = "Há há registros duplicados."
        insertar_contenido(mensaje=mensaje)

def insertar_contenido(mensaje: str, archivo_a_validar: Optional[str] = None):
    try:
        plantilla = 'plantilla.html'
        plantilla_a_enviar = 'plantilla_send.html'
        shutil.copy(plantilla, plantilla_a_enviar)
        print(f"¡Éxito! El archivo '{plantilla}' ha sido duplicado como '{plantilla_a_enviar}'.")
    except FileNotFoundError:
        print(f"Error: El archivo '{plantilla}' no fue encontrado.")
        return
    except Exception as e:
        print(f"Ocurrió un error: {e}")
        return

    with open(plantilla_a_enviar, 'r', encoding='utf-8') as file:
        contenido_plantilla = file.read()
    
    contenido_final = contenido_plantilla.replace('MENSAJE_DUPLICADOS', mensaje)
    
    with open(plantilla_a_enviar, 'w', encoding='utf-8') as fi:
        fi.write(contenido_final)
        
    if archivo_a_validar:
        with open(plantilla_a_enviar, "r", encoding="utf-8") as f:
            lineas = f.readlines()

        lineas.insert(15, ' ' * 8 + archivo_a_validar + '\n')

        with open(plantilla_a_enviar, "w", encoding="utf-8") as f:
            f.writelines(lineas)
        logging.info("Contenido insertado en plantilla_a_enviar.html")

def buscar_correo_duplicados():
    """Busca correos con el asunto 'Nuevos duplicados'."""
    logging.info("Iniciando búsqueda de correos de duplicados.")
    asunto = "Nuevos duplicados"
    patron = "Generacion*.html"
    
    cuerpo, adjunto = buscar_y_leer_correo(asunto_buscado=asunto, patron_adjunto=patron)
    
    if adjunto:
        try:
            contenido_adjunto_str = adjunto.decode('utf-8', errors='ignore')
            logging.info(f"Contenido adjunto decodificado: '{contenido_adjunto_str}'")
            
            with open("contenidodescargadoduplicados.html", "w", encoding="utf-8") as f:
                f.write(contenido_adjunto_str)
            logging.info("Contenido adjunto guardado en contenidodescargadoduplicados.html")

            validacion_contenido(contenido_adjunto_str)

        except Exception as e:
            logging.error(f"No se pudo procesar o guardar el archivo adjunto: {e}")

if __name__ == "__main__":
    buscar_correo_duplicados()
