# agent_001.py - Versión CORREGIDA
import os
import time
import json
from datetime import datetime, timedelta
from typing import Optional, Dict
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

class ProductionAssistant:
    """
    Asistente de producción que reutiliza un agente existente
    y gestiona hilos de manera eficiente
    """
    
    def __init__(self):
        """Inicializa las configuraciones y obtiene el ID del agente existente"""
        # Obtener configuraciones del .env
        self.connection_string = os.getenv("PROJECT_CONNECTION_STRING")
        self.agent_id = os.getenv("AZURE_AGENT_ID")
        self.model = os.getenv("MODEL_DEPLOYMENT_NAME")
        self.retention_days = int(os.getenv("THREAD_RETENTION_DAYS", "30"))
        self.max_threads_per_user = int(os.getenv("MAX_THREADS_PER_USER", "5"))
        self.auto_cleanup = os.getenv("AUTO_CLEANUP_ENABLED", "true").lower() == "true"
        
        # Diccionario para almacenar hilos de usuarios (en producción usarías una DB)
        self.user_threads = {}
        
        print(f"🚀 Asistente inicializado")
        print(f"📌 Agent ID: {self.agent_id}")
        print(f"🤖 Modelo: {self.model}")
        print(f"🔧 Auto-limpieza: {self.auto_cleanup}")
        print(f"📅 Retención de hilos: {self.retention_days} días")
        
        # Verificar que el agente existe
        self._verify_agent()
    
    def _get_client(self):
        """Crea un nuevo cliente para cada operación"""
        return AIProjectClient.from_connection_string(
            credential=DefaultAzureCredential(),
            conn_str=self.connection_string
        )
    
    def _verify_agent(self):
        """Verifica que el agente configurado existe"""
        try:
            client = self._get_client()
            with client:
                # Intentar obtener el agente
                agent = client.agents.get_agent(assistant_id=self.agent_id)
                print(f"✅ Agente verificado: {agent.name}")
                return True
        except Exception as e:
            print(f"⚠️ Error: No se pudo verificar el agente {self.agent_id}")
            print(f"   Detalles: {e}")
            print(f"   Creando nuevo agente...")
            self._create_new_agent()
    
    def _create_new_agent(self):
        """Crea un nuevo agente si el configurado no existe"""
        try:
            client = self._get_client()
            with client:
                agent = client.agents.create_agent(
                    model=self.model,
                    name="production-assistant",
                    instructions="Eres un asistente útil y profesional. Proporciona respuestas claras y concisas."
                )
                self.agent_id = agent.id
                print(f"✅ Nuevo agente creado: {agent.id}")
                print(f"⚠️  Actualiza tu .env con: AZURE_AGENT_ID={agent.id}")
        except Exception as e:
            print(f"❌ Error creando agente: {e}")
            raise
    
    def create_session(self, user_id: str, persistent: bool = False) -> Optional[str]:
        """
        Crea o recupera una sesión de chat para un usuario
        
        Args:
            user_id: Identificador del usuario
            persistent: Si True, mantiene el hilo entre sesiones
        
        Returns:
            ID del hilo creado o recuperado
        """
        try:
            # Si es persistente, buscar hilo existente
            if persistent and user_id in self.user_threads:
                thread_id = self.user_threads[user_id]
                print(f"📂 Recuperando hilo existente para {user_id}: {thread_id}")
                return thread_id
            
            # Crear nuevo hilo
            client = self._get_client()
            with client:
                thread = client.agents.create_thread()
                thread_id = thread.id
            
            # Guardar en memoria (en producción, guardar en DB)
            if persistent:
                self.user_threads[user_id] = thread_id
            
            print(f"🆕 Nuevo hilo creado para {user_id}: {thread_id}")
            return thread_id
                
        except Exception as e:
            print(f"❌ Error creando sesión: {e}")
            return None
    
    def send_message(self, thread_id: str, user_message: str) -> Optional[str]:
        """
        Envía un mensaje al asistente y obtiene la respuesta
        
        Args:
            thread_id: ID del hilo de conversación
            user_message: Mensaje del usuario
        
        Returns:
            Respuesta del asistente o None si hay error
        """
        try:
            client = self._get_client()
            with client:
                # Crear mensaje del usuario
                message = client.agents.create_message(
                    thread_id=thread_id,
                    role="user",
                    content=user_message
                )
                print(f"💬 Mensaje enviado: {message.id[:8]}...")
                
                # Ejecutar el asistente
                run = client.agents.create_run(
                    thread_id=thread_id,
                    assistant_id=self.agent_id
                )
                
                # Esperar respuesta
                print("⏳ Procesando...", end="")
                while run.status in ["queued", "in_progress", "requires_action"]:
                    time.sleep(1)
                    print(".", end="", flush=True)
                    run = client.agents.get_run(
                        thread_id=thread_id,
                        run_id=run.id
                    )
                print(" ✅")
                
                # Obtener respuesta
                messages = client.agents.list_messages(thread_id=thread_id)
                
                # El mensaje más reciente es la respuesta del asistente
                assistant_response = messages.data[0].content[0].text.value
                return assistant_response
                
        except Exception as e:
            print(f"❌ Error enviando mensaje: {e}")
            return None
    
    def cleanup_thread(self, thread_id: str, user_id: Optional[str] = None):
        """
        Elimina un hilo específico
        
        Args:
            thread_id: ID del hilo a eliminar
            user_id: ID del usuario (opcional, para limpiar del diccionario)
        """
        try:
            client = self._get_client()
            with client:
                client.agents.delete_thread(thread_id=thread_id)
                print(f"🗑️ Hilo eliminado: {thread_id}")
            
            # Limpiar del diccionario si existe
            if user_id and user_id in self.user_threads:
                del self.user_threads[user_id]
                    
        except Exception as e:
            print(f"⚠️ Error eliminando hilo: {e}")
    
    def list_all_threads(self):
        """Lista todos los hilos existentes en el proyecto"""
        try:
            client = self._get_client()
            with client:
                # Nota: Esta funcionalidad puede no estar disponible en todas las versiones
                # del SDK. Si no funciona, puedes comentar esta función.
                threads = client.agents.list_threads()
                print(f"\n📋 Hilos existentes:")
                for thread in threads:
                    print(f"   - {thread.id} (Creado: {thread.created_at})")
                return threads
        except Exception as e:
            print(f"⚠️ No se pudieron listar los hilos: {e}")
            return []
    
    def get_stats(self) -> Dict:
        """Obtiene estadísticas del uso actual"""
        return {
            "agent_id": self.agent_id,
            "active_threads": len(self.user_threads),
            "users": list(self.user_threads.keys()),
            "auto_cleanup": self.auto_cleanup,
            "retention_days": self.retention_days
        }


def demo_conversacion_temporal():
    """Demo: Conversación temporal (se elimina al finalizar)"""
    print("\n" + "="*60)
    print("DEMO 1: Conversación Temporal (sin persistencia)")
    print("="*60)
    
    assistant = ProductionAssistant()
    user_id = "demo_user_temp"
    thread_id = None
    
    try:
        # Crear sesión temporal
        thread_id = assistant.create_session(user_id, persistent=False)
        
        if thread_id:
            # Simular conversación
            print(f"\n👤 Usuario: {user_id}")
            
            # Mensaje 1
            pregunta1 = "Hola, ¿cómo estás? Soy un usuario de prueba."
            print(f"\n📝 Pregunta: {pregunta1}")
            response = assistant.send_message(thread_id, pregunta1)
            if response:
                print(f"🤖 Asistente: {response}\n")
            
            # Mensaje 2
            pregunta2 = "¿Puedes explicarme qué es Azure AI?"
            print(f"\n📝 Pregunta: {pregunta2}")
            response = assistant.send_message(thread_id, pregunta2)
            if response:
                print(f"🤖 Asistente: {response}\n")
            
    finally:
        # Limpiar al finalizar
        if thread_id and assistant.auto_cleanup:
            assistant.cleanup_thread(thread_id, user_id)
            print("✅ Sesión temporal limpiada automáticamente")


def demo_conversacion_persistente():
    """Demo: Conversación persistente (mantiene el hilo)"""
    print("\n" + "="*60)
    print("DEMO 2: Conversación Persistente (con memoria)")
    print("="*60)
    
    assistant = ProductionAssistant()
    user_id = "usuario_123"
    
    # Primera sesión
    print("\n📍 Primera sesión del usuario:")
    thread_id = assistant.create_session(user_id, persistent=True)
    
    if thread_id:
        pregunta1 = "Hola, mi nombre es Juan y trabajo en desarrollo de software."
        print(f"\n📝 Pregunta: {pregunta1}")
        response = assistant.send_message(thread_id, pregunta1)
        if response:
            print(f"🤖 Asistente: {response}\n")
    
    # Simular que el usuario vuelve más tarde
    print("\n📍 El usuario vuelve (misma sesión):")
    thread_id = assistant.create_session(user_id, persistent=True)  # Recupera el mismo hilo
    
    if thread_id:
        pregunta2 = "¿Recuerdas cuál es mi nombre y a qué me dedico?"
        print(f"\n📝 Pregunta: {pregunta2}")
        response = assistant.send_message(thread_id, pregunta2)
        if response:
            print(f"🤖 Asistente: {response}\n")
    
    # Mostrar estadísticas
    stats = assistant.get_stats()
    print("\n📊 Estadísticas:")
    print(json.dumps(stats, indent=2))
    
    # Preguntar si limpiar
    if thread_id and input("\n¿Deseas limpiar este hilo persistente? (s/n): ").lower() == 's':
        assistant.cleanup_thread(thread_id, user_id)


def main():
    """Función principal con menú interactivo"""
    print("\n" + "🚀 SISTEMA DE ASISTENTE EN PRODUCCIÓN 🚀".center(60, "="))
    print("\nEste demo muestra cómo usar un agente reutilizable en producción")
    print("Usando el agente: " + os.getenv("AZURE_AGENT_ID", "No configurado"))
    
    while True:
        print("\n" + "="*60)
        print("MENÚ PRINCIPAL")
        print("="*60)
        print("1. Demo conversación temporal (se elimina al finalizar)")
        print("2. Demo conversación persistente (mantiene historial)")
        print("3. Conversación interactiva personalizada")
        print("4. Ver configuración actual")
        print("5. Salir")
        
        opcion = input("\nSelecciona una opción (1-5): ")
        
        if opcion == "1":
            demo_conversacion_temporal()
        
        elif opcion == "2":
            demo_conversacion_persistente()
        
        elif opcion == "3":
            # Conversación interactiva personalizada
            print("\n" + "="*60)
            print("CONVERSACIÓN INTERACTIVA")
            print("="*60)
            
            assistant = ProductionAssistant()
            user_id = input("Ingresa tu ID de usuario: ")
            persistente = input("¿Mantener historial? (s/n): ").lower() == 's'
            
            thread_id = assistant.create_session(user_id, persistent=persistente)
            
            if thread_id:
                print("\n💬 Conversación iniciada (escribe 'salir' para terminar)")
                print("-" * 40)
                
                while True:
                    mensaje = input("\n👤 Tú: ")
                    if mensaje.lower() == 'salir':
                        break
                    
                    respuesta = assistant.send_message(thread_id, mensaje)
                    if respuesta:
                        print(f"\n🤖 Asistente: {respuesta}")
                
                if not persistente and assistant.auto_cleanup:
                    assistant.cleanup_thread(thread_id, user_id)
                    print("\n✅ Conversación temporal eliminada")
                else:
                    print(f"\n💾 Conversación guardada. Thread ID: {thread_id}")
        
        elif opcion == "4":
            # Mostrar configuración
            print("\n" + "="*60)
            print("CONFIGURACIÓN ACTUAL")
            print("="*60)
            print(f"PROJECT_CONNECTION: {os.getenv('PROJECT_CONNECTION_STRING')[:50]}...")
            print(f"MODEL_DEPLOYMENT_NAME: {os.getenv('MODEL_DEPLOYMENT_NAME')}")
            print(f"AZURE_AGENT_ID: {os.getenv('AZURE_AGENT_ID')}")
            print(f"THREAD_RETENTION_DAYS: {os.getenv('THREAD_RETENTION_DAYS')}")
            print(f"MAX_THREADS_PER_USER: {os.getenv('MAX_THREADS_PER_USER')}")
            print(f"AUTO_CLEANUP_ENABLED: {os.getenv('AUTO_CLEANUP_ENABLED')}")
        
        elif opcion == "5":
            print("\n👋 ¡Hasta luego!")
            break
        
        else:
            print("⚠️ Opción no válida")


if __name__ == "__main__":
    main()