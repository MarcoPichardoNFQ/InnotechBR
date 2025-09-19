import os
import logging
import json
import shutil
from dotenv import load_dotenv
from email_utils import buscar_y_leer_correo

# --- Configuración de Logging ---
log_format = '%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
logging.basicConfig(level=logging.INFO, format=log_format)

# --- Carga de Variables de Entorno ---
load_dotenv()

def generar_reporte_html(mas_rapidas, mas_lentas):
	try:
		plantilla = 'plantillatoptiempos.html'
		reporte_final = 'reporte_tiempos.html'
		shutil.copy(plantilla, reporte_final)

		with open(reporte_final, 'r', encoding='utf-8') as file:
			contenido_plantilla = file.read()

		# Generar HTML para las ejecuciones más lentas
		html_lentas = ""
		for ej in mas_lentas:
			link = f"https://rundeck.s3caceis.com.br:4443/project/Aldrin-Megara/execution/show/{ej['archivo']}"
			html_lentas += f"<tr><td>{ej['tipo']}</td><td>{ej['estatus']}</td><td><a href='{link}' target='_blank'>Navegar a execução</a></td><td>{ej['hora_de_inicio']}</td><td>{ej['hora_de_fin']}</td><td>{ej['duracion_segundos']}</td></tr>"

		# Generar HTML para las ejecuciones más rápidas
		html_rapidas = ""
		for ej in mas_rapidas:
			link = f"https://rundeck.s3caceis.com.br:4443/project/Aldrin-Megara/execution/show/{ej['archivo']}"
			#mostrar tiempo en formato de minuto y segundos y no solo en segundos
			hora, minutos, segundos = ej['duracion_segundos'] // 3600, (ej['duracion_segundos'] % 3600) // 60, ej['duracion_segundos'] % 60
			tiempo_formateado = f"{hora:02d}:{minutos:02d}:{segundos:02d}"
			html_rapidas += f"<tr><td>{ej['tipo']}</td><td>{ej['estatus']}</td><td><a href='{link}' target='_blank'>Navegar a execução</a></td><td>{ej['hora_de_inicio']}</td><td>{ej['hora_de_fin']}</td><td>{tiempo_formateado}</td></tr>"

		contenido_final = contenido_plantilla.replace('<!-- TOP_3_LENTAS -->', html_lentas)
		contenido_final = contenido_final.replace('<!-- TOP_3_RAPIDAS -->', html_rapidas)

		with open(reporte_final, 'w', encoding='utf-8') as f:
			f.write(contenido_final)
		logging.info(f"Reporte HTML generado en '{reporte_final}'")
		try:
			plantilla_a_enviar = 'plantilla_send.html'
		except FileNotFoundError:
			print(f"Error: El archivo '{plantilla}' no fue encontrado.")
			return
		except Exception as e:
			print(f"Ocurrió un error: {e}")
			return

		with open(plantilla_a_enviar, 'r', encoding='utf-8') as file:
			contenido_plantilla = file.read()
		
		contenido_final_plantilla = contenido_plantilla.replace('MENSAJE_TOPS', contenido_final)
		with open(plantilla_a_enviar, 'w', encoding='utf-8') as fi:
			fi.write(contenido_final_plantilla)
		logging.info("Contenido insertado en plantilla_a_enviar.html")
        
	except Exception as e:
		logging.error(f"Error al generar el reporte HTML: {e}")

def procesar_correo_tiempos():
	"""Busca correos con el asunto 'DuracionesDia' y procesa el adjunto."""
	logging.info("Iniciando búsqueda de correos de duraciones.")
	
	asunto = "DuracionesDia"
	patron = "DuracionesDia*.html"
	
	cuerpo, adjunto = buscar_y_leer_correo(asunto_buscado=asunto, patron_adjunto=patron)
	
	if adjunto:
		nombre_archivo_salida = "duraciones_dia.json"
		try:
			contenido_adjunto_str = adjunto.decode('utf-8', errors='ignore')
			json_start = contenido_adjunto_str.find('{')
			json_end = contenido_adjunto_str.rfind('}') + 1
			json_data_str = contenido_adjunto_str[json_start:json_end]

			with open(nombre_archivo_salida, "w", encoding="utf-8") as f:
				f.write(json_data_str)
			logging.info(f"Contenido adjunto guardado en '{nombre_archivo_salida}'")

			data = json.loads(json_data_str)
			ejecuciones = data.get("ejecuciones", [])
			
			if not ejecuciones:
				logging.info("No se encontraron ejecuciones en el archivo.")
				return

			ejecuciones_ordenadas = sorted(ejecuciones, key=lambda x: x['duracion_segundos'])
			
			mas_rapidas = ejecuciones_ordenadas[:3]
			mas_lentas = ejecuciones_ordenadas[-3:]
			mas_lentas.reverse() # Para mostrar la más lenta primero
			
			generar_reporte_html(mas_rapidas, mas_lentas)
			
		except json.JSONDecodeError:
			logging.error("El contenido del adjunto no es un JSON válido.")
		except Exception as e:
			logging.error(f"No se pudo procesar o guardar el archivo adjunto: {e}")

if __name__ == "__main__":
	procesar_correo_tiempos()
