import speech_recognition as sr
import os
import difflib
import time

class DetectorPalabraClave:
    def __init__(self, palabra_clave="rin", idioma="es-AR"):
        self.reconocedor = sr.Recognizer()
        self.palabra_clave = palabra_clave.lower()
        self.idioma = idioma
        
        # ===== MEJORAS CRÍTICAS =====
        # Valores seguros que no causan AssertionError
        self.reconocedor.pause_threshold = 0.8  # Aumentado de 0.5 a 0.8
        self.reconocedor.energy_threshold = 300
        self.reconocedor.dynamic_energy_threshold = False
        
        # Control para calibrar solo una vez
        self._calibrado = False
        
        # Lista de variantes (esto es lo que tu orquestador intenta asignar)
        self.variantes = ["rin", "ren", "ran", "ron", "rina", "rins"]

    def _coincide_fuzzy(self, texto: str) -> bool:
        """
        DETECCIÓN MEJORADA:
        - Coincidencia exacta
        - Coincidencia con variantes predefinidas
        - Similitud fonética (para "rín", "ríin", etc.)
        """
        texto_limpio = texto.lower().strip()
        
        # Estrategia 1: Coincidencia exacta (más rápida)
        if self.palabra_clave in texto_limpio:
            return True
        
        # Estrategia 2: Coincidencia con variantes
        for variante in self.variantes:
            if variante in texto_limpio:
                return True
        
        # Estrategia 3: Similitud para palabras cortas (evita falsos con "interesante")
        if len(texto_limpio) <= 8:  # Solo palabras cortas como "rin", "rín", "riin"
            ratio = difflib.SequenceMatcher(None, texto_limpio, self.palabra_clave).ratio()
            if ratio > 0.75:  # 75% de similitud
                return True
        
        return False

    def esperar_activacion(self):
        """
        VERSIÓN MEJORADA:
        - Calibración única (no cada vez)
        - Timeouts reducidos para menor latencia
        - Manejo de errores robusto
        """
        print(f"📡 Centinela activo: Esperando que digas '{self.palabra_clave}'...")
        
        with sr.Microphone(int(os.getenv("MIC_INDEX", 0))) as origen:
            # Calibrar UNA SOLA VEZ (no en cada activación)
            if not self._calibrado:
                print("🔧 Calibrando ruido ambiente (solo una vez)...")
                try:
                    self.reconocedor.adjust_for_ambient_noise(origen, duration=0.5)
                except Exception as e:
                    print(f"⚠️ Error en calibración (usando valores por defecto): {e}")
                self._calibrado = True
                print(f"✨ Umbral de energía: {self.reconocedor.energy_threshold}")
            
            while True:
                try:
                    # Timeouts reducidos para respuesta más rápida
                    audio = self.reconocedor.listen(origen, timeout=0.8, phrase_time_limit=2)
                    texto = self.reconocedor.recognize_google(audio, language=self.idioma)
                    texto_limpio = texto.lower()
                    
                    # Usar la detección mejorada
                    if self._coincide_fuzzy(texto_limpio):
                        print(f"🔥 ¡Palabra clave '{self.palabra_clave}' DETECTADA! 🔥")
                        print(f"📝 Texto completo: '{texto}'")
                        return True
                        
                except sr.UnknownValueError:
                    continue  # No entendió, seguir escuchando
                except sr.WaitTimeoutError:
                    continue  # Silencio, seguir escuchando
                except sr.RequestError as e:
                    print(f"⚠️ Error de conexión: {e}. Reintentando...")
                    time.sleep(0.5)
                    continue
                except OSError as e:
                    print(f"⚠️ Error de audio: {e}")
                    time.sleep(0.5)
                    continue