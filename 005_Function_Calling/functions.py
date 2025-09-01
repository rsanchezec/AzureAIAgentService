# Importando las bibliotecas necesarias.
import requests # Para realizar peticiones HTTP a las APIs.
from typing import Any, Callable, Set, Dict, List, Optional # Para usar "type hints" (pistas de tipo) que mejoran la legibilidad del código.
import json # Para trabajar con datos en formato JSON.
import os # Para acceder a variables de entorno, como las claves de API.
from dotenv import load_dotenv

# Carga las variables de entorno desde un archivo .env.
load_dotenv()

def get_weather(location):
    """
    Obtiene la información del clima para la ubicación especificada.

    :param location (str): La ubicación para la cual obtener el clima.
    :return: La información del clima como una cadena de caracteres.
    :rtype: str
    """
    
    # Este proceso se divide en dos pasos:
    # 1. Convertir el nombre de la ubicación (ej. "Londres") a coordenadas geográficas (latitud y longitud).
    # 2. Usar esas coordenadas para obtener la información del clima.

    # Llamando a la API de geocodificación de OpenWeatherMap.
    api_key = os.getenv("OPENWEATHERMAP_API_KEY")
    # url = "http://api.openweathermap.org/geo/1.0/direct?q=" + location + "&limit=1&appid=YOUR_API_KEY"
    url = f"http://api.openweathermap.org/geo/1.0/direct?q={location}&limit=1&appid={api_key}"
    response=requests.get(url)
    get_response=response.json()
    # Obteniendo la latitud y longitud de la ubicación específica.
    latitude=get_response[0]['lat']
    longitude = get_response[0]['lon']

    # Llamando a la API del clima de OpenWeatherMap con las coordenadas obtenidas.
    # url_final = "https://api.openweathermap.org/data/2.5/weather?lat=" + str(latitude) + "&lon=" + str(longitude) + "&appid=YOUR_API_KEY"
    url_final = f"https://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&appid={api_key}"
    final_response = requests.get(url_final)
    final_response_json = final_response.json()
    # Extrayendo la descripción del clima de la respuesta.
    weather=final_response_json['weather'][0]['description']
    return weather

def get_user_info(user_id: int) -> str:
    """Recupera la información del usuario basándose en su ID.

    :param user_id (int): El ID del usuario.
    :return: La información del usuario como una cadena de texto JSON.
    :rtype: str
    """
    # Esto es un diccionario que simula una base de datos de usuarios para este ejemplo.
    mock_users = {
        1: {"name": "Alice", "email": "alice@example.com"},
        2: {"name": "Bob", "email": "bob@example.com"},
        3: {"name": "Charlie", "email": "charlie@example.com"},
    }
    # Obtiene la información del usuario o un mensaje de error si no se encuentra.
    user_info = mock_users.get(user_id, {"error": "Usuario no encontrado."})
    # Convierte el diccionario de Python a una cadena de texto con formato JSON.
    return json.dumps({"user_info": user_info})

# Se crea un conjunto (set) que contiene todas las funciones que queremos que el agente pueda utilizar.
# El "type hint" Set[Callable[..., Any]] indica que es un conjunto de funciones.
# Al agruparlas aquí, es fácil pasarlas todas juntas al agente al momento de su creación.
user_functions: Set[Callable[..., Any]] = {
    get_weather,
    get_user_info
}