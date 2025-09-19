import logging
import re

def analyze_duplicates(attachment_content_str: str, comparison_file_path: str) -> dict:
    """
    Compara el contenido de un adjunto con un archivo local para detectar duplicados.

    Args:
        attachment_content_str: Contenido del adjunto del correo.
        comparison_file_path: Ruta al archivo local para la comparación (ej. 'non_duplicates.html').

    Returns:
        Un diccionario con el resultado del análisis.
    """
    try:
        with open(comparison_file_path, "r", encoding="utf-8") as f:
            contenido_sin_duplicados = f.read()
    except FileNotFoundError:
        logging.warning(f"El archivo de comparación '{comparison_file_path}' no fue encontrado. Asumiendo que no hay duplicados.")
        contenido_sin_duplicados = ""

    # Crear versiones de los contenidos sin espacios ni saltos de línea solo para la comparación
    compare_local = re.sub(r'\s+', '', contenido_sin_duplicados)
    compare_attachment = re.sub(r'\s+', '', attachment_content_str)

    # La lógica original era comparar si el contenido nuevo era IGUAL al que no tenía duplicados.
    # Si son diferentes, significa que hay nuevos duplicados.
    print("Valor compare_local",compare_local)
    print("Valor compare_attachment",compare_attachment)
    if compare_local != compare_attachment:
        logging.info("Se encontraron nuevos registros duplicados.")
        return {
            "message": "Há registros duplicados.",
            "content": attachment_content_str
        }
    else:
        logging.info("No se encontraron nuevos registros duplicados.")
        return {
            "message": "Não há registros duplicados.", # Mensaje corregido
            "content": None
        }
