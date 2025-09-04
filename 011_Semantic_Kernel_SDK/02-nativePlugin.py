import asyncio
import os
from dotenv import load_dotenv
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel import Kernel
import math
from typing import Annotated

# Importa el decorador que convierte una función de Python en una habilidad del Kernel.
from semantic_kernel.functions.kernel_function_decorator import kernel_function

# --- Configuración Inicial ---
kernel = Kernel()
load_dotenv()

service_id = "default"
# Añade y configura el servicio de Azure OpenAI como en los ejemplos anteriores.
kernel.add_service(
    AzureChatCompletion(service_id=service_id,
                        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
                        deployment_name=os.getenv("AZURE_OPENAI_CHAT_COMPLETION_MODEL"),
                        endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    )
)

# --- Definición del Plugin Nativo ---
# Se define una clase de Python que agrupará todas nuestras funciones matemáticas.
class Math:
    """
    Descripción: MathPlugin proporciona un conjunto de funciones para realizar cálculos matemáticos.

    Uso:
        kernel.add_plugin(MathPlugin(), plugin_name="math")

    Ejemplos:
        {{math.Add}} => Devuelve la suma de la entrada y 'amount' (proporcionados en KernelArguments)
        {{math.Subtract}} => Devuelve la resta de la entrada y 'amount' (proporcionados en KernelArguments)
        {{math.Multiply}} => Devuelve la multiplicación de la entrada y 'number2' (proporcionados en KernelArguments)
        {{math.Divide}} => Devuelve la división de la entrada y 'number2' (proporcionados en KernelArguments)
    """

    # El decorador '@kernel_function' expone este método al Kernel como una habilidad.
    @kernel_function(
        description="Divide dos números.", # La descripción ayuda al LLM a entender qué hace la función.
        name="Divide",                    # El nombre con el que el Kernel conocerá esta función.
    )
    def divide(
        self,
        # 'Annotated' permite añadir una descripción a cada parámetro, lo cual es muy útil para el LLM.
        number1: Annotated[float, "el primer número para dividir"],
        number2: Annotated[float, "el segundo número por el cual dividir"],
    ) -> Annotated[float, "La salida es un número flotante"]:
        return float(number1) / float(number2)

    @kernel_function(
        description="Multiplica dos números. Al aumentar en un porcentaje, no olvides sumar 1 al porcentaje.",
        name="Multiply",
    )
    def multiply(
        self,
        number1: Annotated[float, "el primer número a multiplicar"],
        number2: Annotated[float, "el segundo número a multiplicar"],
    ) -> Annotated[float, "La salida es un número flotante"]:
        return float(number1) * float(number2)

    @kernel_function(
        description="Calcula la raíz cuadrada de un número",
        name="Sqrt",
    )
    def square_root(
        self,
        number1: Annotated[float, "el número del cual obtener la raíz cuadrada"],
    ) -> Annotated[float, "La salida es un número flotante"]:
        return math.sqrt(float(number1))

    # Si no se proporciona una descripción, el Kernel puede intentar inferirla del código.
    @kernel_function(name="Add")
    def add(
        self,
        number1: Annotated[float, "el primer número a sumar"],
        number2: Annotated[float, "el segundo número a sumar"],
    ) -> Annotated[float, "la salida es un número flotante"]:
        return float(number1) + float(number2)

    @kernel_function(
        description="Resta un valor a otro valor",
        name="Subtract",
    )
    def subtract(
        self,
        number1: Annotated[float, "el primer número"],
        number2: Annotated[float, "el número a restar"],
    ) -> Annotated[float, "la salida es un número flotante"]:
        return float(number1) - float(number2)

# --- Uso del Plugin ---
# Se crea una instancia de la clase Math y se añade al Kernel como un plugin llamado "Math".
math_plugin = kernel.add_plugin(Math(), "Math")

# Se selecciona la función específica "Sqrt" del plugin que acabamos de registrar.
sqrt_function = math_plugin["Sqrt"]

# Define la función asíncrona para invocar la habilidad.
async def square_root():
    # Llama a la función del Kernel directamente, pasando los argumentos por nombre.
    return await kernel.invoke(sqrt_function, number1=4)

# Ejecuta la función y muestra el resultado.
print(asyncio.run(square_root()))