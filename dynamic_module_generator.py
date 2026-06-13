import os
import json

class DynamicModuleGenerator:
    def __init__(self, directory="./modules/dynamic"):
        self.directory = directory
        os.makedirs(self.directory, exist_ok=True)
        self.registry_path = os.path.join(self.directory, "registry.json")
        self._asegurar_registro()

    def _asegurar_registro(self):
        if not os.path.exists(self.registry_path):
            with open(self.registry_path, "w") as f:
                json.dump({}, f)

    def registrar_modulo(self, nombre, codigo, metadata):
        """
        Registra el módulo, limpia el formato del código y maneja el registro JSON.
        """
        archivo_path = os.path.join(self.directory, f"{nombre.lower()}.py")
        
        # 1. Limpieza de formato: Convierte los '\n' literales del JSON en saltos de línea reales
        # Esto soluciona el problema de la "línea única" que recibes de la IA
        codigo_formateado = codigo.replace("\\n", "\n").replace("\\t", "\t")
        
        with open(archivo_path, "w") as f:
            f.write(codigo_formateado)
            
        # 2. Lectura segura del registro
        try:
            with open(self.registry_path, "r") as f:
                content = f.read().strip()
                registry = json.loads(content) if content else {}
        except json.JSONDecodeError:
            registry = {}
            
        # 3. Actualizar registro y guardar
        registry[nombre] = {
            "path": os.path.abspath(archivo_path),
            "metadata": metadata
        }
        
        with open(self.registry_path, "w") as f:
            json.dump(registry, f, indent=4)
            
        print(f"✅ Módulo '{nombre}' registrado y formateado correctamente.")
        return True