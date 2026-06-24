import json
import os
from datetime import datetime

class ContextManager:
    """
    Gestiona la persistencia y lectura del archivo context.json 
    para mantener el estado de Rin.
    """
    def __init__(self, filepath="context.json"):
        self.filepath = filepath

    def leer_contexto(self):
        """Lee el estado actual de Rin desde el archivo JSON."""
        if not os.path.exists(self.filepath):
            return {}
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error leyendo el contexto: {e}")
            return {}

    def actualizar_contexto(self, nueva_data):
        """
        Actualiza partes específicas del contexto.
        'nueva_data' es un diccionario con las claves a actualizar.
        """
        contexto = self.leer_contexto()
        
        # Actualizamos recursivamente o sobrescribimos
        for key, value in nueva_data.items():
            contexto[key] = value
        
        # Guardamos el archivo actualizado
        try:
            with open(self.filepath, 'w', encoding='utf-8') as f:
                json.dump(contexto, f, indent=2, ensure_ascii=False)
            print(f"DEBUG: Contexto actualizado en {self.filepath}")
        except Exception as e:
            print(f"Error guardando el contexto: {e}")

    def registrar_accion(self, tarea, resultado):
        """Registra una tarea finalizada en la memoria_reciente."""
        contexto = self.leer_contexto()
        if "memoria_reciente" not in contexto:
            contexto["memoria_reciente"] = []
            
        entrada = {
            "tarea": tarea,
            "fecha": datetime.now().isoformat(),
            "resultado": resultado
        }
        
        contexto["memoria_reciente"].append(entrada)
        # Mantener solo las últimas 10 acciones para eficiencia
        contexto["memoria_reciente"] = contexto["memoria_reciente"][-10:]
        
        self.actualizar_contexto(contexto)