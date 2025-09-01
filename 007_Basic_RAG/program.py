# Importando utilidades y bibliotecas importantes
import json
import requests
import openai
from openai import AzureOpenAI # El cliente específico para interactuar con Azure OpenAI.
import os # Para interactuar con el sistema operativo y leer variables de entorno.
from dotenv import load_dotenv # Para cargar variables desde un archivo .env.

# Estableciendo los detalles de configuración de OpenAI
load_dotenv() # Carga las variables de entorno (claves, endpoints, etc.) desde el archivo .env.
# Obtiene el nombre del despliegue del modelo de embeddings desde las variables de entorno.
deployment_name = os.getenv('get_embed_model')

# Creando un cliente de Azure OpenAI
# Este objeto 'client' será el que se comunique con la API de Azure.
client = AzureOpenAI(
  api_key = os.getenv("get_oai_key"),      # Obtiene la clave de la API para la autenticación.
  api_version = "2024-02-15-preview",      # Especifica la versión de la API que se va a utilizar.
  azure_endpoint =os.getenv("get_oai_base") # Obtiene la URL del endpoint de tu servicio en Azure.
)

# Este es el texto de entrada que queremos convertir en un embedding.
data="se acercan muchos festivales"

# Llama a la API para crear el embedding a partir del texto de entrada.
# El modelo convierte el significado semántico del texto en un vector de números.
response = client.embeddings.create(
    input = data,
    model= deployment_name
)

# Imprime la respuesta completa de la API en formato JSON bien estructurado.
# Esto mostrará el vector de embedding y otra información relevante.
print(response.model_dump_json(indent=2))