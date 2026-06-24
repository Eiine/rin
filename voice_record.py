# -*- coding: utf-8 -*-
import threading
import json
import os
import hashlib
import speech_recognition as sr
import traceback

# Módulos locales
from modules.VisionCapture import VisionCapture
from key import DetectorPalabraClave
from voice_text import TranscriptorAudio
from services_ia import GeminiClient
from voice_output import RinVoz
from sidebar import FloatingSidebar
from modulo_executor import ModuloExecutor
from modules.ContextManager import ContextManager
from modules.browser_player import BrowserPlayer
from modules.process_manager import ProcessManager
from modules.app_launcher import AppLauncher
from modules.GeneralSearcher import GeneralSearcher
from modules.FolderOpener import FolderOpener

class AsistenteOrquestador:
    def __init__(self, sidebar_instance):
        self.sidebar = sidebar_instance
        self.centinela = DetectorPalabraClave(palabra_clave="rin", idioma="es-AR")
        self.centinela.variantes = ["rin", "ren", "ran", "ron", "ryn", "rein", "in", "ri", "ir", "inn", "rinn", "rina", "rin-rin", "rins", "lin", "din", "tin", "gin", "reyn", "reen"]
        self.transcriptor = TranscriptorAudio(idioma="es-AR")
        self.ia = GeminiClient("manifest_1.txt")
        self.motor_voz = RinVoz(forzar_local=False)
        self.contexto = ContextManager()
        
        self.media_path = "media"
        if not os.path.exists(self.media_path):
            os.makedirs(self.media_path)
            
        self.reconocedor_orden = sr.Recognizer()
        self.catalogo_modulos = {
            "BrowserPlayer": BrowserPlayer,
            "ProcessManager": ProcessManager,
            "AppLauncher": AppLauncher,
            "GeneralSearcher": GeneralSearcher,
            "FolderOpener": FolderOpener,
            "VisionCapture": VisionCapture
        }
        self.executor = ModuloExecutor(self.catalogo_modulos)

    def obtener_audio_cached(self, texto):
        hash_texto = hashlib.md5(texto.encode()).hexdigest()
        archivo_audio = os.path.join(self.media_path, f"{hash_texto}.mp3")
        self.motor_voz.guardar_y_reproducir(texto, archivo_audio)

    def capturar_orden(self):
        with sr.Microphone() as o:
            try:
                return self.reconocedor_orden.listen(o, timeout=15, phrase_time_limit=15)
            except Exception as e:
                print(f"Error al capturar audio: {e}")
                return None

    def iniciar_bucle(self):
        print("🚀 Orquestador Rin operativo y escuchando...")
        while True:
            try:
                self.centinela.esperar_activacion()
                self.obtener_audio_cached("A la orden, jefe.")
                
                audio = self.capturar_orden()
                if not audio: continue
                
                peticion = self.transcriptor.transcribir(audio)
                if not peticion: continue
                print(f"👤 [Usuario]: {peticion}")

                estado_actual = self.contexto.leer_contexto()
                prompt_full = f"Contexto actual: {json.dumps(estado_actual)}\nUsuario dice: {peticion}"
                
                # Primera llamada a la IA para decidir qué hacer
                respuesta_bruta = self.ia(prompt_full)
                respuesta_limpia = respuesta_bruta.replace('```json', '').replace('```', '').strip()
                datos = json.loads(respuesta_limpia)
                
                ejecutar = datos.get("ejecutar_modulo")
                resultado_tecnico = "Sin acciones."
                ruta_imagen = None 
                
                # Ejecución de Módulos
                if isinstance(ejecutar, dict):
                    res = self.executor.ejecutar_tarea(ejecutar["clase"], ejecutar.get("args", []))
                    
                    if res.get("success"):
                        resultado_tecnico = str(res.get("resultado"))
                        # Si es el módulo de visión, capturamos la ruta para procesarla
                        if ejecutar["clase"] == "VisionCapture":
                            ruta_imagen = "temp_vision.png"
                    else:
                        resultado_tecnico = str(res.get("error"))
                    
                    self.contexto.registrar_accion(f"{ejecutar['clase']}: {ejecutar['args']}", resultado_tecnico)

                # Si el módulo de visión capturó algo, re-enviamos a la IA con la imagen
                if ruta_imagen and os.path.exists(ruta_imagen):
                    prompt_vision = f"Basado en esta captura, responde a la petición del usuario: {peticion}"
                    respuesta_bruta = self.ia(prompt_vision, ruta_imagen=ruta_imagen)
                    respuesta_limpia = respuesta_bruta.replace('```json', '').replace('```', '').strip()
                    datos = json.loads(respuesta_limpia)
                    os.remove(ruta_imagen) # Limpieza

                # Actualizar UI y Voz
                ui_info = datos.get("ui_data", {})
                if ui_info.get("mostrar"):
                    ui_info["detalles_tecnicos"] = resultado_tecnico
                    self.sidebar.show(ui_info)
                
                self.obtener_audio_cached(datos.get("voz", "Entendido."))
                
            except Exception as e:
                print(f"⚠️ Error en el flujo del orquestador: {e}")
                traceback.print_exc()

if __name__ == "__main__":
    try:
        interfaz = FloatingSidebar()
        asistente = AsistenteOrquestador(interfaz)
        hilo = threading.Thread(target=asistente.iniciar_bucle, daemon=True)
        hilo.start()
        interfaz.iniciar_interfaz()
    except Exception as e:
        print(f"CRITICAL ERROR AL INICIAR: {e}")
        traceback.print_exc()