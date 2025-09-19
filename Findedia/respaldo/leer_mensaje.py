import re
import os

def analizar_log_de_chat(file_path, search_terms):
    """
    Analiza un archivo de log de chat para encontrar menciones de actividades
    y extraer el tiempo invertido.

    Args:
        file_path (str): La ruta al archivo de log.
        search_terms (dict): Un diccionario con listas de palabras clave.
            Ejemplo: {
                'activity': ['UAT'],
                'time_question': ['cuantas horas'],
                'time_mention': ['hora', 'horas']
            }
    """
    if not os.path.exists(file_path):
        print(f"Error: El archivo '{file_path}' no fue encontrado.")
        return

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Dividir el chat en mensajes individuales
    messages = content.split('--------------------')
    
    # Procesar para limpiar y estructurar los mensajes
    processed_messages = []
    for msg_block in messages:
        msg_block = msg_block.strip()
        if not msg_block:
            continue
        
        match = re.match(r'\[(.*?)\]\s*Desconocido:\r?\n(.*)', msg_block, re.DOTALL)
        if match:
            timestamp, text = match.groups()
            processed_messages.append({
                'timestamp': timestamp.split('T')[0],
                'full_text': text.strip()
            })

    print(f"Analizando {len(processed_messages)} mensajes...\n")

    # Regex para encontrar números (potenciales horas)
    hours_pattern_direct = re.compile(r'(\d+)\s*(?:' + '|'.join(search_terms['time_mention']) + ')', re.IGNORECASE)
    hours_pattern_answer = re.compile(r'\b(\d+)\b')

    results = []

    for i, msg_data in enumerate(processed_messages):
        text = msg_data['full_text'].lower()
        
        # 1. Buscar menciones directas de horas
        if any(activity.lower() in text for activity in search_terms['activity']):
            match = hours_pattern_direct.search(text)
            if match:
                results.append({
                    'Horas': match.group(1),
                    'Fecha': msg_data['timestamp'],
                    'Actividad': 'Mención directa en mensaje',
                    'Mensaje': msg_data['full_text'],
                    'Contexto': ''
                })
                continue

        # 2. Buscar preguntas sobre horas y sus respuestas
        if any(activity.lower() in text for activity in search_terms['activity']) and any(question.lower() in text for question in search_terms['time_question']):
            
            # Buscar en los siguientes 5 mensajes una respuesta
            for j in range(i + 1, min(i + 6, len(processed_messages))):
                next_msg_text = processed_messages[j]['full_text']
                answer_match = hours_pattern_answer.search(next_msg_text)
                
                # Simple heuristic: if the message is short and contains a number, it's likely an answer.
                if answer_match and len(next_msg_text.split()) < 5:
                    results.append({
                        'Horas': answer_match.group(1),
                        'Fecha': msg_data['timestamp'],
                        'Actividad': 'Pregunta y respuesta',
                        'Mensaje': msg_data['full_text'],
                        'Contexto': f"Respuesta: {next_msg_text}"
                    })
                    break

    # Imprimir resultados
    if not results:
        print("No se encontraron resultados para los términos de búsqueda.")
        return

    for res in results:
        print(f"*   Horas: {res['Horas']}")
        print(f"    Fecha: {res['Fecha']}")
        print(f"    Actividad: {res['Actividad']}")
        print(f"    Mensaje: {res['Mensaje']}")
        if res['Contexto']:
            print(f"    Contexto: {res['Contexto']}")
        print("\n")


if __name__ == '__main__':
    # --- CONFIGURACIÓN ---
    # Modifica estas listas para cambiar lo que buscas.
    # Puedes agregar más palabras clave a cada lista.
    terminos_de_busqueda = {
        'activity': ['UAT','uat'],
        'time_question': ['cuantas horas','hora','cuanto','tiempo'],
        'time_mention': ['hora', 'horas']
    }

    # El script asume que el archivo de log está en el mismo directorio.
    # Cambia la ruta si es necesario.
    archivo_log = 'mensajes_chat_agosto.txt'
    # -------------------

    analizar_log_de_chat(archivo_log, terminos_de_busqueda)