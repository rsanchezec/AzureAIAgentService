# Importando las bibliotecas necesarias.
import os
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.projects.models import BingGroundingTool # Importa la clase específica para la herramienta de búsqueda de Bing.
from dotenv import load_dotenv

# Carga las variables de entorno desde un archivo .env.
load_dotenv()

# Crea el cliente principal para interactuar con el proyecto de IA de Azure.
project_client = AIProjectClient.from_connection_string(
    credential=DefaultAzureCredential(),
    conn_str=os.getenv("PROJECT_CONNECTION_STRING")
)

# Obtiene el nombre del despliegue del modelo desde las variables de entorno.
model=os.getenv("MODEL_DEPLOYMENT_NAME")

# Obtiene el nombre de la conexión de Bing que ha sido preconfigurada en tu proyecto de Azure AI.
bing_connection_name = os.getenv("BING_CONNECTION_NAME")

# Obtiene el objeto de conexión de Bing usando el cliente del proyecto y el nombre de la conexión.
bing_connection = project_client.connections.get(connection_name=bing_connection_name)
# Extrae el ID de la conexión, que es necesario para inicializar la herramienta.
conn_id = bing_connection.id

# Inicializa la herramienta de búsqueda de Bing (BingGroundingTool) con el ID de la conexión.
bing = BingGroundingTool(connection_id=conn_id)

# El bloque 'with' asegura que el cliente se cierre correctamente al finalizar.
with project_client:
    # Crea un agente (asistente) y le proporciona la herramienta de búsqueda de Bing.
    agent = project_client.agents.create_agent(
        model=model,
        name="bing-assistant", # Un nombre para identificar a este agente.
        instructions="Eres un asistente útil", # Las instrucciones que guían el comportamiento del agente.
        tools=bing.definitions, # Aquí se le asigna la herramienta de Bing al agente para que pueda realizar búsquedas.
        headers={"x-ms-enable-preview": "true"}, # Cabecera necesaria para usar funcionalidades en vista previa.
    )

    print(f"Agente creado, ID: {agent.id}")

    # Crea un hilo de conversación (thread) para la comunicación.
    thread = project_client.agents.create_thread()
    print(f"Hilo creado, ID: {thread.id}")

    # Crea y añade un mensaje del usuario al hilo.
    message = project_client.agents.create_message(
        thread_id=thread.id,
        role="user",
        content="¿cuál es el clima en Guayaquil - Ecuador ahora?", # La pregunta del usuario.
    )
    print(f"Mensaje creado, ID: {message.id}")

    # Inicia y procesa una ejecución del agente en el hilo.
    # Esta función espera a que el agente use sus herramientas (si es necesario) y complete la respuesta.
    run = project_client.agents.create_and_process_run(thread_id=thread.id, assistant_id=agent.id)
    print(f"Ejecución finalizada con estado: {run.status}")

    # Manejo básico de errores por si la ejecución falla.
    if run.status == "failed":
        print(f"La ejecución falló: {run.last_error}")

    # Obtiene todos los mensajes del hilo después de que la ejecución haya finalizado.
    messages = project_client.agents.list_messages(thread_id=thread.id)
    
    # Mostrando la respuesta del asistente.
    # El mensaje más reciente (índice 0) contiene la respuesta de texto del asistente.
    print(messages.data[0].content[0].text.value)
    
    # Mostrando la citación de la URL.
    # La respuesta del agente puede incluir "anotaciones" con las fuentes que utilizó.
    content = messages['data'][0]['content'][0]['text']['annotations']
    # Itera a través de las anotaciones para extraer y mostrar las URLs de las fuentes.
    for annotation in content:
        url_citation = annotation['url_citation']['url']
        print(f"Fuente (URL): {url_citation}")