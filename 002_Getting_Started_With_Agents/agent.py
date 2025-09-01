# Importando las bibliotecas necesarias.
import os, time
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.projects.models import MessageTextContent
from dotenv import load_dotenv

# Carga las variables de entorno desde un archivo .env.
load_dotenv()

# [INICIO create_project_client]
# Crea un cliente para el proyecto de IA de Azure usando una cadena de conexión.
# Este cliente es el punto de entrada para interactuar con los servicios de IA.
project_client = AIProjectClient.from_connection_string(
    credential=DefaultAzureCredential(), # Utiliza las credenciales de Azure por defecto para la autenticación.
    conn_str=os.getenv("PROJECT_CONNECTION_STRING") # Obtiene la cadena de conexión desde las variables de entorno.
)

# Obtiene el nombre del despliegue del modelo que se usará.
model=os.getenv("MODEL_DEPLOYMENT_NAME")

# El bloque 'with' asegura que el cliente se cierre correctamente al finalizar las operaciones.
with project_client:

    # [INICIO create_agent]
    # Crea una nueva instancia de un agente (asistente).
    agent = project_client.agents.create_agent(  # agrega get_agent(assistant_id="") para usar un agente ya creado
        model=model,
        name="my-assistant",
        instructions="Eres un asistente útil", # Define el comportamiento y el rol del asistente.
    )
    # [FIN create_agent]
    print(f"Agente creado, ID del agente: {agent.id}")

    # [INICIO create_thread]
    # Crea un hilo de conversación (thread) para mantener el contexto del diálogo.
    thread = project_client.agents.create_thread()  # agrega get_thread(thread_id="") para usar un hilo ya creado
    # [FIN create_thread]
    print(f"Hilo creado, ID del hilo: {thread.id}")

    # [INICIO create_message]
    # Añade un mensaje del usuario al hilo de la conversación.
    message = project_client.agents.create_message(thread_id=thread.id, role="user", content="Hola, dime algo sobre la India")
    # [FIN create_message]
    print(f"Mensaje creado, ID del mensaje: {message.id}")

    # [INICIO create_run]
    # Inicia una ejecución (run), que le indica al asistente que procese el hilo y genere una respuesta.
    run = project_client.agents.create_run(thread_id=thread.id, assistant_id=agent.id) # agrega create_and_process_run para una implementación de lógica inherente

    # Sondea la ejecución mientras su estado sea 'en cola' o 'en progreso'.
    while run.status in ["queued", "in_progress", "requires_action"]:
        # Espera un segundo antes de volver a verificar.
        time.sleep(1)
        # Obtiene el estado más reciente de la ejecución.
        run = project_client.agents.get_run(thread_id=thread.id, run_id=run.id)
        # [FIN create_run]
        print(f"Estado de la ejecución: {run.status}")

    # [INICIO list_messages]
    # Una vez que la ejecución ha terminado, obtiene la lista actualizada de mensajes del hilo.
    messages = project_client.agents.list_messages(thread_id=thread.id)

    # Mostrando el ID del mensaje más reciente (la respuesta del asistente).
    print(messages.data[0].id)
    
    # Mostrando la respuesta del asistente.
    # El mensaje en la posición 0 es la respuesta más reciente generada por el asistente.
    print(messages.data[0].content[0].text.value)

    # [FIN list_messages]
    # Imprime el objeto completo de mensajes para una vista detallada.
    print(f"Mensajes: {messages}")

    try:
        # Eliminar el hilo si fue creado
        if thread:
            project_client.agents.delete_thread(thread_id=thread.id)
            print(f"Hilo eliminado: {thread.id}")
            
        # Eliminar el agente si fue creado
        if agent:
            project_client.agents.delete_agent(assistant_id=agent.id)
            print(f"Agente eliminado: {agent.id}")
            
    except Exception as cleanup_error:
        print(f"Error durante la limpieza: {cleanup_error}")