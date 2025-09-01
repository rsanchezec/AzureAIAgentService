# Importando las bibliotecas necesarias para el funcionamiento del script.
import os
from openai import AzureOpenAI
from dotenv import load_dotenv

# Creando un cliente para interactuar con la API de Azure OpenAI.
# Esta es la configuración inicial para conectar nuestro código con el servicio de Azure.
load_dotenv() # Carga las variables de entorno desde un archivo .env. Es una buena práctica para mantener seguras las claves de API y otros datos sensibles.

client = AzureOpenAI(
  azure_endpoint = os.getenv("OPENAI_API_BASE"), # Obtiene la URL del endpoint de Azure desde las variables de entorno.
  api_key=os.getenv("OPENAI_API_KEY"),          # Obtiene la clave de la API desde las variables de entorno para autenticación.
  api_version="2024-02-15-preview"              # Especifica la versión de la API de OpenAI que se va a utilizar.
)

# Enviando una solicitud al modelo de Azure OpenAI para obtener una respuesta.
# Aquí es donde le pedimos al modelo que realice una tarea específica.
response = client.chat.completions.create(
    model="rsc-gpt-5-mini", # model = "deployment_name". Debes reemplazar "YOUR_MODEL_NAME" con el nombre de tu despliegue en Azure.
    messages=[
        # El mensaje del sistema establece el comportamiento inicial del asistente.
        {"role": "system", "content": "Eres un asistente muy útil."},
        # El mensaje del usuario es la pregunta o instrucción que le damos al modelo.
        {"role": "user", "content": "cuales son los jugadores de la seleccion del Ecuador 2025?"}
    ]
)

# Imprimiendo la respuesta final que se recibe después de hacer la llamada a la API.
# La respuesta del modelo se encuentra dentro del objeto 'response'.
print("la información es:" + response.choices[0].message.content + "\n")