# Importando las bibliotecas necesarias.
import os
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
# Importa clases para definir herramientas que el agente puede usar.
from azure.ai.projects.models import FunctionTool, ToolSet
# Importa las funciones personalizadas que hemos definido en otro archivo (functions.py).
from .functions import user_functions
from dotenv import load_dotenv

# Carga las variables de entorno desde un archivo .env.
load_dotenv()
# Obtiene el nombre del despliegue del modelo desde las variables de entorno.
model = os.getenv("MODEL_DEPLOYMENT_NAME")
# Obtiene la cadena de conexión del proyecto desde las variables de entorno.
project_connection_string = os.getenv("PROJECT_CONNECTION_STRING")

# Crea el cliente principal para interactuar con el proyecto de IA de Azure.
project_client = AIProjectClient.from_connection_string(
    credential=DefaultAzureCredential(),
    conn_str=project_connection_string,
)

# El bloque 'with' asegura que el cliente se cierre correctamente al finalizar.
with project_client:
    # Inicializa el conjunto de herramientas del agente con nuestras funciones personalizadas.
    # [INICIO create_agent_toolset]
    # Envuelve nuestras funciones personalizadas en un objeto FunctionTool que el agente puede entender.
    functions = FunctionTool(user_functions)
    
    # Crea un conjunto de herramientas (toolset).
    toolset = ToolSet()
    # Añade nuestras funciones al conjunto de herramientas.
    toolset.add(functions)
    
    # Crea un agente y le proporciona el conjunto de herramientas.
    # Esto permite al agente ejecutar nuestro código para responder preguntas.
    agent = project_client.agents.create_agent(
        model=model,
        name="function-calling-assistant", # Nombre para el agente.
        instructions="Eres un asistente útil", # Instrucciones de comportamiento.
        toolset=toolset, # Asigna el conjunto de herramientas al agente.
    )
    # [FIN create_agent_toolset]
    print(f"Agente creado, ID: {agent.id}")

    # Crea un hilo de conversación (thread) para la comunicación.
    thread = project_client.agents.create_thread()
    print(f"Hilo creado, ID: {thread.id}")

    # Crea y añade un mensaje del usuario al hilo.
    message = project_client.agents.create_message(
        thread_id=thread.id,
        role="user",
        #content="Hola, ¿puedes obtener la información del clima para Guayaquil?",
        content="Dame la información del usuario con ID 2",
    )
    print(f"Mensaje creado, ID: {message.id}")

    # Inicia y procesa una ejecución del agente en el hilo.
    # El agente analizará el mensaje, determinará que necesita llamar a una de sus funciones (herramientas)
    # para obtener el clima, la ejecutará, y usará el resultado para formular una respuesta.
    # [INICIO create_and_process_run]
    run = project_client.agents.create_and_process_run(thread_id=thread.id, assistant_id=agent.id)
    # [FIN create_and_process_run]
    print(f"Ejecución finalizada con estado: {run.status}")

    # Manejo básico de errores por si la ejecución falla.
    if run.status == "failed":
        print(f"La ejecución falló: {run.last_error}")

    # Obtiene todos los mensajes del hilo después de que la ejecución haya finalizado.
    messages = project_client.agents.list_messages(thread_id=thread.id)
    print(f"Mensajes: {messages}")
    print("\n")
    
    # Imprimiendo la respuesta final del asistente.
    # Esta respuesta se basa en la información obtenida al ejecutar la función personalizada.
    print(f"Respuesta del asistente: {messages.data[0].content[0].text.value}")