import os
import json
import shlex
import subprocess
import asyncio
import socket
import platform 
import pygame
import edge_tts
import pyttsx3

class RinVoz:
    def __init__(self, forzar_local: bool = False):
        self.forzar_local = forzar_local
        self.voz_edge = "es-AR-ElenaNeural"
        self.sistema_operativo = platform.system()
        self.espeak_lang = "es+f2"
        self.espeak_speed = 140
        self.espeak_pitch = 65
        
        try:
            if self.sistema_operativo == "Windows":
                self.engine_local = pyttsx3.init(driverName='sapi5')
            else:
                self.engine_local = None 
        except: self.engine_local = None

    def _hay_internet(self) -> bool:
        if self.forzar_local: return False
        try:
            socket.setdefaulttimeout(1.5)
            socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(("8.8.8.8", 53))
            return True
        except: return False

    def reproducir_archivo(self, ruta_archivo: str):
        """Reproduce un archivo local con Pygame."""
        pygame.mixer.init()
        pygame.mixer.music.load(ruta_archivo)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
        pygame.mixer.music.stop()
        pygame.mixer.quit()

    def guardar_y_reproducir(self, texto: str, ruta_archivo: str):
        """Genera audio, lo guarda y reproduce. Si existe, no regenera."""
        # --- VERIFICACIÓN DE CACHÉ ---
        if os.path.exists(ruta_archivo):
            print(f"⚡ [Caché]: Usando archivo existente: {ruta_archivo}")
            self.reproducir_archivo(ruta_archivo)
            return

        print(f"🎙️ [Voz-Rin]: Generando nueva voz para caché...")
        if self._hay_internet():
            asyncio.run(self._guardar_edge(texto, ruta_archivo))
        else:
            print("⚠️ Sin internet: Usando voz local (sin caché persistente)")
            self.procesar_y_hablar(texto)
            return
            
        self.reproducir_archivo(ruta_archivo)

    async def _guardar_edge(self, texto, ruta):
        comunicar = edge_tts.Communicate(texto, self.voz_edge)
        await comunicar.save(ruta)

    def procesar_y_hablar(self, entrada_raw: str):
        texto = entrada_raw.strip()
        if self._hay_internet():
            asyncio.run(self._hablar_edge(texto))
        else:
            self._hablar_local_offline(texto)

    async def _hablar_edge(self, texto):
        archivo_temp = "temp.mp3"
        await self._guardar_edge(texto, archivo_temp)
        self.reproducir_archivo(archivo_temp)
        if os.path.exists(archivo_temp): os.remove(archivo_temp)

    def _hablar_local_offline(self, texto):
        if self.sistema_operativo == "Windows" and self.engine_local:
            self.engine_local.say(texto)
            self.engine_local.runAndWait()
        else:
            comando = f'espeak -v {self.espeak_lang} -s {self.espeak_speed} "{texto}"'
            subprocess.run(shlex.split(comando))