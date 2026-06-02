import os
import json
import shlex
import subprocess
import asyncio
import socket
import platform 
import pygame
import edge_tts
import pyttsx3  # <--- NUEVA DEPENDENCIA PARA EL RESPALDO MULTIPLATAFORMA

class RinVoz:
    def __init__(self, forzar_local: bool = False):
        self.forzar_local = forzar_local
        self.voz_edge = "es-AR-ElenaNeural"
        self.archivo_temporal = "rin_voz_temp.mp3"
        
        # Detectamos el Sistema Operativo una sola vez al iniciar
        self.sistema_operativo = platform.system()
        
        # Parámetros adaptativos de espeak local (Para Linux)
        self.espeak_lang = "es+f2"
        self.espeak_speed = 140
        self.espeak_pitch = 65

        # 📌 INICIALIZACIÓN DEL MOTOR LOCAL DE RESPALDO
        self.engine_local = None
        try:
            if self.sistema_operativo == "Windows":
                # SAPI5 es el motor nativo de Windows (No requiere eSpeak)
                self.engine_local = pyttsx3.init(driverName='sapi5')
                self.engine_local.setProperty('rate', 170)  # Velocidad de habla cómoda
                
                # Intentamos buscar una voz en español instalada en Windows
                voces = self.engine_local.getProperty('voices')
                for voz in tuple(voces):
                    if "spanish" in voz.name.lower() or "helena" in voz.name.lower() or "sabina" in voz.name.lower():
                        self.engine_local.setProperty('voice', voz.id)
                        break
            else:
                # Si es Linux, mantenemos la inicialización por defecto para espeak
                self.engine_local = None 
        except Exception as e:
            print(f"⚠️ Advertencia al inicializar el subsistema de voz local: {e}")

    def _hay_internet(self) -> bool:
        if self.forzar_local:
            return False
        try:
            socket.setdefaulttimeout(1.5)
            socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(("8.8.8.8", 53))
            return True
        except OSError:
            return False

    def _hablar_local_offline(self, texto: str):
        """Motor offline adaptativo según el sistema operativo."""
        print(f"🔌 [Voz-Rin]: Modo OFFLINE activo en {self.sistema_operativo}...")
        
        # === CASO 1: RESPALDO EN WINDOWS (NATIVO CON SAPI5) ===
        if self.sistema_operativo == "Windows" and self.engine_local:
            try:
                self.engine_local.say(texto)
                self.engine_local.runAndWait()
                return
            except Exception as e:
                print(f"❌ Error en motor nativo de Windows: {e}. Intentando fallback...")

        # === CASO 2: RESPALDO EN LINUX (ESPEAK TRADICIONAL) ===
        binario_espeak = "espeak" 
        comando = f'{binario_espeak} -v {self.espeak_lang} -s {self.espeak_speed} -p {self.espeak_pitch} "{texto}"'
        
        try:
            es_posix = False if self.sistema_operativo == "Windows" else True
            argumentos = shlex.split(comando, posix=es_posix)
            
            startupinfo = None
            if self.sistema_operativo == "Windows":
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            
            subprocess.run(argumentos, check=True, startupinfo=startupinfo)
        except Exception as e:
            print(f"❌ Error crítico en motor local alternativo: {e}")

    async def _hablar_edge(self, texto: str):
        print("🌐 [Voz-Rin]: Modo ONLINE activo. Generando voz neuronal...")
        try:
            comunicar = edge_tts.Communicate(texto, self.voz_edge)
            await comunicar.save(self.archivo_temporal)
            
            pygame.mixer.init()
            pygame.mixer.music.load(self.archivo_temporal)
            pygame.mixer.music.play()
            
            while pygame.mixer.music.get_busy():
                await asyncio.sleep(0.1)
                
            pygame.mixer.music.stop()
            pygame.mixer.quit()
            
            if os.path.exists(self.archivo_temporal):
                os.remove(self.archivo_temporal)
                
        except Exception as e:
            print(f"⚠️ Falló Edge-TTS en caliente. Rebotando a motor local... Motivo: {e}")
            # Redirige al nuevo método adaptativo
            self._hablar_local_offline(texto)

    def procesar_y_hablar(self, entrada_raw: str):
        texto_para_leer = ""
        try:
            datos = json.loads(entrada_raw)
            texto_para_leer = datos.get("leer", "").strip()
        except (json.JSONDecodeError, TypeError):
            texto_para_leer = entrada_raw.strip()

        if not texto_para_leer:
            print("⚠️ [Voz-Rin]: Nada para leer en esta respuesta.")
            return

        if self._hay_internet():
            asyncio.run(self._hablar_edge(texto_para_leer))
        else:
            self._hablar_local_offline(texto_para_leer)