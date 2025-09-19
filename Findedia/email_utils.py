import os
import logging
import imaplib
import email
import fnmatch
import smtplib
from email.message import EmailMessage
from email.utils import formataddr
from pathlib import Path
from typing import Optional, Tuple, List
from dotenv import load_dotenv

load_dotenv()

# --- Constantes de Configuración ---
IMAP_HOST = "imap.gmail.com"
IMAP_PORT = 993
EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_APP_PASSWORD")
SENDER_NAME = "Equipo de Desarrollo"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 465

def buscar_y_leer_correo(asunto_buscado: str, patron_adjunto: str) -> Tuple[Optional[str], Optional[bytes]]:
    """
    Busca el correo más reciente con un asunto específico, encuentra un adjunto que coincida
    con un patrón y devuelve el cuerpo del correo y el contenido del adjunto.

    Args:
        asunto_buscado (str): El asunto del correo a buscar.
        patron_adjunto (str): El patrón de nombre de archivo para el adjunto (ej. "DuracionesDia*.html").

    Returns:
        Tuple[Optional[str], Optional[bytes]]: Una tupla con el cuerpo del correo y el contenido del adjunto.
    """
    if not all([EMAIL_SENDER, EMAIL_PASSWORD]):
        logging.error("Faltan credenciales de correo. Asegúrate de configurar el archivo .env.")
        return None, None

    mail = None
    try:
        logging.info("Conectando al servidor IMAP...")
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
        
        id_correo = ids_mensajes[-1]  # Obtiene el último (más reciente)
        
        logging.info("Correo encontrado. Recuperando contenido...")
        status, data = mail.fetch(id_correo, "(RFC822)")
        
        raw_email = data[0][1]
        email_message = email.message_from_bytes(raw_email)
        
        cuerpo_encontrado = ""
        contenido_adjunto = None

        for part in email_message.walk():
            disposition = str(part.get_content_disposition())
            
            if "attachment" in disposition:
                nombre_archivo = part.get_filename()
                if nombre_archivo and fnmatch.fnmatch(nombre_archivo, patron_adjunto):
                    logging.info(f"Archivo adjunto '{nombre_archivo}' encontrado y coincide con el patrón.")
                    contenido_adjunto = part.get_payload(decode=True)
                    break # Detener después de encontrar el adjunto correcto

            elif part.get_content_type() == "text/html" and "attachment" not in disposition:
                cuerpo_encontrado = part.get_payload(decode=True).decode()
            elif part.get_content_type() == "text/plain" and "attachment" not in disposition and not cuerpo_encontrado:
                cuerpo_encontrado = part.get_payload(decode=True).decode()

        if contenido_adjunto:
            logging.info(f"Contenido del archivo adjunto extraído.")
        else:
            logging.warning(f"No se encontró ningún archivo adjunto que coincida con el patrón '{patron_adjunto}'.")

        return cuerpo_encontrado, contenido_adjunto
            
    except Exception as e:
        logging.error(f"Error al leer el correo: {e}")
        return None, None
    finally:
        if mail:
            mail.logout()
            logging.info("Sesión IMAP cerrada.")

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
    logging.info("destinatarios {}".format(destinatarios))
    logging.info("cuerpo_html {}".format(cuerpo_html))
    logging.info("asunto {}".format(asunto))
    logging.info("remitente_nombre {}".format(remitente_nombre))
    logging.info("archivos_adjuntos {}".format(archivos_adjuntos))
    logging.info("cuerpo_html {}".format(cuerpo_html))
    logging.info("")
    msg = EmailMessage()
    msg["Subject"] = asunto
    msg["From"] = formataddr((remitente_nombre, EMAIL_SENDER))
    msg["To"] = ", ".join(destinatarios)
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