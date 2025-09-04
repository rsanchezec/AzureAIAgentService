# Importando las bibliotecas necesarias de Semantic Kernel y otras utilidades.
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.functions import KernelArguments
import os
import asyncio # Biblioteca para ejecutar código de forma asíncrona.
import time
from dotenv import load_dotenv

# 1. Se crea una instancia del Kernel. Este es el objeto central que orquestará todo.
kernel = Kernel()

# Carga las variables de entorno desde el archivo .env.
load_dotenv()

# Validar que las variables de entorno están configuradas
required_env_vars = [
    "AZURE_OPENAI_API_KEY",
    "AZURE_OPENAI_CHAT_COMPLETION_MODEL", 
    "AZURE_OPENAI_ENDPOINT"
]

for var in required_env_vars:
    if not os.getenv(var):
        raise ValueError(f"Variable de entorno requerida no encontrada: {var}")

# Define un identificador para el servicio de IA que vamos a registrar.
service_id = "default"
# 2. Se añade un servicio de IA al Kernel.
# En este caso, se conecta a un modelo de chat de Azure OpenAI.
kernel.add_service(
    AzureChatCompletion(service_id=service_id,
                        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
                        deployment_name=os.getenv("AZURE_OPENAI_CHAT_COMPLETION_MODEL"),
                        endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    )
)

# 3. Se añade un "Plugin" al Kernel.
# Un plugin es una colección de funciones (habilidades).
# Aquí, se carga un plugin llamado "basic_plugin" desde un directorio local
# que contiene plantillas de prompts.
plugin = kernel.add_plugin(parent_directory = os.path.join(os.path.dirname(__file__), "plugins", "prompt_templates"), plugin_name = "basic_plugin")

# 4. Se selecciona una función específica del plugin.
# Estamos obteniendo la función llamada "greeting" del "basic_plugin".
greeting_function = plugin["greeting"]

# Definimos una función asíncrona para ejecutar la habilidad.
async def greeting():
    try:
        # 5. Se invoca la función a través del Kernel.
        # El Kernel tomará la plantilla de prompt de 'greeting_function',
        # llenará los marcadores de posición con los 'KernelArguments' (nombre y edad),
        # enviará el prompt completo al servicio de IA y devolverá la respuesta.
        return await kernel.invoke(greeting_function, KernelArguments(name="Raul Sanchez", age="42"))
    except Exception as e:
        print(f"Error detallado al invocar la función: {e}")
        print(f"Tipo de error: {type(e)}")
        if hasattr(e, '__cause__') and e.__cause__:
            print(f"Causa del error: {e.__cause__}")
        raise

# 6. Se ejecuta la función asíncrona y se obtiene el resultado.
greeting_response =  asyncio.run(greeting())

# Se imprime la respuesta final generada por el modelo de IA.
print(greeting_response)