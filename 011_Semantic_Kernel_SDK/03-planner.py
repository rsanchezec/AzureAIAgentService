from semantic_kernel import Kernel
import os
import asyncio
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from dotenv import load_dotenv
# Importa la clase del planificador secuencial.
from semantic_kernel.planners import SequentialPlanner

# --- Configuración Inicial ---
kernel = Kernel()
service_id = "default"
load_dotenv()
kernel.add_service(
    AzureChatCompletion(service_id=service_id,
                        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
                        deployment_name=os.getenv("AZURE_OPENAI_CHAT_COMPLETION_MODEL"),
                        endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    )
)

# 1. Se crea una instancia del Planificador Secuencial.
# Se le proporciona el kernel para que tenga acceso a los plugins y al servicio de IA.
planner = SequentialPlanner(
    kernel,
    service_id
)

# 2. Se cargan las herramientas que el planificador podrá usar.
# Este 'writerPlugin' debe contener funciones como 'Summarize' y 'Email'.
#kernel.add_plugin(parent_directory="../plugins/prompt_templates/", plugin_name="writerPlugin")
kernel.add_plugin(parent_directory = os.path.join(os.path.dirname(__file__), "plugins", "prompt_templates"), plugin_name = "writerPlugin")

# (Opcional) Imprime todas las funciones disponibles para que veas qué herramientas tiene el planificador.
print("Funciones cargadas en el Kernel:")
for plugin_name, plugin in kernel.plugins.items():
    for function_name, function in plugin.functions.items():
        print(f"  - Plugin: {plugin_name}, Función: {function_name}")
        
# 3. Se prepara la entrada de datos.
file_path = os.path.join(os.path.dirname(__file__), "data", "chatgpt.txt")
text=" "
with open(file_path, "r") as file:
    chatgpt = file.read()
    text = text+chatgpt
    
# 4. Se define el OBJETIVO de alto nivel en lenguaje natural.
goal = f"resume este texto: {text} y envíalo por correo a sam@gmail.com"
        
# Define una función asíncrona para que el planificador cree el plan.
async def call_planner():
    # 5. Se le pide al planificador que cree un plan para alcanzar el objetivo.
    # El planificador analizará el objetivo y seleccionará las funciones necesarias del 'writerPlugin'.
    return await planner.create_plan(goal)

# Ejecuta la creación del plan.
sequential_plan = asyncio.run(call_planner())

# 6. Se imprime el plan generado para que podamos ver los pasos que la IA ha decidido seguir.
print("\nLos pasos del plan son:")
for step in sequential_plan._steps:
    print(
        f"- {step.description.replace('.', '') if step.description else 'Sin descripción'} usando {step.metadata.fully_qualified_name} con parámetros: {step.parameters}"
    )

# Define una función asíncrona para ejecutar el plan.
async def generate_answer():
    # 7. Se ejecuta el plan completo.
    # El Kernel llamará a cada función en la secuencia, pasando la salida de un paso como entrada al siguiente.
    return await sequential_plan.invoke(kernel)

# Ejecuta el plan y obtiene el resultado final.
result = asyncio.run(generate_answer())

# Imprime el resultado final de la ejecución de todo el plan.
print(f"\nResultado final:\n{result}")