import os
import jsonref # Una biblioteca para cargar archivos JSON que pueden contener referencias internas.
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
# Importa clases para definir herramientas basadas en una especificación OpenAPI.
from azure.ai.projects.models import OpenApiTool, OpenApiAnonymousAuthDetails
from dotenv import load_dotenv

# Carga las variables de entorno.
load_dotenv()
project_connection_string = os.getenv("PROJECT_CONNECTION_STRING")
model=os.getenv("MODEL_DEPLOYMENT_NAME")

# Crea el cliente principal para interactuar con el proyecto de IA de Azure.
project_client = AIProjectClient.from_connection_string(
    credential=DefaultAzureCredential(),
    conn_str=project_connection_string,
)
# [INICIO create_agent_with_openapi]

# Abre y lee el archivo de especificación OpenAPI.
# Este archivo describe cómo funciona la API de clima: qué endpoints tiene, qué parámetros acepta, etc.
current_dir = os.path.dirname(os.path.abspath(__file__))
json_path = os.path.join(current_dir, "weather_openapi.json")
with open(json_path, "r") as f:
    openapi_spec = jsonref.loads(f.read())

# Crea un objeto de autenticación para la herramienta OpenAPI.
# En este caso, 'Anonymous' significa que la API no requiere una clave de autenticación.
auth = OpenApiAnonymousAuthDetails()

# Inicializa la herramienta OpenAPI del agente usando la especificación que leímos del archivo.
openapi = OpenApiTool(
    name="get_weather", 
    spec=openapi_spec, 
    description="Recupera información del clima para una ubicación", # Descripción para que el agente entienda para qué sirve la herramienta.
    auth=auth
)

# El bloque 'with' asegura que el cliente se cierre correctamente al finalizar.
with project_client:
    # Crea un agente y le proporciona la herramienta OpenAPI.
    agent = project_client.agents.create_agent(
        model=model,
        name="openapi-function-assistant",
        instructions="Eres un asistente útil",
        tools=openapi.definitions, # Asigna la herramienta definida por el archivo OpenAPI al agente.
    )

    # [FIN create_agent_with_openapi]

    print(f"Agente creado, ID: {agent.id}")

    # Crea un hilo de conversación para la comunicación.
    thread = project_client.agents.create_thread()
    print(f"Hilo creado, ID: {thread.id}")

    # Crea y añade un mensaje del usuario al hilo.
    message = project_client.agents.create_message(
        thread_id=thread.id,
        role="user",
        content="¿Cuál es el clima y la humedad en Guayaquil?",
    )
    print(f"Mensaje creado, ID: {message.id}")

    # Inicia y procesa una ejecución del agente.
    # El agente interpretará la pregunta, entenderá que necesita usar su herramienta 'get_weather',
    # realizará la llamada a la API externa como se describe en el archivo JSON, y usará la respuesta
    # de la API para construir su respuesta final al usuario.
    run = project_client.agents.create_and_process_run(thread_id=thread.id, assistant_id=agent.id)
    print(f"Ejecución finalizada con estado: {run.status}")

    # Manejo de errores.
    if run.status == "failed":
        print(f"La ejecución falló: {run.last_error}")

    # Obtiene todos los mensajes del hilo.
    messages = project_client.agents.list_messages(thread_id=thread.id)
    print(f"Mensajes: {messages}")
    print("\n")
    
    # Imprime la respuesta del asistente.
    print(f"Respuesta del Asistente: {messages.data[0].content[0].text.value}")