import subprocess
import shlex
import os

class RinVoz:
    def __init__(self, forzar_local=False):
        self.forzar_local = forzar_local

    def procesar_y_hablar(self, texto: str, velocidad: int = 145):
        """Tu método original para hablar al vuelo."""
        print(f"🎙️ Rin (Local) dice: '{texto}'")
        comando = f'espeak -v es -s {velocidad} "{texto}"'
        subprocess.run(shlex.split(comando), check=True)

    def guardar_y_reproducir(self, texto: str, ruta_archivo: str, velocidad: int = 145):
        """Genera el audio, lo guarda y lo reproduce."""
        # -w guarda el audio en formato .wav
        comando = f'espeak -v es -s {velocidad} -w "{ruta_archivo}" "{texto}"'
        subprocess.run(shlex.split(comando), check=True)
        self.reproducir_archivo(ruta_archivo)

    def reproducir_archivo(self, ruta_archivo: str):
        """Reproduce un archivo .wav guardado."""
        # Usamos 'aplay' (típico de sistemas Linux/ALSA) para reproducir el archivo
        # Es mucho más eficiente que regenerar el audio
        subprocess.run(["aplay", "-q", ruta_archivo])