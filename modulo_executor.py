# modulo_executor.py

class ModuloExecutor:
    def __init__(self, catalogo):
        self.catalogo = catalogo

    def ejecutar_tarea(self, nombre_clase, argumentos):
        if nombre_clase not in self.catalogo:
            return {"success": False, "error": f"Módulo {nombre_clase} no encontrado"}

        try:
            instancia = self.catalogo[nombre_clase]()
            
            # Intentamos ejecutar según el patrón de diseño del módulo
            if hasattr(instancia, "ejecutar"):
                res = instancia.ejecutar(*argumentos)
            elif hasattr(instancia, "abrir"):
                res = instancia.abrir(argumentos[0])
            elif hasattr(instancia, "ejecutar_busqueda"):
                res = instancia.ejecutar_busqueda(argumentos[0])
            else:
                return {"success": False, "error": f"Módulo {nombre_clase} sin método ejecutable"}
                
            return {"success": True, "resultado": res}
        
        except Exception as e:
            return {"success": False, "error": str(e)}