# modules/system/code_architect.py
import os
import shutil

class CodeArchitect:
    def __init__(self):
        self.base_path = os.getcwd()

    def refactorizar(self, nombre_archivo, nuevo_codigo):
        """
        Modifica el código de un archivo específico.
        """
        ruta_completa = os.path.join(self.base_path, nombre_archivo)
        
        if not os.path.exists(ruta_completa):
            return {"success": False, "error": f"Archivo {nombre_archivo} no encontrado."}

        try:
            # 1. Crear backup antes de tocar nada
            shutil.copy(ruta_completa, f"{ruta_completa}.bak")
            
            # 2. Escribir el nuevo código
            with open(ruta_completa, "w", encoding="utf-8") as f:
                f.write(nuevo_codigo)
                
            return {"success": True, "resultado": f"Archivo {nombre_archivo} actualizado correctamente. Backup creado."}
        except Exception as e:
            return {"success": False, "error": f"Error crítico al escribir: {str(e)}"}