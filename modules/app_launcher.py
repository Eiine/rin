import subprocess
import shutil

class AppLauncher:
    def ejecutar(self, *args):
        if not args:
            return "No especificaste qué aplicación abrir."
        
        app_name = args[0]
        
        # shutil.which busca el ejecutable en el PATH del sistema
        if shutil.which(app_name):
            try:
                subprocess.Popen([app_name])
                return f"Iniciando {app_name} correctamente."
            except Exception as e:
                return f"Error al intentar abrir {app_name}: {str(e)}"
        else:
            return f"No pude encontrar la aplicación '{app_name}' en el sistema."