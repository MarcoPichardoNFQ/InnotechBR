import smtplib
import os
import logging
import imaplib
import email
from email.message import EmailMessage
from email.utils import formataddr
from pathlib import Path
from dotenv import load_dotenv
from typing import List, Optional, Tuple

# --- Configuración de Logging ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Carga de Variables de Entorno para Seguridad ---
load_dotenv()

# --- Constantes de Configuración ---
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 465
IMAP_HOST = "imap.gmail.com"
IMAP_PORT = 993
EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_APP_PASSWORD")
SENDER_NAME = "Equipo de Desarrollo"

def enviar_correo(
    asunto: str,
    cuerpo_html: str,
    destinatarios: List[str],
    remitente_nombre: str = SENDER_NAME,
    archivos_adjuntos: Optional[List[str]] = None
) -> bool:
    """Envía un correo electrónico de forma robusta y segura."""
    if not all([EMAIL_SENDER, EMAIL_PASSWORD]):
        logging.error("Faltan credenciales de correo. Asegúrate de configurar el archivo .env.")
        return False
    if not destinatarios:
        logging.warning("No se proporcionaron destinatarios.")
        return False
    msg = EmailMessage()
    msg["Subject"] = asunto
    msg["From"] = formataddr((remitente_nombre, EMAIL_SENDER))
    msg["To"] = ", ".join(destinatarios)
    #msg.set_content("Este correo requiere un cliente con capacidad para ver HTML.")
    msg.add_alternative(cuerpo_html, subtype="html")
    if archivos_adjuntos:
        for ruta_archivo in archivos_adjuntos:
            try:
                archivo = Path(ruta_archivo)
                with open(archivo, "rb") as f:
                    msg.add_attachment(
                        f.read(),
                        maintype="application",
                        subtype=archivo.suffix.strip('.'),
                        filename=archivo.name
                    )
            except FileNotFoundError:
                logging.error(f"El archivo adjunto no se encontró en la ruta: {ruta_archivo}")
                continue
            except Exception as e:
                logging.error(f"Error al adjuntar el archivo {ruta_archivo}: {e}")
                return False
    try:
        with smtplib.SMTP_SSL(EMAIL_HOST, EMAIL_PORT) as smtp:
            logging.info("Conectando al servidor SMTP...")
            smtp.login(EMAIL_SENDER, EMAIL_PASSWORD)
            logging.info(f"Enviando correo a: {', '.join(destinatarios)}")
            smtp.send_message(msg)
            logging.info("Correo enviado con éxito.")
            return True
    except smtplib.SMTPAuthenticationError:
        logging.error("Error de autenticación. Revisa tu email y contraseña de aplicación.")
    except smtplib.SMTPConnectError:
        logging.error(f"No se pudo conectar al servidor {EMAIL_HOST}:{EMAIL_PORT}.")
    except Exception as e:
        logging.error(f"Ocurrió un error inesperado al enviar el correo: {e}")
    return False

# --- Nueva función para buscar y leer correos ---
def buscar_y_leer_correo(asunto_buscado: str, nombre_archivo_adjunto: Optional[str] = None) -> Tuple[Optional[str], Optional[bytes]]:
    """
    Busca el correo más reciente con un asunto específico y devuelve su cuerpo y el contenido del adjunto.

    Args:
        asunto_buscado (str): El asunto del correo a buscar.
        nombre_archivo_adjunto (Optional[str]): El nombre del archivo adjunto a leer.

    Returns:
        Tuple[Optional[str], Optional[bytes]]: Una tupla con el cuerpo del correo y el contenido del adjunto.
    """
    if not all([EMAIL_SENDER, EMAIL_PASSWORD]):
        logging.error("Faltan credenciales de correo para la búsqueda. Asegúrate de configurar el archivo .env.")
        return None, None

    mail = None
    try:
        logging.info("Conectando al servidor IMAP para la búsqueda...")
        mail = imaplib.IMAP4_SSL(IMAP_HOST, IMAP_PORT)
        mail.login(EMAIL_SENDER, EMAIL_PASSWORD)
        
        logging.info("Seleccionando la bandeja de entrada...")
        mail.select("inbox")
        
        logging.info(f"Buscando correos con asunto: '{asunto_buscado}'")
        status, mensajes = mail.search(None, f'(SUBJECT "{asunto_buscado}")')
        
        ids_mensajes = mensajes[0].split()
        
        if not ids_mensajes:
            logging.info("No se encontraron correos con ese asunto.")
            return None, None
        else:
            id_correo = ids_mensajes[-1] # Obtiene el último (más reciente)
            
            logging.info("Correo encontrado. Recuperando contenido...")
            status, data = mail.fetch(id_correo, "(RFC822)")
            
            raw_email = data[0][1]
            email_message = email.message_from_bytes(raw_email)
            
            logging.info("-" * 50)
            logging.info("Contenido del correo:")
            logging.info(f"De: {email_message['From']}")
            logging.info(f"Asunto: {email_message['Subject']}")
            
            cuerpo_encontrado = ""
            contenido_adjunto = None

            for part in email_message.walk():
                content_type = part.get_content_type()
                disposition = str(part.get_content_disposition())

                # Lógica para leer el cuerpo (texto o HTML)
                if content_type == "text/html" and "attachment" not in disposition:
                    cuerpo_encontrado = part.get_payload(decode=True).decode()
                elif content_type == "text/plain" and "attachment" not in disposition and not cuerpo_encontrado:
                    cuerpo_encontrado = part.get_payload(decode=True).decode()
                
                # --- NUEVA LÓGICA PARA ARCHIVOS ADJUNTOS ---
                if nombre_archivo_adjunto and "attachment" in disposition:
                    nombre_archivo_adjunto_en_correo = part.get_filename()
                    if nombre_archivo_adjunto_en_correo == nombre_archivo_adjunto:
                        logging.info(f"Archivo adjunto '{nombre_archivo_adjunto}' encontrado.")
                        contenido_adjunto = part.get_payload(decode=True)
                        # Podemos detener la búsqueda si ya encontramos lo que buscábamos
                        break

            if cuerpo_encontrado:
                logging.info("\nCuerpo del mensaje:\n" + cuerpo_encontrado)
            if contenido_adjunto:
                logging.info(f"Contenido del archivo adjunto '{nombre_archivo_adjunto}' extraído.")
            
            logging.info("-" * 50)
            return cuerpo_encontrado, contenido_adjunto
            
    except Exception as e:
        logging.error(f"Error al leer el correo: {e}")
        return None, None
    finally:
        if mail:
            mail.logout()
            logging.info("Sesión IMAP cerrada.")

# --- Bloque de Ejecución Principal ---
if __name__ == "__main__":
    # --- Ejemplo de uso de la función de envío ---
    destinatarios_prueba = ["marco.pichardo@nfq.mx"]
    asunto_prueba = "Reporte con Archivo Adjunto"
    cuerpo_prueba_html = "<html><body><p>Hola, aquí está el reporte en el archivo adjunto.</p></body></html>"
    
    with open("reporte.txt", "w") as f:
        f.write("Este es el contenido del reporte de prueba.")
    
    archivos_a_adjuntar = ["reporte.txt"]

    enviar_correo(asunto=asunto_prueba, cuerpo_html=cuerpo_prueba_html, destinatarios=destinatarios_prueba, archivos_adjuntos=archivos_a_adjuntar)
    
    logging.info("=" * 50)

    # --- Ejemplo de uso de la función de lectura de correos y adjuntos ---
    asunto_a_buscar = "Reporte con Archivo Adjunto"
    nombre_adjunto = "reporte.txt"
    
    cuerpo_encontrado, contenido_adjunto = buscar_y_leer_correo(asunto_a_buscar, nombre_adjunto)

    if cuerpo_encontrado:
        logging.info("Cuerpo del correo leído con éxito.")

    if contenido_adjunto:
        # Puedes guardar el archivo o procesar su contenido
        with open("reporte_recibido.txt", "wb") as f:
            f.write(contenido_adjunto)
        logging.info(f"Archivo adjunto '{nombre_adjunto}' guardado como 'reporte_recibido.txt'.")
        
        # También puedes leer el contenido del archivo si es texto
        try:
            contenido_texto = contenido_adjunto.decode("utf-8")
            logging.info("\n--- Contenido del archivo adjunto ---")
            logging.info(contenido_texto)
        except Exception as e:
            logging.warning(f"No se pudo decodificar el contenido del adjunto: {e}")
    else:
        logging.warning("No se pudo leer el correo o el archivo adjunto.")