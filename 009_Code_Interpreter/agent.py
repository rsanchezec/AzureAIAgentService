# Importando las bibliotecas y utilidades necesarias.
import os
from azure.ai.projects import AIProjectClient
# Importa clases clave para manejar el Intérprete de Código, adjuntar archivos y definir roles.
from azure.ai.projects.models import CodeInterpreterTool, MessageAttachment
from azure.ai.projects.models import FilePurpose, MessageRole
from azure.identity import DefaultAzureCredential
from pathlib import Path
from dotenv import load_dotenv

# Carga las variables de entorno.
load_dotenv()

model = os.getenv("MODEL_DEPLOYMENT_NAME")
project_connection_string = os.getenv("PROJECT_CONNECTION_STRING")

# Crea el cliente principal para interactuar con el proyecto de IA de Azure.
project_client = AIProjectClient.from_connection_string(
    credential=DefaultAzureCredential(),
    conn_str=project_connection_string
)

# El bloque 'with' asegura que el cliente se cierre correctamente al finalizar.
with project_client:
    # Construye una ruta absoluta al archivo CSV para asegurar que siempre se encuentre.
    current_dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(current_dir, "electronics_products.csv")
    
    # Sube el archivo y espera a que sea procesado y esté listo para usar.
    # 'FilePurpose.AGENTS' especifica que este archivo será utilizado por un agente.
    file = project_client.agents.upload_file_and_poll(
        file_path=path, purpose=FilePurpose.AGENTS
    )
    print(f"Archivo subido, ID del archivo: {file.id}")

    # [INICIO create_agent_and_message_with_code_interpreter_file_attachment]
    # Ten en cuenta que el CodeInterpreter debe estar habilitado al crear el agente;
    # de lo contrario, el agente no podrá ver el archivo adjunto para interpretarlo con código.
    agent = project_client.agents.create_agent(
        model=model,
        name="code-interpreter-assistant",
        instructions="Eres un asistente útil destinado a responder la consulta del usuario analizando el archivo que se te proporciona",
        # Habilita la herramienta CodeInterpreter para que el agente pueda ejecutar código Python.
        tools=CodeInterpreterTool().definitions,
    )
    print(f"Agente creado, ID del agente: {agent.id}")

    thread = project_client.agents.create_thread()
    print(f"Hilo creado, ID del hilo: {thread.id}")

    # Crea un objeto "adjunto" (attachment).
    # Esto vincula el ID del archivo subido con la herramienta CodeInterpreter.
    attachment = MessageAttachment(file_id=file.id, tools=CodeInterpreterTool().definitions)

    # Crea un mensaje de usuario.
    message = project_client.agents.create_message(
        thread_id=thread.id,
        role="user",
        content="¿Podrías crear un gráfico de columnas con los productos en el eje X y sus respectivos precios en el eje Y?",
        # Adjunta el archivo al mensaje para que el agente sepa que debe usarlo para esta consulta específica.
        attachments=[attachment],
    )
    # [FIN create_agent_and_message_with_code_interpreter_file_attachment]
    print(f"Mensaje creado, ID del mensaje: {message.id}")

    # Inicia y procesa la ejecución. El agente leerá la pregunta, verá el archivo CSV,
    # y usará su herramienta CodeInterpreter para escribir y ejecutar código Python que genere el gráfico.
    run = project_client.agents.create_and_process_run(thread_id=thread.id, assistant_id=agent.id)
    print(f"Ejecución finalizada con estado: {run.status}")

    # Manejo de errores.
    if run.status == "failed":
        # Comprueba si el error es "Rate limit is exceeded." (Límite de peticiones excedido), en cuyo caso necesitarías más cuota.
        print(f"La ejecución falló: {run.last_error}")

    # Obtiene todos los mensajes del hilo, que ahora incluirán la respuesta del agente.
    messages = project_client.agents.list_messages(thread_id=thread.id)
    print(f"Mensajes: {messages}")

    # Obtiene el último mensaje de texto enviado por el agente.
    last_msg = messages.get_last_text_message_by_role(MessageRole.AGENT)
    if last_msg:
        print(f"Último Mensaje: {last_msg.text.value}")

    # Define el directorio de salida en la misma carpeta que el script.
    output_dir = Path(current_dir)
    output_dir.mkdir(parents=True, exist_ok=True) # Crea el directorio si no existe.

    # Itera sobre cualquier contenido de imagen en la respuesta (el gráfico generado).
    for image_content in messages.image_contents:
        print(f"ID del archivo de imagen: {image_content.image_file.file_id}")
        file_name = f"{image_content.image_file.file_id}_image_file.png"
        
        # Construye la ruta final para guardar el archivo.
        file_path = output_dir / file_name

        # Descarga y guarda el archivo de imagen en la ruta especificada.
        project_client.agents.save_file(
            file_id=image_content.image_file.file_id,
            file_name=str(file_path)
        )
        print(f"Archivo de imagen guardado en: {file_path}")