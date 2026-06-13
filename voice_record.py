import threading
import json
import os
import speech_recognition as sr
import importlib.util

from key import DetectorPalabraClave
from voice_text import TranscriptorAudio
from services_ia import GeminiClient
from voice_output import RinVoz
from sidebar import FloatingSidebar
from services_imagenes import WikimediaSearcher
from folder_opener import FolderOpener
from modulo_executor import ModuloExecutor
from dynamic_module_generator import DynamicModuleGenerator
from modules.system.CodeArchitect import CodeArchitect

class AsistenteOrquestador:
    def __init__(self, sidebar_instance):
        self.sidebar = sidebar_instance
        self.centinela = DetectorPalabraClave(palabra_clave="rin", idioma="es-AR")
        self.transcriptor = TranscriptorAudio(idioma="es-AR")
        self.ia = GeminiClient("manifest_1.txt")
        self.motor_voz = RinVoz(forzar_local=False)
        self.generator = DynamicModuleGenerator()
        
        self.reconocedor_orden = sr.Recognizer()
        self.reconocedor_orden.pause_threshold = 6.0

        # Catálogo centralizado
        self.catalogo_modulos = {
            "WikimediaSearcher": WikimediaSearcher,
            "FolderOpener": FolderOpener,
            "CodeArchitect": CodeArchitect
        }
        
        self._cargar_modulos_dinamicos()
        self.executor = ModuloExecutor(self.catalogo_modulos)

    def _cargar_modulos_dinamicos(self):
        registry_path = "./modules/dynamic/registry.json"
        if not os.path.exists(registry_path): return

        with open(registry_path, "r") as f:
            try:
                registry = json.load(f)
            except: return
            
        for nombre, info in registry.items():
            try:
                spec = importlib.util.spec_from_file_location(nombre, info["path"])
                modulo = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(modulo)
                if hasattr(modulo, nombre):
                    self.catalogo_modulos[nombre] = getattr(modulo, nombre)
                    print(f"✅ Módulo cargado: {nombre}")
            except Exception as e:
                print(f"❌ Error cargando {nombre}: {e}")

    def iniciar_bucle(self):
        print("🚀 Orquestador iniciado correctamente. Modo iterativo activado.")
        while True:
            self.centinela.esperar_activacion()
            audio = self.capturar_orden()
            if not audio: continue

            peticion_original = self.transcriptor.transcribir(audio)
            if not peticion_original or peticion_original.startswith("["): continue

            print(f"👤 [Usuario]: {peticion_original}")
            
            # --- BUCLE DE ITERACIÓN DE INTENTOS ---
            contexto_error = ""
            for intento in range(3):
                # Incluimos el error en el prompt si es una iteración de reintento
                prompt = f"{peticion_original} {contexto_error}"
                respuesta_json = self.ia(prompt)

                try:
                    datos = json.loads(respuesta_json)
                except:
                    datos = {"leer": "No pude procesar la respuesta.", "ejecutar_modulo": None}

                # 1. AUTO-REGISTRO
                if datos.get("nuevo_modulo"):
                    m = datos["nuevo_modulo"]
                    print(f"💾 Registrando nuevo módulo: {m.get('nombre')}")
                    self.generator.registrar_modulo(m['nombre'], m['codigo'], m['metadata'])
                    self._cargar_modulos_dinamicos()
                    self.executor = ModuloExecutor(self.catalogo_modulos)
                    
                    if not datos.get("ejecutar_modulo"):
                        datos["ejecutar_modulo"] = {"clase": m['nombre'], "args": []}
                    del datos["nuevo_modulo"]

                # 2. EJECUCIÓN CON VALIDACIÓN
                ejecutar = datos.get("ejecutar_modulo")
                if isinstance(ejecutar, dict) and ejecutar.get("clase") in self.catalogo_modulos:
                    print(f"⚙️ [Intento {intento + 1}]: Ejecutando -> {ejecutar['clase']}")
                    resultado = self.executor.ejecutar_tarea(ejecutar["clase"], ejecutar.get("args", []))
                    
                    if resultado.get("success"):
                        print(f"✅ Éxito: {resultado.get('resultado')}")
                        self.motor_voz.procesar_y_hablar(datos.get("leer", "Hecho."))
                        self.sidebar.show(resultado)
                        break # Salida exitosa del bucle for
                    else:
                        # Inyectamos el error para que la IA corrija en la siguiente iteración
                        contexto_error = f" (Error previo: {resultado['error']}. Analízalo y reintenta la tarea corrigiendo la lógica o argumentos)."
                        print(f"❌ Error detectado: {resultado['error']}. Reintentando...")
                else:
                    # Si no hay acción o es una respuesta informativa
                    self.motor_voz.procesar_y_hablar(datos.get("leer", "Entendido."))
                    break

    def capturar_orden(self):
        with sr.Microphone(int(os.getenv("MIC_INDEX", 0))) as o:
            try: return self.reconocedor_orden.listen(o, timeout=5, phrase_time_limit=10)
            except: return None

if __name__ == "__main__":
    interfaz = FloatingSidebar()
    asistente = AsistenteOrquestador(interfaz)
    threading.Thread(target=asistente.iniciar_bucle, daemon=True).start()
    interfaz.iniciar_interfaz()