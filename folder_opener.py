import os
import subprocess
import platform
from pathlib import Path

class FolderOpener:
    """
    Módulo para BUSCAR y abrir carpetas locales.
    Busca de forma recursiva e insensible a mayúsculas/minúsculas.
    """

    def __init__(self, ruta_base=None):
        # Si no se especifica ruta_base, busca desde la raíz del usuario (C:\Users\TuUsuario)
        # ¡Cuidado! Buscar desde "C:\\" puede ser muy lento.
        self.ruta_base = ruta_base if ruta_base else str(Path.home())
        # Si quieres buscar en todo el disco duro (C:\), descomenta la línea de abajo
        # self.ruta_base = "C:\\"

    def buscar_carpeta(self, nombre_carpeta: str):
        """
        Busca una carpeta por su nombre (insensible a mayúsculas) dentro de self.ruta_base.
        Retorna la ruta completa de la PRIMERA coincidencia encontrada.
        """
        print(f"🔍 Buscando '{nombre_carpeta}' en {self.ruta_base}...")
        try:
            # .rglob('*') busca en todas las subcarpetas recursivamente
            # Filtramos solo los directorios y comparamos el nombre sin importar mayúsculas
            for ruta in Path(self.ruta_base).rglob('*'):
                if ruta.is_dir() and ruta.name.lower() == nombre_carpeta.lower():
                    print(f"✅ Carpeta encontrada: {ruta}")
                    return str(ruta)
        except PermissionError:
            # Es normal tener errores de permisos en carpetas del sistema como 'AppData' o 'System32'
            pass
        except Exception as e:
            print(f"⚠️ Error durante la búsqueda: {e}")
        
        print(f"❌ No se encontró la carpeta '{nombre_carpeta}'.")
        return None

    def abrir(self, nombre_carpeta: str):
        """
        Busca la carpeta y si la encuentra, la abre.
        """
        # 1. Buscar la carpeta
        ruta_completa = self.buscar_carpeta(nombre_carpeta)
        
        if not ruta_completa:
            return False

        # 2. Abrir la carpeta (misma lógica multiplataforma)
        try:
            sistema = platform.system()
            
            if sistema == "Windows":
                os.startfile(ruta_completa)
            elif sistema == "Darwin":  # macOS
                subprocess.Popen(["open", ruta_completa])
            else:  # Linux
                subprocess.Popen(["xdg-open", ruta_completa])
                
            print(f"📂 [FolderOpener]: Abriendo {ruta_completa}...")
            return True
            
        except Exception as e:
            print(f"❌ Error al intentar abrir la carpeta: {e}")
            return False


# Prueba
if __name__ == "__main__":
    opener = FolderOpener()
    
    # Buscará 'Documentos' aunque escribas 'documentos' o 'DOCUMENTOS'
    opener.abrir("documentos") 