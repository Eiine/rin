import speech_recognition as sr
import os
import threading
from sidebar import FloatingSidebar
def escanear_microfonos_sr():
    """Muestra exactamente cómo ve los micrófonos la librería SpeechRecognition."""
    print("\n🔍 [Diagnóstico Rin]: Mapeando dispositivos desde SpeechRecognition...")
    try:
        lista_micros = sr.Microphone.list_microphone_names()
        if not lista_micros:
            print("❌ La librería no detectó ningún hardware de entrada de audio.")
            return
        
        print("=== COMPATIBILIDAD DE MICRÓFONOS EN PYTHON ===")
        for indice, nombre in enumerate(lista_micros):
            # Limpiamos posibles caracteres raros del driver de Windows
            nombre_limpio = nombre.encode('utf-8', errors='ignore').decode('utf-8')
            print(f"🎤 Índice [{indice}]: {nombre_limpio}")
        print("==============================================\n")
    except Exception as e:
        print(f"❌ Fallo crítico al listar micrófonos con PyAudio: {e}")

if __name__ == "__main__":
    # 1. Ejecutamos el escáner nativo antes de arrancar todo
    escanear_microfonos_sr()
    
    # Leemos qué índice tenés configurado actualmente
    print(f"⚙️ Índice actual configurado en .env: {os.getenv('MIC_INDEX', '0 (Por defecto)')}")

    # 2. Inicialización de la interfaz gráfica en el hilo principal
    interfaz = FloatingSidebar()
    
    # 3. Instanciamos el orquestador pasándole la UI
    asistente = AsistenteOrquestador(sidebar_instance=interfaz)
    
    # 4. Lanzamos el bucle completo de fondo
    hilo_audio = threading.Thread(target=asistente.iniciar_bucle, daemon=True)
    hilo_audio.start()
    print("🚀 Hilo de escucha de audio (Centinela + Orden) inicializado de fondo...")

    try:
        interfaz.iniciar_interfaz()
    except KeyboardInterrupt:
        print("\n👋 Sistema cerrado correctamente.")