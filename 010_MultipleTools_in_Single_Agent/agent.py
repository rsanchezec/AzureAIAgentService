# Importando las bibliotecas y utilidades necesarias.
import os
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
# Importa las clases para manejar herramientas de función, conjuntos de herramientas y la herramienta de Bing.
from azure.ai.projects.models import FunctionTool, ToolSet
from .functions import user_functions # Importa tus funciones personalizadas (ej. get_user_info).
from dotenv import load_dotenv
from azure.ai.projects.models import BingGroundingTool

# Carga las variables de entorno.
load_dotenv()
model = os.getenv("MODEL_DEPLOYMENT_NAME")
project_connection_string = os.getenv("PROJECT_CONNECTION_STRING")

# Crea el cliente principal para interactuar con el proyecto de IA de Azure.
project_client = AIProjectClient.from_connection_string(
    credential=DefaultAzureCredential(),
    conn_str=project_connection_string,
)

# --- Configuración de la herramienta de Búsqueda de Bing ---
bing_connection_name=os.getenv("BING_CONNECTION_NAME")
bing_connection = project_client.connections.get(connection_name=bing_connection_name)
conn_id = bing_connection.id
# Inicializa el objeto de la herramienta de Bing.
bing = BingGroundingTool(connection_id=conn_id)

# El bloque 'with' asegura que el cliente se cierre correctamente al finalizar.
with project_client:
    # --- Creación del Conjunto de Herramientas (Toolset) ---
    # [INICIO create_agent_toolset]
    # 1. Prepara las funciones personalizadas.
    functions = FunctionTool(user_functions)
    
    # 2. Crea un "conjunto de herramientas" para agrupar todas las capacidades del agente.
    toolset = ToolSet()
    # 3. Añade tus funciones personalizadas al conjunto.
    toolset.add(functions)
    # 4. Añade la herramienta de Búsqueda de Bing al MISMO conjunto.
    toolset.add(bing)
    
    # Crea un agente y le asigna el conjunto de herramientas combinado.
    # Ahora el agente puede tanto buscar usuarios como navegar por internet.
    agent = project_client.agents.create_agent(
        model=model,
        name="multiple-tools-assistant",
        instructions="Eres un asistente útil",
        toolset=toolset, # Asigna el conjunto de herramientas con múltiples capacidades.
    )
    # [FIN create_agent_toolset]
    print(f"Agente creado, ID: {agent.id}")

    # Crea un hilo de conversación.
    thread = project_client.agents.create_thread()
    print(f"Hilo creado, ID: {thread.id}")

    # Crea un mensaje de usuario que requiere el uso de AMBAS herramientas.
    message = project_client.agents.create_message(
        thread_id=thread.id,
        role="user",
        content="¿cuáles son los detalles del usuario con id 1 y realiza una búsqueda en internet sobre el nombre asociado a ese id de usuario?",
    )
    print(f"Mensaje creado, ID: {message.id}")

    # Inicia y procesa la ejecución.
    # El agente seguirá estos pasos:
    # 1. Entenderá que primero debe buscar al usuario con ID 1, llamando a la función 'get_user_info'.
    # 2. Usará el nombre obtenido ("Alice") de esa función como término de búsqueda para la segunda herramienta (Bing).
    # 3. Sintetizará los resultados de ambas acciones en una respuesta final.
    # [INICIO create_and_process_run]
    run = project_client.agents.create_and_process_run(thread_id=thread.id, assistant_id=agent.id)
    # [FIN create_and_process_run]
    print(f"Ejecución finalizada con estado: {run.status}")

    # Manejo de errores.
    if run.status == "failed":
        print(f"La ejecución falló: {run.last_error}")

    # Obtiene todos los mensajes del hilo.
    messages = project_client.agents.list_messages(thread_id=thread.id)
    print(f"Mensajes: {messages}")
    print("\n")
    
    # Imprimiendo la respuesta final del asistente.
    print(f"Respuesta del Asistente: {messages.data[0].content[0].text.value}")