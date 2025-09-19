import logging
from src import config
from src import email_client
from src.processing import duplicates, timings, queued
from src.reporting import generator

def setup_logging():
    """Configura el logging para todo el proyecto."""
    logging.basicConfig(level=config.LOG_LEVEL, format=config.LOG_FORMAT)

def run_report_process():
    """Orquesta el proceso completo de generación de reportes."""
    logging.info("--- INICIANDO PROCESO DE REPORTES AUTOMÁTICOS ---")

    report_context = {}

    # --- 1. Tarea de Duplicados ---
    logging.info("Iniciando procesamiento de duplicados...")
    task_config = config.TASKS['duplicates']
    _, attachment_bytes = email_client.buscar_y_leer_correo(
        asunto_buscado=task_config['subject'],
        patron_adjunto=task_config['attachment_pattern']
    )
    if attachment_bytes:
        content_str = attachment_bytes.decode('utf-8', errors='ignore')
        duplicates_result = duplicates.analyze_duplicates(
            attachment_content_str=content_str,
            comparison_file_path=task_config['local_comparison_file']
        )
        report_context['duplicates_data'] = duplicates_result
        logging.info("el contenido de duplicados es: {}".format(duplicates_result))
        logging.info("")
        logging.info("Procesamiento de duplicados finalizado.")
    else:
        logging.warning("No se encontró correo de duplicados. Saltando este paso.")
        report_context['duplicates_data'] = {"message": "No se pudo verificar (correo no encontrado).", "content": None}

    # --- 2. Tarea de Tiempos de Ejecución ---
    logging.info("Iniciando procesamiento de tiempos de ejecución...")
    task_config = config.TASKS['timings']
    _, attachment_bytes = email_client.buscar_y_leer_correo(
        asunto_buscado=task_config['subject'],
        patron_adjunto=task_config['attachment_pattern']
    )
    if attachment_bytes:
        content_str = attachment_bytes.decode('utf-8', errors='ignore')
        timings_result = timings.analyze_timings(content_str)
        timings_html = generator.generate_timings_table(timings_result)
        report_context['timings_report_html'] = timings_html
        logging.info("Procesamiento de tiempos finalizado.")
    else:
        logging.warning("No se encontró correo de tiempos. Saltando este paso.")
        report_context['timings_report_html'] = "<p>No se pudo generar el reporte de tiempos (correo no encontrado).</p>"

    # --- 3. Tarea de Paquetes Encolados ---
    logging.info("Iniciando procesamiento de paquetes encolados...")
    task_config = config.TASKS['queued']
    _, attachment_bytes = email_client.buscar_y_leer_correo(
        asunto_buscado=task_config['subject'],
        patron_adjunto=task_config['attachment_pattern']
    )
    if attachment_bytes:
        content_str = attachment_bytes.decode('utf-8', errors='ignore')
        queued_result = queued.analyze_queued(content_str)
        report_context['queued_data'] = queued_result
        logging.info("Procesamiento de paquetes encolados finalizado.")
    else:
        logging.warning("No se encontró correo de paquetes encolados. Saltando este paso.")
        report_context['queued_data'] = "No se pudo verificar (correo no encontrado)."

    # --- 4. Generar y Enviar Reporte Final ---
    logging.info("Generando el cuerpo del correo final...")
    final_html_body = generator.generate_final_report(report_context)

    # Guardar el reporte final para depuración (opcional)
    with open("final_report_debug.html", "w", encoding="utf-8") as f:
        f.write(final_html_body)

    logging.info("Enviando correo final...")
    email_sent = email_client.enviar_correo(
        asunto="Reporte Diario de Status",
        cuerpo_html=final_html_body,
        destinatarios=config.RECIPIENTS,
        remitente_nombre=config.SENDER_NAME
    )

    if email_sent:
        logging.info("Correo final enviado exitosamente.")
    else:
        logging.error("Fallo al enviar el correo final.")

    logging.info("--- PROCESO DE REPORTES FINALIZADO ---")

if __name__ == "__main__":
    setup_logging()
    run_report_process()
