# modulo_executor.py

class ModuloExecutor:
    def __init__(self, catalogo):
        self.catalogo = catalogo

    def ejecutar_tarea(self, nombre_clase, argumentos):
        """
        Ejecuta de forma genérica cualquier módulo registrado.
        Retorna un dict con los datos actualizados o el error.
        """
        if nombre_clase not in self.catalogo:
            return {"error": f"Módulo {nombre_clase} no encontrado"}

        try:
            instancia = self.catalogo[nombre_clase]()
            
            # Asumimos que todos tienen un método .ejecutar() 
            # o mapeamos métodos específicos aquí si son distintos
            if hasattr(instancia, "ejecutar"):
                return instancia.ejecutar(*argumentos)
            elif hasattr(instancia, "abrir"): # Caso para FolderOpener
                return instancia.abrir(argumentos[0])
            elif hasattr(instancia, "ejecutar_busqueda"): # Caso para Wikimedia
                return instancia.ejecutar_busqueda(argumentos[0])
                
            return {"error": f"El módulo {nombre_clase} no tiene un método ejecutable reconocido"}
        
        except Exception as e:
            return {"error": str(e)}