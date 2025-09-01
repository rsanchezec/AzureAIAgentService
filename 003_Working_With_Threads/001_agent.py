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
# La autenticación se maneja con las credenciales predeterminadas de Azure.
project_client = AIProjectClient.from_connection_string(
    credential=DefaultAzureCredential(),
    conn_str=os.getenv("PROJECT_CONNECTION_STRING") # Obtiene la cadena de conexión de las variables de entorno.
)

# Obtiene el nombre del despliegue del modelo desde las variables de entorno.
model=os.getenv("MODEL_DEPLOYMENT_NAME")

# El bloque 'with' asegura que la conexión con el cliente se cierre correctamente al finalizar.
with project_client:
    # Inicializar variables para el agente y el hilo
    agent = None
    thread = None
    
    try:
        # [INICIO create_agent]
        # Crea un nuevo agente (asistente) con un modelo, nombre e instrucciones específicas.
        agent = project_client.agents.create_agent(
            model=model,
            name="rsc-my-assistant", # Nombre personalizado para tu asistente.
            instructions="Eres un asistente útil", # Instrucciones que definen el comportamiento del asistente.
        )
        # [FIN create_agent]
        print(f"Agente creado, ID del agente: {agent.id}")

        # [INICIO create_thread]
        # Crea un hilo (thread) que representa una conversación.
        thread = project_client.agents.create_thread()
        # [FIN create_thread]
        print(f"Hilo creado, ID del hilo: {thread.id}")
        
        # Declarando la variable de elección para controlar el bucle de la conversación.
        choice: str = ""
        
        # El bucle se ejecutará mientras el usuario no escriba "END".
        while(choice!="END"):
            # Pide al usuario que ingrese su pregunta o mensaje.
            user_query = input("Ingresa tu consulta: ")
            
            # [INICIO create_message]
            # Crea un nuevo mensaje con el rol de "usuario" y lo añade al hilo de la conversación.
            message = project_client.agents.create_message(thread_id=thread.id, role="user", content=user_query)
            # [FIN create_message]
            print(f"Mensaje creado, ID del mensaje: {message.id}")
            
            # [INICIO create_run]
            # Inicia una ejecución (run), que le indica al asistente que procese el hilo y genere una respuesta.
            run = project_client.agents.create_run(thread_id=thread.id, assistant_id=agent.id)

            # Sondea la ejecución mientras su estado sea 'en cola', 'en progreso' o 'requiere acción'.
            while run.status in ["queued", "in_progress", "requires_action"]:
                # Espera un segundo antes de volver a verificar el estado.
                time.sleep(1)
                # Obtiene el estado más reciente de la ejecución.
                run = project_client.agents.get_run(thread_id=thread.id, run_id=run.id)
                # [FIN create_run]
                print(f"Estado de la ejecución: {run.status}")
            
            # [INICIO list_messages]
            # Una vez que la ejecución ha terminado, obtiene la lista actualizada de mensajes del hilo.
            messages = project_client.agents.list_messages(thread_id=thread.id)

            # Mostrando la respuesta del asistente.
            # El mensaje más reciente (índice 0) es la respuesta del asistente.
            print(messages.data[0].content[0].text.value)
            
            # Pregunta al usuario si desea terminar la conversación.
            choice = input("Escribe END para detener la conversación o cualquier otra cosa para continuar: ")
            
    except Exception as e:
        print(f"Error durante la ejecución: {e}")
        
    finally:
        # Limpieza: Eliminar el agente y el hilo al finalizar
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
        
        print("Conversación finalizada")