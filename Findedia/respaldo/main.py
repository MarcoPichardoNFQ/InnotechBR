import shutil
import logging
from buscarduplicados import buscar_correo_duplicados

# --- Configuración de Logging ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Nombre que tendrá el nuevo archivo duplicado

if __name__ == "__main__":
	logging.info("Iniciando proceso principal.")
	buscar_correo_duplicados()
	#insertar_contenido()
 
	logging.info("Proceso principal finalizado.")