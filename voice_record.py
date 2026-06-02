import threading
import json
import speech_recognition as sr
from key import DetectorPalabraClave 
from voice_text import TranscriptorAudio
from services_ia import GeminiClient 
from voice_output import RinVoz 
# 📌 IMPORTAMOS LA SIDEBAR
from sidebar import FloatingSidebar

class AsistenteOrquestador:
    def __init__(self, sidebar_instance):
        self.sidebar = sidebar_instance # Guardamos la referencia de la interfaz
        self.centinela = DetectorPalabraClave(palabra_clave="rin", idioma="es-AR")
        self.transcriptor = TranscriptorAudio(idioma="es-AR")
        self.ia = GeminiClient("manifest_1.txt")
        self.motor_voz = RinVoz(forzar_local=False)
        self.reconocedor_orden = sr.Recognizer()
        self.reconocedor_orden.pause_threshold = 1.5

    def capturar_orden(self):
        with sr.Microphone() as origen:
            print("\n🔊 [Asistente]: Te escucho...")
            self.reconocedor_orden.adjust_for_ambient_noise(origen, duration=0.5)
            audio_orden = self.reconocedor_orden.listen(origen)
        return audio_orden

    def iniciar_bucle(self):
        while True:
            self.centinela.esperar_activacion()
            audio_de_la_orden = self.capturar_orden()
            peticion_texto = self.transcriptor.transcribir(audio_de_la_orden)
            
            if peticion_texto and not peticion_texto.startswith("["):
                respuesta_json = self.ia(peticion_texto)
                
                # Parsea el JSON para mandárselo limpio a la Sidebar gráfica
                try:
                    datos_dict = json.loads(respuesta_json)
                except:
                    datos_dict = {"leer": respuesta_json, "metodo": ""}

                # 🚀 ACTUALIZA LA SIDEBAR (Seguro a través de hilos gracias al .after)
                self.sidebar.show(datos_dict)

                # Narra la respuesta por audio en simultáneo
                self.motor_voz.procesar_y_hablar(respuesta_json)

if __name__ == "__main__":
    # 1. Instanciamos la interfaz gráfica en el hilo principal
    interfaz = FloatingSidebar()
    
    # 2. Instanciamos el orquestador pasándole la UI
    asistente = AsistenteOrquestador(sidebar_instance=interfaz)
    
    # 3. Lanzamos el bucle de audio DE FONDO (Daemon=True para que muera al cerrar la UI)
    hilo_audio = threading.Thread(target=asistente.iniciar_bucle, daemon=True)
    hilo_audio.start()
    print("🚀 Hilo de escucha de audio inicializado de fondo...")

    # 4. Bloqueamos el hilo principal con la UI
    try:
        interfaz.iniciar_interfaz()
    except KeyboardInterrupt:
        print("\n👋 Sistema cerrado correctamente.")