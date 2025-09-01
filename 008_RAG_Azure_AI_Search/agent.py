# Importando las bibliotecas y utilidades necesarias.
import os
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
# Importa la clase para la herramienta de Azure AI Search y los tipos de conexión.
from azure.ai.projects.models import AzureAISearchTool, ConnectionType
from dotenv import load_dotenv


# Carga las variables de entorno desde un archivo .env.
load_dotenv()
project_connection_string = os.getenv("PROJECT_CONNECTION_STRING")
model = os.getenv("MODEL_DEPLOYMENT_NAME")
# El nombre del índice específico dentro de tu servicio de Azure AI Search que el agente consultará.
index_name=os.getenv("AI_SEARCH_INDEX_NAME")

# Crea el cliente principal para interactuar con el proyecto de IA de Azure.
project_client = AIProjectClient.from_connection_string(
    credential=DefaultAzureCredential(),
    conn_str=project_connection_string,
)

# [INICIO create_agent_with_azure_ai_search_tool]
# Busca en la lista de conexiones del proyecto para encontrar la que corresponde a Azure AI Search.
conn_list = project_client.connections.list()
conn_id = ""
for conn in conn_list:
    # Comprueba si el tipo de conexión es el de Azure AI Search.
    if conn.connection_type == ConnectionType.AZURE_AI_SEARCH:
        # Guarda el ID de la conexión cuando la encuentra.
        conn_id = conn.id
        break

print(f"ID de la conexión encontrada: {conn_id}")

# Inicializa la herramienta de Azure AI Search.
# Se le pasa el ID de la conexión y el nombre del índice para que sepa dónde buscar.
ai_search = AzureAISearchTool(index_connection_id=conn_id, index_name=index_name)

# El bloque 'with' asegura que el cliente se cierre correctamente al finalizar.
with project_client:
    # Crea un agente y le proporciona la herramienta de Azure AI Search.
    agent = project_client.agents.create_agent(
        model=model,
        name="ai-search-assistant",
        instructions="Eres un asistente útil",
        tools=ai_search.definitions, # Define las capacidades de la herramienta.
        tool_resources=ai_search.resources, # Proporciona los recursos necesarios para que la herramienta funcione (ej. la conexión).
        headers={"x-ms-enable-preview": "true"}, # Cabecera para funcionalidades en vista previa.
    )
    # [FIN create_agent_with_azure_ai_search_tool]
    print(f"Agente creado, ID: {agent.id}")

    # Crea un hilo de conversación para la comunicación.
    thread = project_client.agents.create_thread()
    print(f"Hilo creado, ID: {thread.id}")

    # Crea y añade un mensaje del usuario al hilo.
    message = project_client.agents.create_message(
        thread_id=thread.id,
        role="user",
        content="¿cuáles son los hoteles que ofrece Margie's Travel en Las Vegas?",
    )
    print(f"Mensaje creado, ID: {message.id}")

    # Inicia y procesa una ejecución del agente.
    # El agente usará la herramienta de búsqueda para consultar el índice y encontrar la respuesta.
    run = project_client.agents.create_and_process_run(thread_id=thread.id, assistant_id=agent.id)
    print(f"Ejecución finalizada con estado: {run.status}")

    # Manejo de errores.
    if run.status == "failed":
        print(f"La ejecución falló: {run.last_error}")

    # Elimina el asistente una vez que hemos terminado. Es una buena práctica para limpiar recursos.
    project_client.agents.delete_agent(agent.id)
    print("Agente eliminado")

    # Obtiene todos los mensajes del hilo.
    messages = project_client.agents.list_messages(thread_id=thread.id)
    print(f"Mensajes: {messages}")
    print("\n")
    
    # Imprime la respuesta del asistente, que se basa en los datos encontrados en el índice de búsqueda.
    print(f"Respuesta del Asistente: {messages.data[0].content[0].text.value}")
    print("\n")
    
    # Mostrando la citación de la URL - ¡la citación de URL no funciona muy bien por ahora!
    content = messages['data'][0]['content'][0]
    url_citation = content['text']['annotations'][0]['url_citation']['url']
    print(f"URL de la fuente: {url_citation}")