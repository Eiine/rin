import speech_recognition as sr

class TranscriptorAudio:
    def __init__(self, idioma="es-AR"):
        """
        Inicializa el transcriptor con un idioma específico.
        Por defecto usa español de Argentina.
        """
        self.reconocedor = sr.Recognizer()
        self.idioma = idioma

    def transcribir(self, objeto_audio):
        """
        Recibe un objeto de audio de speech_recognition,
        lo procesa y retorna el texto transcrito.
        """
        if objeto_audio is None:
            return "Error: No se proporcionó un objeto de audio válido."
            
        try:
            # Procesamos el objeto de audio que entró por parámetro
            texto_transcrito = self.reconocedor.recognize_google(
                objeto_audio, 
                language=self.idioma
            )
            return texto_transcrito
            
        except sr.UnknownValueError:
            return "[No se pudo entender el audio]"
        except sr.RequestError as e:
            return f"[Error de conexión con el servicio de voz: {e}]"


# =====================================================================
# EJEMPLO DE USO: Cómo implementar la clase en tu flujo principal
# =====================================================================
if __name__ == "__main__":
    
    # 1. Instanciamos nuestra clase especialista
    asistente_voz = TranscriptorAudio(idioma="es-AR")
    
    # 2. Capturamos el audio desde el micrófono de forma externa
    reconocedor_micro = sr.Recognizer()
    
    with sr.Microphone() as origen:
        print("\n[Ajustando ruido ambiente...]")
        reconocedor_micro.adjust_for_ambient_noise(origen, duration=1)
        
        print("🎤 Hablá ahora...")
        # Capturamos el audio puro del hardware
        audio_capturado = reconocedor_micro.listen(origen)
        print("⏳ Enviando audio a la clase transcriptora...")

    # 3. Le pasamos el objeto de audio a la clase y guardamos el retorno
    resultado_final = asistente_voz.transcribir(audio_capturado)
    
    # 4. Imprimimos el string que nos devolvió la clase
    print("\n✨ Resultado retornado por la clase:")
    print(f"👉 {resultado_final}\n")