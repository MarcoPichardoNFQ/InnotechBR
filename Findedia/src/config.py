import os
from dotenv import load_dotenv

# Cargar variables desde el archivo .env
load_dotenv()

# --- Configuración de Email ---
IMAP_HOST = "imap.gmail.com"
IMAP_PORT = 993
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 465

# Es crucial que EMAIL_SENDER y EMAIL_APP_PASSWORD estén en tu archivo .env
EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_APP_PASSWORD")

# --- Configuración de Reportes ---
RECIPIENTS = ["marco.pichardo@nfq.mx"] # Lista de destinatarios
SENDER_NAME = "Reporte Automático"

# --- Tareas de Procesamiento ---
# Cada diccionario contiene la configuración para una tarea específica
TASKS = {
    "duplicates": {
        "subject": "Nuevos duplicados",
        "attachment_pattern": "Generacion*.html",
        "local_comparison_file": "non_duplicates.html"
    },
    "timings": {
        "subject": "DuracionesDia",
        "attachment_pattern": "DuracionesDia*.html",
        "output_json_file": "duraciones_dia.json" # Archivo intermedio
    },
    "queued": {
        "subject": "PacotesEncolados",
        "attachment_pattern": "paquetes*.html"
    }
}

# --- Configuración de Plantillas ---
TEMPLATES_DIR = "templates"
BASE_TEMPLATE = "base_email.html"
TIMINGS_TEMPLATE = "timings_report.html"
NON_DUPLICATES_TEMPLATE = "non_duplicates.html"

# --- Configuración de Logging ---
LOG_FORMAT = '%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
LOG_LEVEL = "INFO"
