import subprocess
import shlex

def rin_hablar_local(texto: str, velocidad: int = 145):
    """
    Hace que Rin hable utilizando el binario de espeak del sistema operativo
    de forma directa y portable a través de un subproceso de Python.
    """
    print(f"🎙️ Rin (Local) dice: '{texto}'")
    
    # Preparamos los parámetros del comando exactamente como te funcionó en la terminal:
    # -v es: idioma español
    # -s: velocidad de habla (words per minute, 145 es ideal)
    comando = f'espeak -v es -s {velocidad} "{texto}"'
    
    try:
        # shlex.split divide el string de forma segura para evitar problemas con las comillas
        argumentos = shlex.split(comando)
        
        # Ejecuta el comando en el sistema operativo de forma síncrona
        # (bloquea el script de Python hasta que termina de hablar, igual que runAndWait)
        subprocess.run(argumentos, check=True)
        print("✅ Flujo de audio completado de forma local.")
        
    except FileNotFoundError:
        print("❌ Error: No se encontró 'espeak' instalado en este sistema operativo.")
    except Exception as e:
        print(f"❌ Ocurrió un error inesperado al reproducir el audio: {e}")

if __name__ == "__main__":
    frase_prueba = "Hola, soy Rin, un asistente cognitivo que está siendo desarrollado por Miguel."
    rin_hablar_local(frase_prueba)