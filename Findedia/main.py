import logging
from buscarduplicados import buscar_correo_duplicados
from leertiempos import procesar_correo_tiempos
from email_utils import enviar_correo
from pacotesencolados import buscar_correo_paquetes


# --- Configuración de Logging ---
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

if __name__ == "__main__":
	logging.info("Iniciando proceso principal.")
	
	logging.info("--- Buscando correos de duplicados ---")
	buscar_correo_duplicados()
	
	logging.info("--- Procesando correos de tiempos ---")
	procesar_correo_tiempos()
	plantilla_a_enviar = 'plantilla_send.html'
	
	logging.info("enviando correo")
	cuerpo_html = "hola"
	logging.info("--- Buscando correos de paquetes encolados ---")
	buscar_correo_paquetes()
	logging.info("--- Enviando correo con archivo adjunto ---")

	enviar_correo(    asunto="Reporte con Archivo Adjunto",cuerpo_html= cuerpo_html,
	destinatarios= ["marco.pichardo@nfq.mx"],    remitente_nombre= "El crack",archivos_adjuntos=[plantilla_a_enviar])
	logging.info("Proceso principal finalizado.")
