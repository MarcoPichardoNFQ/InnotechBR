import logging
import json

def analyze_timings(attachment_content_str: str) -> dict:
    """
    Procesa el contenido de un adjunto de tiempos, extrae el JSON y devuelve 
    las 3 ejecuciones más rápidas y las 3 más lentas.

    Args:
        attachment_content_str: El contenido del archivo adjunto como una cadena.

    Returns:
        Un diccionario con las listas 'fastest' y 'slowest', o un diccionario vacío si falla.
    """
    try:
        # El adjunto es un HTML que contiene un JSON. Lo extraemos.
        json_start = attachment_content_str.find('{')
        json_end = attachment_content_str.rfind('}') + 1
        
        if json_start == -1 or json_end == 0:
            logging.warning("No se encontró un objeto JSON en el contenido del adjunto de tiempos.")
            return {}

        json_data_str = attachment_content_str[json_start:json_end]
        data = json.loads(json_data_str)
        ejecuciones = data.get("ejecuciones", [])
        
        if not ejecuciones:
            logging.info("No se encontraron ejecuciones en el JSON de tiempos.")
            return {}

        # Ordenar ejecuciones por duración
        ejecuciones_ordenadas = sorted(ejecuciones, key=lambda x: x.get('duracion_segundos', 0))
        
        mas_rapidas = ejecuciones_ordenadas[:3]
        mas_lentas = ejecuciones_ordenadas[-3:]
        mas_lentas.reverse()  # Mostrar la más lenta primero
        
        logging.info(f"Análisis de tiempos completado. Se encontraron {len(mas_rapidas)} ejecuciones rápidas y {len(mas_lentas)} lentas.")
        
        return {
            "fastest": mas_rapidas,
            "slowest": mas_lentas
        }

    except json.JSONDecodeError:
        logging.error("El contenido extraído del adjunto de tiempos no es un JSON válido.")
        return {}
    except Exception as e:
        logging.error(f"Error al procesar los datos de tiempos: {e}")
        return {}
