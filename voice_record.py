import threading
import json
import requests
import speech_recognition as sr
import os
import time

from view_image import WebImageViewer

# Módulos del sistema
from key import DetectorPalabraClave
from voice_text import TranscriptorAudio
from services_ia import GeminiClient
from voice_output import RinVoz
from sidebar import FloatingSidebar
from services_imagenes import WikimediaSearcher
from folder_opener import FolderOpener  # <-- NUEVO IMPORT


class AsistenteOrquestador:

    def __init__(self, sidebar_instance):

        self.sidebar = sidebar_instance

        self.centinela = DetectorPalabraClave(
            palabra_clave="rin",
            idioma="es-AR"
        )

        self.transcriptor = TranscriptorAudio(
            idioma="es-AR"
        )

        self.ia = GeminiClient(
            "manifest_1.txt"
        )

        self.motor_voz = RinVoz(
            forzar_local=False
        )

        self.reconocedor_orden = sr.Recognizer()
        self.reconocedor_orden.pause_threshold = 6.0

        # Catálogo de módulos escalable (AHORA CON DOS MÓDULOS)
        self.catalogo_modulos = {
            "WikimediaSearcher": WikimediaSearcher,
            "FolderOpener": FolderOpener  # <-- NUEVO MÓDULO
        }

    def capturar_orden(self):
        """
        Escucha el micrófono para capturar la orden del usuario.
        """

        with sr.Microphone(
            int(os.getenv("MIC_INDEX", 0))
        ) as origen:

            print("\n🔊 [Asistente]: Te escucho...")

            self.reconocedor_orden.adjust_for_ambient_noise(
                origen,
                duration=0.5
            )

            try:

                return self.reconocedor_orden.listen(
                    origen,
                    timeout=5,
                    phrase_time_limit=10
                )

            except sr.WaitTimeoutError:

                return None

    def iniciar_bucle(self):
        """
        Bucle principal de escucha y orquestación.
        """

        print("🚀 Orquestador iniciado correctamente.")

        while True:

            # --------------------------------------------------
            # 1. Esperar palabra clave
            # --------------------------------------------------

            self.centinela.esperar_activacion()

            # --------------------------------------------------
            # 2. Capturar orden
            # --------------------------------------------------

            audio_orden = self.capturar_orden()

            if not audio_orden:
                continue

            peticion_texto = self.transcriptor.transcribir(
                audio_orden
            )

            if not peticion_texto:
                continue

            if peticion_texto.startswith("["):
                continue

            print(
                f"👤 [Usuario]: {peticion_texto}"
            )

            respuesta_json = self.ia(
                peticion_texto
            )

            try:

                datos_dict = json.loads(
                    respuesta_json
                )

            except Exception:

                datos_dict = {
                    "leer": respuesta_json,
                    "metodo": False,
                    "imagen": None
                }

            # --------------------------------------------------
            # 3. Motor de ejecución de módulos (CORREGIDO)
            # --------------------------------------------------

            ejecutar_modulo = datos_dict.get(
                "ejecutar_modulo"
            )

            if isinstance(
                ejecutar_modulo,
                dict
            ):

                nombre_clase = ejecutar_modulo.get(
                    "clase"
                )

                argumentos = ejecutar_modulo.get(
                    "args",
                    []
                )

                if (
                    nombre_clase in self.catalogo_modulos
                    and argumentos
                ):

                    print(
                        f"⚙️ [Orquestador]: Ejecutando módulo -> "
                        f"{nombre_clase}"
                    )

                    try:

                        instancia_clase = (
                            self.catalogo_modulos[
                                nombre_clase
                            ]()
                        )

                        # --------------------------------------
                        # WikimediaSearcher
                        # --------------------------------------

                        if nombre_clase == "WikimediaSearcher":

                            resultados = (
                                instancia_clase.ejecutar_busqueda(
                                    argumentos[0]
                                )
                            )

                            if resultados:

                                mejor_resultado = (
                                    resultados[0]
                                )

                                print(
                                    f"🔗 [Orquestador]: Link inyectado: "
                                    f"{mejor_resultado['url']}"
                                )

                                print(
                                    f"🖼️ [Orquestador]: Título: "
                                    f"{mejor_resultado['titulo']}"
                                )

                                datos_dict["imagen"] = (
                                    mejor_resultado["url"]
                                )

                                datos_dict["imagen_titulo"] = (
                                    mejor_resultado["titulo"]
                                )

                            else:

                                print(
                                    "⚠️ [Orquestador]: "
                                    "No se encontraron imágenes."
                                )

                        # --------------------------------------
                        # FolderOpener (NUEVO)
                        # --------------------------------------

                        elif nombre_clase == "FolderOpener":

                            # El módulo FolderOpener tiene método 'abrir'
                            # que recibe el nombre de la carpeta
                            resultado = instancia_clase.abrir(
                                argumentos[0]  # nombre_carpeta
                            )

                            if resultado:
                                print(
                                    f"📂 [Orquestador]: Carpeta abierta exitosamente."
                                )
                                # Opcional: agregar confirmación al dict
                                datos_dict["carpeta_abierta"] = argumentos[0]
                            else:
                                print(
                                    f"❌ [Orquestador]: No se pudo abrir la carpeta '{argumentos[0]}'"
                                )

                    except Exception as e:

                        print(
                            f"❌ Error en módulo "
                            f"{nombre_clase}: {e}"
                        )

            # --------------------------------------------------
            # 4. Voz
            # --------------------------------------------------

            self.motor_voz.procesar_y_hablar(
                respuesta_json
            )

            # --------------------------------------------------
            # 5. Sidebar
            # --------------------------------------------------

            self.sidebar.show(
                datos_dict
            )

            # --------------------------------------------------
            # 6. Visualizador de imágenes
            # --------------------------------------------------

            link_imagen = datos_dict.get(
                "imagen"
            )

            if link_imagen:

                try:

                    visor = WebImageViewer(
                        link_imagen
                    )

                except Exception as e:

                    print(
                        f"❌ Error al abrir visor: {e}"
                    )


# ==================================================
# ARRANQUE DEL SISTEMA
# ==================================================

if __name__ == "__main__":

    interfaz = FloatingSidebar()

    asistente = AsistenteOrquestador(
        sidebar_instance=interfaz
    )

    hilo_audio = threading.Thread(
        target=asistente.iniciar_bucle,
        daemon=True
    )

    hilo_audio.start()

    try:

        interfaz.iniciar_interfaz()

    except KeyboardInterrupt:

        print(
            "\n👋 Sistema cerrado correctamente."
        )