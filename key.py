import speech_recognition as sr
import os
class DetectorPalabraClave:
    def __init__(self, palabra_clave="rin", idioma="es-AR"):
        self.reconocedor = sr.Recognizer()
        self.palabra_clave = palabra_clave.lower()
        self.idioma = idioma
        self.reconocedor.pause_threshold = 0.5 

    def esperar_activacion(self):
        print(f"📡 Centinela activo: Esperando que digas '{self.palabra_clave}'...")
        with sr.Microphone(int(os.getenv("MIC_INDEX", 0))) as origen:
            self.reconocedor.adjust_for_ambient_noise(origen, duration=1)
            while True:
                try:
                    audio = self.reconocedor.listen(origen, phrase_time_limit=3)
                    texto = self.reconocedor.recognize_google(audio, language=self.idioma)
                    texto_limpio = texto.lower()
                    
                    if self.palabra_clave in texto_limpio:
                        print(f"🔥 ¡Palabra clave '{self.palabra_clave}' DETECTADA! 🔥")
                        return True
                except sr.UnknownValueError:
                    continue
                except sr.RequestError:
                    print("⚠️ Error de conexión en el centinela. Reintentando...")
                    continue