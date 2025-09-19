import shutil
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

# --- Configuración de Logging --- que tambien muestra linea ejecutada

log_format = '%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'

logging.basicConfig(
	level=logging.INFO,
	format=log_format
)


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

def validacion_contenido(archivo_a_validar):
	try:
		with open("noduplicados.html", "r", encoding="utf-8") as f:
			noduplicados = f.read()
			noduplicados = str(noduplicados)
	except FileNotFoundError:
		logging.info("no se encontro el archivo noduplicados.html")
	if noduplicados != archivo_a_validar:
		hay_duplicados = True
	else:
		hay_duplicados = False
	if hay_duplicados:
		mensaje = "Há registros duplicados."
		logging.info(f"contenido '{archivo_a_validar}'")
		insertar_contenido(mensaje=mensaje,archivo_a_validar=archivo_a_validar)
	else:
		mensaje = "Não há registros duplicados."
		insertar_contenido(mensaje=mensaje)

def insertar_contenido(mensaje :str,archivo_a_validar: Optional[str] = None)-> Tuple[Optional[str], Optional[bytes]]:
	try:
		plantilla = 'plantilla.html'

# Nombre que tendrá el nuevo archivo duplicado
		plantilla_a_enviar = 'plantilla_send.html'
		shutil.copy(plantilla, plantilla_a_enviar)
		print(f"¡Éxito! El archivo '{plantilla}' ha sido duplicado como '{plantilla_a_enviar}'.")
	except FileNotFoundError:
		print(f"Error: El archivo '{plantilla}' no fue encontrado.")
	except Exception as e:
		print(f"Ocurrió un error: {e}")
# Leer la plantilla
	with open(plantilla_a_enviar, 'r', encoding='utf-8') as file:
		contenido_plantilla = file.read()
	
	# Reemplazar el marcador de posición
	contenido_final = contenido_plantilla.replace('MENSAJE_DUPLICADOS', mensaje)
	# Guardar el resultado en un nuevo archivo
	with open(plantilla_a_enviar, 'w', encoding='utf-8') as fi:
		fi.write(contenido_final)
		
	try:
		with open("contenidodescargadoduplicados.html", "r", encoding="utf-8") as f:
			contenido_insertar = f.read()
	except FileNotFoundError:
		logging.warning("El archivo contenidodescargadoduplicados.html no fue encontrado. Puede que no hubiera adjunto.")
		contenido_insertar = ""

	with open(plantilla_a_enviar, "r", encoding="utf-8") as f:
		lineas = f.readlines()

	# Insertar con indentación
	lineas.insert(15, ' ' * 8 + contenido_insertar + '\n')

	with open(plantilla_a_enviar, "w", encoding="utf-8") as f:
		f.writelines(lineas)
	logging.info("Contenido insertado en plantilla_a_enviar.html")

	
	

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
					logging.info(f"Nombre del archivo adjunto en el correo: {nombre_archivo_adjunto_en_correo}")
					logging.info(f"Nombre del archivo adjunto a buscar: {nombre_archivo_adjunto}")
					logging.info(f"Archivo adjunto '{nombre_archivo_adjunto}' encontrado.")
					contenido_adjunto = part.get_payload(decode=True)
					# Podemos detener la búsqueda si ya encontramos lo que buscábamos

			#if cuerpo_encontrado:
				#logging.info("\nCuerpo del mensaje:\n" + cuerpo_encontrado)
			if contenido_adjunto:
				logging.info(f"Contenido del archivo adjunto '{contenido_adjunto}' extraído.")
				with open("noduplicados.html", "r", encoding="utf-8") as f:
					contenido_vacio= f.read()
				
				#if contenido_adjunto == contenido_vacio:
	
			return cuerpo_encontrado, contenido_adjunto
			
	except Exception as e:
		logging.error(f"Error al leer el correo: {e}")
		return None, None
	finally:
		if mail:
			mail.logout()
			logging.info("Sesión IMAP cerrada.")

def buscar_correo_duplicados():
	"""Busca correos con el asunto 'Nuevos duplicados'."""
	logging.info("Iniciando búsqueda de correos de duplicados.")
	#adjunto sera una expresion regular pues buscamos algo que su nombre empiece con "Generacion"
	adjunto = "Generacion*.txt"
	cuerpo, adjunto = buscar_y_leer_correo(asunto_buscado="Nuevos duplicados",nombre_archivo_adjunto="Generacion*.txt")
	contenido_adjunto =adjunto
	if contenido_adjunto:
		if isinstance(contenido_adjunto, bytes):
			logging.info("Contenido adjunto es de tipo bytes.")
			contenido_adjunto_str = contenido_adjunto.decode('utf-8', errors='ignore')
			logging.info(f"Contenido adjunto es de tipo str.'{contenido_adjunto_str}'")
			validacion_contenido(contenido_adjunto_str)
		else:
			logging.info(f"Contenido adjunto es de tipo str.'{contenido_adjunto}'")
			contenido_adjunto_str = str(contenido_adjunto)
			logging.info(f"Contenido adjunto es de tipo str.'{contenido_adjunto_str}'")
		with open("contenidodescargadoduplicados.html", "w", encoding="utf-8") as f:
			f.write(contenido_adjunto_str)
		logging.info("Contenido adjunto guardado en contenidodescargadoduplicados.html")
