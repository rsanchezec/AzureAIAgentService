from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.functions import KernelArguments
import os
from dotenv import load_dotenv
import asyncio

# 1. Se crea una instancia del Kernel.
kernel = Kernel()

service_id = "default"

# Carga las variables de entorno.
load_dotenv()
# 2. Se añade y configura el servicio de Azure OpenAI.
kernel.add_service(
    AzureChatCompletion(service_id=service_id,
                        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
                        deployment_name=os.getenv("AZURE_OPENAI_CHAT_COMPLETION_MODEL"),
                        endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    )
)

# 3. Se carga el plugin que contiene nuestras funciones.
plugin = kernel.add_plugin(parent_directory = os.path.join(os.path.dirname(__file__), "plugins", "prompt_templates"), plugin_name = "basic_plugin")

# 4. Se selecciona la función específica 'contact_information' del plugin.
contact_function = plugin["contact_information"]

# Define la función asíncrona que ejecutará la llamada al Kernel.
async def contact():
    # 5. Se invoca la función, pasando todos los datos de contacto como argumentos.
    # El Kernel usará estos argumentos para rellenar la plantilla del prompt.
    return await kernel.invoke(
        contact_function, 
        KernelArguments(
            name="Raul Sanchez", 
            contact_number="1234567890", 
            email_id="hello@gmail.com", 
            address="1234, 5th Avenue, New York, NY 10001"
        )
    )

# 6. Se ejecuta la función asíncrona y se imprime el resultado final.
print(asyncio.run(contact()))