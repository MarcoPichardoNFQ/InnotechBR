import logging
from jinja2 import Environment, FileSystemLoader
from src import config

# Configura el entorno de Jinja2 para que cargue plantillas desde la carpeta 'templates'
env = Environment(loader=FileSystemLoader(config.TEMPLATES_DIR))

def generate_timings_table(timings_data):
    """Renderiza la tabla de tiempos (más rápidos y más lentos)."""
    try:
        template = env.get_template(config.TIMINGS_TEMPLATE)
        return template.render(mas_lentas=timings_data.get('slowest', []), mas_rapidas=timings_data.get('fastest', []))
    except Exception as e:
        logging.error(f"Error al renderizar la plantilla de tiempos: {e}")
        return "<p>Error al generar la tabla de tiempos.</p>"

def generate_final_report(report_context):
    """
    Renderiza el correo electrónico completo usando la plantilla base y el contexto.

    Args:
        report_context (dict): Un diccionario con todos los datos para la plantilla.
                               Ej: {'duplicates_data': ..., 'timings_html': ..., 'queued_data': ...}

    Returns:
        str: El cuerpo del correo en formato HTML.
    """
    logging.info("Generando reporte HTML final...")
    try:
        template = env.get_template(config.BASE_TEMPLATE)
        template_modificado =  template.render(report_context)
        logging.info("Reporte HTML final generado exitosamente.")
        return template.render(report_context)
    except Exception as e:
        logging.error(f"Error al renderizar la plantilla base: {e}")
        # Devuelve un HTML de error para que el proceso no falle silenciosamente
        return f"<h1>Error Crítico</h1><p>No se pudo generar el reporte: {e}</p>"
