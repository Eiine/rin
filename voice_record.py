import threading
import json
import requests
import speech_recognition as sr
import os
import time

from view_image import WebImageViewer

# Módulos del sistema
from key import DetectorPalabraClave
from voice_text import TranscriptorAudio
from services_ia import GeminiClient
from voice_output import RinVoz
from sidebar import FloatingSidebar
from services_imagenes import WikimediaSearcher
from folder_opener import FolderOpener  # <-- NUEVO IMPORT

import threading
import json
import os
import speech_recognition as sr

from view_image import WebImageViewer
from key import DetectorPalabraClave
from voice_text import TranscriptorAudio
from services_ia import GeminiClient
from voice_output import RinVoz
from sidebar import FloatingSidebar
from services_imagenes import WikimediaSearcher
from folder_opener import FolderOpener
from modulo_executor import ModuloExecutor  # Importamos el nuevo motor

class AsistenteOrquestador:

    def __init__(self, sidebar_instance):
        self.sidebar = sidebar_instance
        self.centinela = DetectorPalabraClave(palabra_clave="rin", idioma="es-AR")
        self.transcriptor = TranscriptorAudio(idioma="es-AR")
        self.ia = GeminiClient("manifest_1.txt")
        self.motor_voz = RinVoz(forzar_local=False)
        
        self.reconocedor_orden = sr.Recognizer()
        self.reconocedor_orden.pause_threshold = 6.0

        # Catálogo de módulos
        self.catalogo_modulos = {
            "WikimediaSearcher": WikimediaSearcher,
            "FolderOpener": FolderOpener
        }
        
        # Inicializamos el ejecutor universal
        self.executor = ModuloExecutor(self.catalogo_modulos)

    def capturar_orden(self):
        with sr.Microphone(int(os.getenv("MIC_INDEX", 0))) as origen:
            print("\n🔊 [Asistente]: Te escucho...")
            self.reconocedor_orden.adjust_for_ambient_noise(origen, duration=0.5)
            try:
                return self.reconocedor_orden.listen(origen, timeout=5, phrase_time_limit=10)
            except sr.WaitTimeoutError:
                return None

    def iniciar_bucle(self):
        print("🚀 Orquestador iniciado correctamente.")
        while True:
            # 1. Esperar palabra clave
            self.centinela.esperar_activacion()

            # 2. Capturar orden
            audio_orden = self.capturar_orden()
            if not audio_orden: continue

            peticion_texto = self.transcriptor.transcribir(audio_orden)
            if not peticion_texto or peticion_texto.startswith("["): continue

            print(f"👤 [Usuario]: {peticion_texto}")
            respuesta_json = self.ia(peticion_texto)

            try:
                datos_dict = json.loads(respuesta_json)
            except:
                datos_dict = {"leer": respuesta_json, "metodo": False, "imagen": None}

            # 3. Motor de ejecución (Simplificado mediante el Executor)
            ejecutar_modulo = datos_dict.get("ejecutar_modulo")
            if isinstance(ejecutar_modulo, dict):
                nombre_clase = ejecutar_modulo.get("clase")
                argumentos = ejecutar_modulo.get("args", [])

                if nombre_clase in self.catalogo_modulos:
                    print(f"⚙️ [Orquestador]: Ejecutando módulo -> {nombre_clase}")
                    # Delegamos la ejecución al motor, sin if/else internos
                    resultado = self.executor.ejecutar_tarea(nombre_clase, argumentos)
                    datos_dict.update(resultado)

            # 4. Voz
            self.motor_voz.procesar_y_hablar(respuesta_json)

            # 5. Sidebar
            self.sidebar.show(datos_dict)

            # 6. Visualizador de imágenes
            if datos_dict.get("imagen"):
                try:
                    WebImageViewer(datos_dict["imagen"])
                except Exception as e:
                    print(f"❌ Error al abrir visor: {e}")

# ==================================================
# ARRANQUE DEL SISTEMA
# ==================================================
if __name__ == "__main__":
    interfaz = FloatingSidebar()
    asistente = AsistenteOrquestador(sidebar_instance=interfaz)
    hilo_audio = threading.Thread(target=asistente.iniciar_bucle, daemon=True)
    hilo_audio.start()

    try:
        interfaz.iniciar_interfaz()
    except KeyboardInterrupt:
        print("\n👋 Sistema cerrado correctamente.")