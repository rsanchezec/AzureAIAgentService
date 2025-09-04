# Azure AI Foundry - Agent Service Course

Este proyecto contiene ejemplos prácticos del curso de Azure AI Foundry, enfocado en la implementación de agentes inteligentes y servicios de IA usando el SDK de Azure AI Projects.

## 📁 Estructura del Proyecto

### 000_Documentation
Documentación HTML del curso con resúmenes de:
- Agentes LLM y Azure AI Agent Service
- Azure AI Foundry SDK
- Function Calling y OpenAPI
- RAG (Retrieval-Augmented Generation)
- Embeddings y Azure AI Search
- MCP (Model Context Protocol)
- Multiagentes con Azure Semantic Kernel
- Suite MCP con multiagentes y plugins

### 001_ChatCompletionsAPI
Introducción básica a la API de Chat Completions de Azure OpenAI.
- **Archivo principal**: `call.py`
- **Funcionalidad**: Llamadas básicas a modelos GPT para chat

### 002_Getting_Started_With_Agents
Fundamentos de creación y gestión de agentes.
- **Archivo principal**: `agent.py`
- **Funcionalidad**: Crear agentes, threads, mensajes y ejecutar conversaciones

### 003_Working_With_Threads
Gestión avanzada de hilos de conversación.
- **Archivos**: `001_agent.py`, `002_agent.py`
- **Funcionalidad**: Manejo de contexto y conversaciones persistentes

### 004_Bing_Grounding
Integración con búsqueda web de Bing.
- **Archivo principal**: `agent.py`
- **Funcionalidad**: Agentes con capacidad de búsqueda en tiempo real usando Bing

### 005_Function_Calling
Implementación de llamadas a funciones personalizadas.
- **Archivos**: `agent.py`, `functions.py`
- **Funcionalidad**: 
  - Obtener información del clima via API
  - Consultar datos de usuarios mockeados
  - Function calling personalizado

### 006_OpenAPI_Functions
Integración de APIs externas usando especificaciones OpenAPI.
- **Archivos**: `agent.py`, `weather_openapi.json`
- **Funcionalidad**: Consumo de APIs definidas por especificación OpenAPI

### 007_Basic_RAG
Implementación básica de RAG (Retrieval-Augmented Generation).
- **Archivo principal**: `program.py`
- **Funcionalidad**: Generación de embeddings y búsqueda semántica

### 008_RAG_Azure_AI_Search
RAG avanzado con Azure AI Search.
- **Archivos**: `agent.py`, `collateral.zip`
- **Funcionalidad**: Búsqueda avanzada e indexación con Azure AI Search

### 009_Code_Interpreter
Implementación de agentes con capacidades de interpretación de código.
- **Archivos**: `agent.py`, `electronics_products.csv`
- **Funcionalidad**: 
  - Análisis de datos con Python usando Code Interpreter
  - Generación de gráficos y visualizaciones
  - Procesamiento de archivos CSV adjuntos

### 010_MultipleTools_in_Single_Agent
Demostración de cómo combinar múltiples herramientas en un solo agente.
- **Archivos**: `agent.py`, `functions.py`
- **Funcionalidad**:
  - Combinación de function calling personalizado con búsqueda web de Bing
  - Uso de ToolSet para agrupar múltiples capacidades
  - Ejecución secuencial de herramientas en una sola consulta
  - Ejemplo práctico: buscar información de usuario y realizar búsqueda web relacionada
  - Demostración de orquestación automática entre herramientas

### 011_Semantic_Kernel_SDK
Ejemplos completos del SDK de Semantic Kernel para sistemas de IA avanzados y multi-agente.
- **Archivos**: 
  - `00-introduction.py` - Introducción básica al kernel y configuración con Azure OpenAI
  - `01-promptTemplate.py` - Trabajo con plantillas de prompts
  - `02-nativePlugin.py` - Creación de plugins nativos
  - `03-planner.py` - Planificador secuencial para tareas complejas
  - `04-agentic_system.py` y `04-agentic_system.ipynb` - Sistema agéntico completo
- **Datos**: `data/chatgpt.txt` - Archivo de texto para ejemplos de procesamiento
- **Plugins**: 
  - `basic_plugin` - Plugin básico con funciones de saludo y contacto
  - `writerPlugin` - Plugin de escritura con funciones de resumen y email
- **Funcionalidad**:
  - Configuración básica y avanzada de Semantic Kernel
  - Carga de plugins de plantillas de prompts
  - Ejecución de funciones con parámetros personalizados
  - Creación y gestión de plugins personalizados
  - Planificación automática de tareas complejas
  - Sistemas agénticos con múltiples capacidades
  - Integración con Azure OpenAI para modelos de chat


## 🛠️ Tecnologías Utilizadas

- **Azure AI Projects SDK** (`azure-ai-projects==1.0.0b5`)
- **Azure OpenAI** (`openai`)
- **Azure Identity** (`azure-identity==1.20.0`)
- **Semantic Kernel** (`semantic-kernel`) - Framework para orquestación de IA
- **Python-dotenv** - Gestión de variables de entorno
- **Requests** - Llamadas HTTP a APIs externas
- **JSONRef** - Manejo de especificaciones OpenAPI

## 📋 Requisitos Previos

1. **Cuenta de Azure** con acceso a Azure AI Foundry
2. **Python 3.8+**
3. **Variables de entorno configuradas**:
   ```
   PROJECT_CONNECTION_STRING=tu_connection_string
   MODEL_DEPLOYMENT_NAME=tu_modelo_desplegado
   OPENAI_API_KEY=tu_api_key
   OPENAI_API_BASE=tu_endpoint
   AI_SEARCH_INDEX_NAME=tu_indice
   BING_CONNECTION_NAME=tu_conexion_bing
   
   # Para Semantic Kernel
   AZURE_OPENAI_API_KEY=tu_azure_openai_api_key
   AZURE_OPENAI_CHAT_COMPLETION_MODEL=tu_modelo_chat
   AZURE_OPENAI_ENDPOINT=tu_azure_openai_endpoint
   ```

## 🚀 Instalación

```bash
pip install -r requirements.txt
```

## 💡 Características Principales

### Agentes Inteligentes
- Creación y gestión de agentes conversacionales
- Manejo de hilos de conversación persistentes
- Integración con modelos de Azure OpenAI

### Function Calling
- Ejecución de funciones personalizadas desde agentes
- Integración con APIs externas (clima, datos de usuario)
- Soporte para especificaciones OpenAPI

### RAG (Retrieval-Augmented Generation)
- Generación de embeddings para búsqueda semántica
- Integración con Azure AI Search
- Búsqueda de información contextual

### Búsqueda Web
- Integración con Bing Search para información en tiempo real
- Citaciones y referencias de fuentes web

## 🔧 Uso

Cada carpeta contiene ejemplos independientes. Para ejecutar un ejemplo:

```bash
cd 00X_Nombre_Modulo
python agent.py  # o program.py según el módulo
```

## 📖 Orden de Aprendizaje Recomendado

1. **001_ChatCompletionsAPI** - Fundamentos de Azure OpenAI
2. **002_Getting_Started_With_Agents** - Creación básica de agentes
3. **003_Working_With_Threads** - Gestión de conversaciones
4. **005_Function_Calling** - Funciones personalizadas
5. **006_OpenAPI_Functions** - Integración con APIs
6. **004_Bing_Grounding** - Búsqueda web
7. **010_MultipleTools_in_Single_Agent** - Combinación de múltiples herramientas
8. **009_Code_Interpreter** - Interpretación de código y análisis de datos
9. **007_Basic_RAG** - RAG básico
10. **008_RAG_Azure_AI_Search** - RAG avanzado
11. **011_Semantic_Kernel_SDK** - SDK completo de Semantic Kernel

## 🎯 Casos de Uso

- **Chatbots empresariales** con acceso a datos internos
- **Asistentes con búsqueda web** en tiempo real
- **Sistemas de pregunta-respuesta** sobre documentos
- **Agentes con capacidades específicas** (clima, datos de usuario)
- **Análisis de datos y visualización** con Code Interpreter
- **Implementación de RAG** para búsqueda semántica
- **Sistemas multi-agente** con orquestación inteligente
- **Planificación automática de tareas** complejas con Semantic Kernel
- **Plugins personalizados** para funcionalidades específicas

---

*Proyecto educativo - Curso Udemy Azure AI Foundry*