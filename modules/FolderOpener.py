import os
import subprocess
import platform
from pathlib import Path

class FolderOpener:
    """
    Módulo inteligente para BUSCAR y abrir carpetas locales.
    Compatible con ModuloExecutor y con logs de depuración.
    """

    def __init__(self, ruta_base=None):
        self.ruta_base = ruta_base if ruta_base else str(Path.home())
        print(f"DEBUG [FolderOpener]: Inicializado. Ruta base de búsqueda: {self.ruta_base}")

    def ejecutar(self, *args):
        """
        Interfaz estándar para ModuloExecutor.
        args[0] = nombre de la carpeta a buscar.
        """
        print(f"DEBUG [FolderOpener]: Método 'ejecutar' invocado. Argumentos recibidos: {args}")
        
        if not args:
            print("DEBUG [FolderOpener]: Error, no se recibieron argumentos.")
            return self._formatear_respuesta(False, "No se especificó un nombre de carpeta.")
        
        # --- LIMPIEZA DE SEGURIDAD ---
        # Si la IA envía una ruta tipo '/ruta/al/proyectos', extraemos solo 'proyectos'
        raw_name = args[0]
        nombre_carpeta = os.path.basename(raw_name.replace("/ruta/al/", ""))
        print(f"DEBUG [FolderOpener]: Nombre de carpeta limpio extraído: '{nombre_carpeta}'")
        
        # 1. Búsqueda inteligente
        ruta_encontrada = self._buscar_carpeta(nombre_carpeta)
        
        if not ruta_encontrada:
            print(f"DEBUG [FolderOpener]: No se encontró carpeta con nombre: '{nombre_carpeta}'")
            return self._formatear_respuesta(False, f"No encontré la carpeta '{nombre_carpeta}' en {self.ruta_base}")

        # 2. Intentar abrir
        print(f"DEBUG [FolderOpener]: Carpeta encontrada: '{ruta_encontrada}'. Intentando abrir...")
        exito = self._abrir_ruta(ruta_encontrada)
        
        if exito:
            print("DEBUG [FolderOpener]: Apertura exitosa.")
            return self._formatear_respuesta(True, f"Carpeta encontrada: {ruta_encontrada}")
        else:
            print("DEBUG [FolderOpener]: Fallo al intentar abrir la ruta.")
            return self._formatear_respuesta(False, f"Encontré '{nombre_carpeta}' pero el sistema denegó la apertura.")

    def _buscar_carpeta(self, nombre_carpeta: str):
        try:
            print(f"DEBUG [FolderOpener]: Escaneando recursivamente en {self.ruta_base}...")
            # Búsqueda recursiva insensible a mayúsculas
            for ruta in Path(self.ruta_base).rglob('*'):
                if ruta.is_dir() and ruta.name.lower() == nombre_carpeta.lower():
                    print(f"DEBUG [FolderOpener]: ¡Coincidencia confirmada!: {ruta}")
                    return str(ruta)
        except PermissionError:
            pass # Ignoramos carpetas del sistema sin acceso
        except Exception as e:
            print(f"DEBUG [FolderOpener]: Error inesperado durante la búsqueda: {str(e)}")
        return None

    def _abrir_ruta(self, ruta_completa: str):
        try:
            sistema = platform.system()
            print(f"DEBUG [FolderOpener]: Detectado SO: {sistema}. Abriendo...")
            
            if sistema == "Windows":
                os.startfile(ruta_completa)
            elif sistema == "Darwin":
                subprocess.Popen(["open", ruta_completa])
            else: # Linux
                subprocess.Popen(["xdg-open", ruta_completa])
            return True
        except Exception as e:
            print(f"DEBUG [FolderOpener]: Error al ejecutar comando del sistema: {str(e)}")
            return False

    def _formatear_respuesta(self, exito, mensaje):
        """
        Estructura el retorno esperado por ModuloExecutor.
        """
        if exito:
            return {
                "voz": "He accedido a la carpeta solicitada.",
                "ui_data": {
                    "mostrar": True,
                    "info": "Carpeta abierta",
                    "detalles_tecnicos": mensaje
                }
            }
        else:
            return {
                "voz": "Lo siento, tuve un problema al intentar completar esa tarea.",
                "ui_data": {
                    "mostrar": True,
                    "info": "Error al procesar",
                    "detalles_tecnicos": mensaje
                }
            }