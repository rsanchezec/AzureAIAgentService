# -*- coding: utf-8 -*-

# ==============================================================================
# SECCIÓN 1: IMPORTACIONES Y CONFIGURACIÓN INICIAL
# ==============================================================================

# --- Importando las bibliotecas necesarias ---
from semantic_kernel import Kernel  # El "cerebro" u orquestador principal de Semantic Kernel.
import os  # Para interactuar con el sistema operativo, principalmente para leer variables de entorno.
import asyncio  # Para ejecutar código de forma asíncrona, necesario para las llamadas a la IA.
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion  # El conector específico para el servicio de chat de Azure OpenAI.
from dotenv import load_dotenv  # Utilidad para cargar variables desde un archivo .env.
from semantic_kernel.planners import SequentialPlanner  # El "Director" que creará el plan paso a paso.
from typing import Annotated  # Para añadir metadatos (como descripciones) a los parámetros de las funciones.
from semantic_kernel.functions.kernel_function_decorator import kernel_function  # El "decorador" que convierte una función de Python en una herramienta para la IA.
from azure.ai.projects import AIProjectClient  # El cliente para interactuar con el servicio de Agentes de Azure AI.
from azure.identity import DefaultAzureCredential  # Para manejar la autenticación con Azure.
from azure.ai.projects.models import BingGroundingTool  # La herramienta específica para la búsqueda con Bing.

# --- Cargando las variables de entorno ---
# Carga las claves y configuraciones desde tu archivo .env para mantenerlas seguras.
load_dotenv()
azure_openai_key = os.getenv("AZURE_OPENAI_API_KEY")  # Tu clave secreta para la API de Azure OpenAI.
azure_openai_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")  # La URL de tu servicio de Azure OpenAI.
azure_openai_deployment_name = os.getenv("AZURE_OPENAI_CHAT_COMPLETION_MODEL")  # El nombre de tu modelo desplegado (ej. gpt-4).
ai_project_connection_string = os.getenv("AI_PROJECT_CONNECTION_STRING")  # La cadena de conexión para el servicio de Agentes de Azure AI.
bing_connection_name = os.getenv("BING_CONNECTION_NAME")  # El nombre de tu conexión de Bing preconfigurada en Azure.

# --- Creando el cliente de Azure AI ---
# Este objeto se usará para crear los agentes "trabajadores" o "especialistas".
project_client = AIProjectClient.from_connection_string(
        credential=DefaultAzureCredential(), # Usa tus credenciales de Azure para autenticarte.
        conn_str=ai_project_connection_string # Usa la cadena de conexión para apuntar al servicio correcto.
        )

# ==============================================================================
# SECCIÓN 2: DEFINICIÓN DEL PLUGIN DE AGENTES (LOS "ESPECIALISTAS")
# ==============================================================================

# Esta clase agrupa todas las funciones que actuarán como agentes especialistas.
class Agents:
    """
    La clase 'Agents' funciona como un contenedor para las herramientas que el Planificador podrá usar.
    Cada método decorado con @kernel_function es una habilidad que el "Director" puede asignar.
    """

    # --- Agente Especialista 1: El Investigador Web ---
    @kernel_function(
        # La descripción es VITAL. El Planificador la lee para entender qué hace esta herramienta.
        description="Esta función se usará para utilizar un agente de IA de Azure con capacidad de búsqueda web usando la API de Búsqueda de Bing",
        # El nombre es cómo el Planificador se referirá a esta herramienta en el plan.
        name="WebSearchAgent"
    )
    def web_search_agent(
        self, # Parámetro estándar en los métodos de una clase.
        # 'Annotated' permite describir cada parámetro. Esto también ayuda al Planificador.
        query: Annotated[str, "La consulta del usuario para la cual se necesita obtener información contextual de la web"]
    ) -> Annotated[str, "La respuesta del agente de búsqueda web"]:
        """
        Esta función completa es el 'Departamento de Investigación'. Cuando se invoca,
        crea un agente de Azure AI desde cero, le da la herramienta de Bing, le asigna
        la tarea de buscar la 'query', y devuelve el resultado.
        """
        # Obtiene los detalles de la conexión de Bing preconfigurada en Azure.
        bing_connection = project_client.connections.get(connection_name=bing_connection_name)
        conn_id = bing_connection.id
        # Prepara la herramienta de Bing para dársela al agente.
        bing = BingGroundingTool(connection_id=conn_id)
        
        # Crea un agente de Azure AI temporal y especializado. Su única misión es buscar.
        agent = project_client.agents.create_agent(
            model=azure_openai_deployment_name,
            name="bing-assistant", # Un nombre temporal para este agente.
            instructions="Eres un asistente útil",
            tools=bing.definitions, # La única herramienta que tendrá es la búsqueda de Bing.
            headers={"x-ms-enable-preview": "true"},
        )
        # Cada agente necesita un "hilo" de conversación para operar.
        thread = project_client.agents.create_thread()
        # Se añade la consulta de búsqueda como el primer mensaje en la conversación.
        message = project_client.agents.create_message(
                thread_id=thread.id,
                role="user",
                content=query,
            )
        # Se le ordena al agente que procese la conversación y genere una respuesta.
        run = project_client.agents.create_and_process_run(thread_id=thread.id, assistant_id=agent.id)
        # Se recupera la lista de mensajes, donde la respuesta del agente será la más reciente.
        messages = project_client.agents.list_messages(thread_id=thread.id)
        
        # Se imprime la respuesta para poder ver el progreso en la consola.
        print(f"\n--- [Respuesta del Investigador Web] ---\n{messages.data[0].content[0].text.value}\n---------------------------------------\n")
        
        # Se devuelve únicamente el texto de la respuesta, que será la entrada para el siguiente paso del plan.
        return messages.data[0].content[0].text.value
    
    # --- Agente Especialista 2: El Guionista de Noticias ---
    @kernel_function(
       description="Esta función usará un agente de IA de Azure para preparar un guion para un reportero de noticias basado en información reciente para un tema específico",
       name="NewsReporterAgent"
   )
    def news_reporter_agent(
        self,
        topic: Annotated[str, "El tema para el cual se ha obtenido la información/noticia más reciente"],
        latest_news: Annotated[str,"La información más reciente para un tema específico"]
    ) -> Annotated[str, "la respuesta del NewsReporterAgent, que es el guion para el reportero"]:
        """
        Esta función completa es el 'Departamento de Redacción'. Recibe la información
        investigada y su única misión es escribir un guion con un formato específico.
        """
        # Crea un segundo agente de Azure AI, también temporal y especializado. Su única misión es escribir.
        agent = project_client.agents.create_agent(
            model=azure_openai_deployment_name,
            name="news-reporter",
            # Las instrucciones son muy detalladas para asegurar que el resultado sea de alta calidad.
            instructions="""Eres un asistente útil destinado a preparar un guion para un reportero de noticias basado en la información más reciente sobre un tema específico, los cuales se te proporcionarán.
                El canal de noticias se llama MSinghTV y el reportero se llama John. Se te dará el tema y la información más reciente para ese tema. Prepara un guion para el reportero John basado en esta información.""",
            headers={"x-ms-enable-preview": "true"}, # No tiene herramientas, solo instrucciones.
        )
        # Al igual que el otro agente, necesita su propio hilo de conversación.
        thread = project_client.agents.create_thread()
        # Se le entrega la información (el tema y las noticias) en forma de un mensaje.
        message = project_client.agents.create_message(
                thread_id=thread.id,
                role="user",
                content=f"""El tema es {topic} y la información más reciente es {latest_news}""",
            )
        # Se le ordena al agente que escriba el guion.
        run = project_client.agents.create_and_process_run(thread_id=thread.id, assistant_id=agent.id)
        # Se recupera el guion final de la conversación.
        messages = project_client.agents.list_messages(thread_id=thread.id)
        
        # Se imprime el guion final.
        print(f"\n--- [Guion del Reportero de Noticias] ---\n{messages.data[0].content[0].text.value}\n----------------------------------------\n")
            
        # Se devuelve el guion como el resultado final de esta función.
        return messages.data[0].content[0].text.value

# ==============================================================================
# SECCIÓN 3: INICIALIZACIÓN DEL KERNEL Y EL PLANIFICADOR (EL "DIRECTOR")
# ==============================================================================

# Se crea la instancia principal del Kernel, el "cerebro" orquestador.
kernel = Kernel()
service_id = "default" # Un alias para nuestro servicio de IA.

# Se conecta el Kernel al modelo de lenguaje de Azure OpenAI. Ahora el Kernel tiene "poder de cómputo".
kernel.add_service(
    AzureChatCompletion(service_id=service_id,
                        api_key=azure_openai_key,
                        deployment_name=azure_openai_deployment_name,
                        endpoint = azure_openai_endpoint
    )
)

# Se crea la instancia del Planificador. Este será nuestro "Mánager de Proyectos".
planner = SequentialPlanner(
    kernel, # Se le da acceso al Kernel para que pueda usar sus funciones y su IA.
    service_id # Se le indica qué servicio de IA debe usar para "pensar".
)

# Se añade la clase 'Agents' como un plugin al Kernel.
# Este es el paso crucial donde el "Director" conoce a su "equipo de especialistas".
agents_plugin = kernel.add_plugin(Agents(), "Agents")


# ==============================================================================
# SECCIÓN 4: EJECUCIÓN DEL PLAN
# ==============================================================================

async def main():
    """Función principal asíncrona que orquesta todo el proceso."""
    
    # Se define el objetivo de alto nivel para el planificador.
    objetivo = f"preparar un guion de noticias para John sobre las últimas noticias de la India?"
    print(f"🎯 Objetivo: {objetivo}\n")

    # --- Fase de Planificación ---
    print("🧠  El Director está pensando y creando un plan...")
    # Se le pide al planificador que cree un plan para alcanzar el objetivo.
    # En este momento, el planificador está llamando a la IA para que razone.
    sequential_plan = await planner.create_plan(objetivo)

    # Se imprime el plan que el planificador ha decidido seguir.
    print("\n📝 Los pasos del plan son:")
    for step in sequential_plan._steps:
        print(
            f"  - {step.description.replace('.', '') if step.description else 'Sin descripción'} usando la herramienta '{step.metadata.fully_qualified_name}' con los parámetros: {step.parameters}"
        )

    # --- Fase de Ejecución ---
    print("\n🚀 Ejecutando el plan...")
    # Se invoca el plan. El Kernel ejecutará cada paso en secuencia,
    # pasando automáticamente la salida de un paso como la entrada del siguiente.
    result = await sequential_plan.invoke(kernel)

    print("\n✅ Ejecución finalizada.")
    # El resultado final (el guion) ya se imprime dentro de la función 'news_reporter_agent'.
    # La variable 'result' contiene el mismo valor.

# Punto de entrada estándar para un script de Python.
if __name__ == "__main__":
    # Se ejecuta la función principal 'main' usando el gestor de eventos de asyncio.
    asyncio.run(main())