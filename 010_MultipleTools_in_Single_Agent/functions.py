# Importando bibliotecas. 'typing' es para pistas de tipo, 'json' para manejar datos JSON,
# y 'dotenv' para cargar variables de entorno.
from typing import Any, Callable, Set, Dict, List, Optional
import json
import os
from dotenv import load_dotenv

# Carga las variables de entorno desde un archivo .env (si existiera).
load_dotenv()

def get_user_info(user_id: int) -> str:
    """Recupera la información del usuario basándose en su ID.

    :param user_id (int): El ID del usuario.
    :return: La información del usuario como una cadena de texto JSON.
    :rtype: str
    """
    # Esto es un diccionario que simula una base de datos de usuarios para este ejemplo.
    # En una aplicación real, aquí habría una consulta a una base de datos.
    mock_users = {
        1: {"name": "Alice", "email": "alice@example.com"},
        2: {"name": "Bob", "email": "bob@example.com"},
        3: {"name": "Charlie", "email": "charlie@example.com"},
    }
    # Busca la información del usuario por su ID. Si no lo encuentra, devuelve un mensaje de error.
    user_info = mock_users.get(user_id, {"error": "Usuario no encontrado."})
    # Convierte el diccionario de Python a una cadena de texto con formato JSON para la respuesta.
    return json.dumps({"user_info": user_info})

# Se crea un conjunto (set) que contiene todas las funciones que queremos que el agente pueda utilizar.
# En este caso, solo contiene la función 'get_user_info'.
user_functions: Set[Callable[..., Any]] = {
    get_user_info
}