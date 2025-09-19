import shutil
import os
import logging
from typing import Optional, Tuple
from dotenv import load_dotenv
from email_utils import buscar_y_leer_correo

# --- Configuración de Logging ---
log_format = '%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
logging.basicConfig(level=logging.INFO, format=log_format)

# --- Carga de Variables de Entorno ---
load_dotenv()
def buscar_correo_paquetes():
	"""Busca correos con el asunto 'Nuevos duplicados'."""
	logging.info("Iniciando búsqueda de correos de duplicados.")
	asunto = "PacotesEncolados"
	patron = "paquetes*.html"
	
	cuerpo, adjunto = buscar_y_leer_correo(asunto_buscado=asunto, patron_adjunto=patron)
	
	if adjunto:
		try:
			contenido_adjunto_str = adjunto.decode('utf-8', errors='ignore')
			
			logging.info(f"Contenido adjunto decodificado: '{contenido_adjunto_str}'")
			
			with open("contenidopacotesencolados.html", "w", encoding="utf-8") as f:
				f.write(contenido_adjunto_str)
			logging.info("Contenido adjunto guardado en contenidodescargadoduplicados.html")



		except Exception as e:
			logging.error(f"No se pudo procesar o guardar el archivo adjunto: {e}")
		plantilla_a_enviar = 'plantilla_send.html'
		try:
			with open(plantilla_a_enviar, 'r', encoding='utf-8') as file:
				contenido_plantilla = file.read()
		except FileNotFoundError:
			print(f"Error: El archivo '{plantilla_a_enviar}' no fue encontrado.")
			return
		contenido_final = contenido_plantilla.replace('MENSAJE_ENCOLADOS', contenido_adjunto_str)
    
		with open(plantilla_a_enviar, 'w', encoding='utf-8') as fi:
			fi.write(contenido_final)
	    
	
if __name__ == "__main__":
	buscar_correo_paquetes()
