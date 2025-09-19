import logging
import re

def analyze_queued(attachment_content_str: str) -> str:
    """
    Analiza el contenido del adjunto de paquetes encolados para encontrar el número máximo de archivos.

    Args:
        attachment_content_str: Contenido del adjunto del correo.

    Returns:
        Un mensaje indicando el estado de los paquetes encolados.
    """
    logging.info("Iniciando análisis de paquetes encolados.")
    
    try:
        # Usar una expresión regular para encontrar todos los números de archivos.
        # El patrón busca el número que está entre "tiene " y " archivos".
        counts_str = re.findall(r"tiene (\d+) archivos", attachment_content_str)
        
        # Si no se encuentra ningún número, puede que el formato del correo haya cambiado.
        if not counts_str:
            logging.warning("No se encontraron conteos de archivos en el correo de paquetes encolados.")
            # Como fallback, si el correo simplemente dice que no hay, usamos ese mensaje.
            if "Nao ha pacotes" in attachment_content_str:
                return "Nao ha Pacotes encolados"
            return "Formato de reporte de encolados no reconocido."

        # Convertir los números encontrados (que son strings) a enteros
        counts = [int(c) for c in counts_str]
        max_count = max(counts)
        
        if max_count > 0:
            message = f"Há {max_count} pacotes pendentes a serem executados."
        else:
            message = "Nao ha Pacotes encolados"
            
        logging.info(f"Análisis de encolados finalizado. Mensaje: '{message}'")
        return message
            
    except Exception as e:
        logging.error(f"Error al analizar el contenido de paquetes encolados: {e}")
        return "Error al procesar el reporte de paquetes encolados."
