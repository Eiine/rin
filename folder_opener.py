import os
import subprocess
import platform
from pathlib import Path

class FolderOpener:
    """
    Módulo para BUSCAR y abrir carpetas locales.
    """

    def __init__(self, ruta_base=None):
        self.ruta_base = ruta_base if ruta_base else str(Path.home())

    def ejecutar(self, nombre_carpeta: str):
        """
        Método unificado que retorna SIEMPRE un diccionario.
        """
        ruta_completa = self._buscar_carpeta_interna(nombre_carpeta)
        
        if not ruta_completa:
            return {"error": f"No se encontró la carpeta: {nombre_carpeta}"}

        # Intentamos abrir
        exito = self._abrir_ruta(ruta_completa)
        
        if exito:
            return {"carpeta_abierta": nombre_carpeta, "ruta": ruta_completa}
        else:
            return {"error": f"No se pudo abrir la ruta: {ruta_completa}"}

    def _buscar_carpeta_interna(self, nombre_carpeta: str):
        print(f"🔍 Buscando '{nombre_carpeta}' en {self.ruta_base}...")
        try:
            for ruta in Path(self.ruta_base).rglob('*'):
                if ruta.is_dir() and ruta.name.lower() == nombre_carpeta.lower():
                    print(f"✅ Carpeta encontrada: {ruta}")
                    return str(ruta)
        except Exception as e:
            print(f"⚠️ Error durante la búsqueda: {e}")
        return None

    def _abrir_ruta(self, ruta_completa: str) -> bool:
        try:
            sistema = platform.system()
            if sistema == "Windows":
                os.startfile(ruta_completa)
            elif sistema == "Darwin":
                subprocess.Popen(["open", ruta_completa])
            else:
                subprocess.Popen(["xdg-open", ruta_completa])
            print(f"📂 [FolderOpener]: Abriendo {ruta_completa}...")
            return True
        except Exception as e:
            print(f"❌ Error al intentar abrir la carpeta: {e}")
            return False