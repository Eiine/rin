import os
import json
import shlex
import subprocess
import time
import asyncio
import socket
import pygame
import edge_tts

class RinVoz:
    def __init__(self, forzar_local: bool = False):
        """
        Componente de salida de audio híbrido para Rin.
        :param forzar_local: Si es True, ignora internet y usa siempre espeak.
        """
        self.forzar_local = forzar_local
        self.voz_edge = "es-AR-ElenaNeural"
        self.archivo_temporal = "rin_voz_temp.mp3"
        
        # Parámetros de espeak local (la versión 'menos peor')
        self.espeak_lang = "es+f2"
        self.espeak_speed = 140
        self.espeak_pitch = 65

    def _hay_internet(self) -> bool:
        """Verifica de forma ultrarrápida si el servidor tiene salida a internet."""
        if self.forzar_local:
            return False
        try:
            # Intentamos conectar al DNS de Google en el puerto 53
            socket.setdefaulttimeout(1.5)
            socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(("8.8.8.8", 53))
            return True
        except OSError:
            return False

    def _hablar_espeak(self, texto: str):
        """Motor offline de emergencia (espeak)."""
        print("🔌 [Voz-Rin]: Modo OFFLINE activo. Usando espeak local...")
        comando = f'espeak -v {self.espeak_lang} -s {self.espeak_speed} -p {self.espeak_pitch} "{texto}"'
        try:
            argumentos = shlex.split(comando)
            subprocess.run(argumentos, check=True)
        except Exception as e:
            print(f"❌ Error crítico en motor local espeak: {e}")

    async def _hablar_edge(self, texto: str):
        """Motor online premium (Edge-TTS)."""
        print("🌐 [Voz-Rin]: Modo ONLINE activo. Generando voz neuronal...")
        try:
            # 1. Generar el flujo binario y guardarlo en el archivo temporal
            comunicar = edge_tts.Communicate(texto, self.voz_edge)
            await comunicar.save(self.archivo_temporal)
            
            # 2. Reproducir el archivo usando Pygame de forma portable
            pygame.mixer.init()
            pygame.mixer.music.load(self.archivo_temporal)
            pygame.mixer.music.play()
            
            while pygame.mixer.music.get_busy():
                await asyncio.sleep(0.1)
                
            pygame.mixer.music.stop()
            pygame.mixer.quit()
            
            # 3. Limpieza del buffer de disco
            if os.path.exists(self.archivo_temporal):
                os.remove(self.archivo_temporal)
                
        except Exception as e:
            print(f"⚠️ Falló Edge-TTS en caliente. Rebotando a espeak... Motivo: {e}")
            self._hablar_espeak(texto)

    def procesar_y_hablar(self, entrada_raw: str):
        """
        Recibe la respuesta de la API, parsea el JSON para extraer la clave 'leer'
        y determina dinámicamente qué motor de audio utilizar.
        """
        texto_para_leer = ""

        # --- FASE 1: PARSEO INTELIGENTE DEL JSON ---
        try:
            datos = json.loads(entrada_raw)
            # Extraemos la llave que acordamos en el manifiesto
            texto_para_leer = datos.get("leer", "").strip()
        except (json.JSONDecodeError, TypeError):
            # Fallback de seguridad: si Gemini no devolvió JSON o vino roto,
            # leemos el string crudo para que el sistema no se quede mudo
            texto_para_leer = entrada_raw.strip()

        if not texto_para_leer:
            print("⚠️ [Voz-Rin]: Nada para leer en esta respuesta.")
            return

        # --- FASE 2: DECISIÓN DE CONECTIVIDAD ---
        if self._hay_internet():
            # Ejecutamos el motor asíncrono de Edge dentro del entorno síncrono del orquestador
            asyncio.run(self._hablar_edge(texto_para_leer))
        else:
            self._hablar_espeak(texto_para_leer)