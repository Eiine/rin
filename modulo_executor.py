class ModuloExecutor:
    def __init__(self, catalogo):
        self.catalogo = catalogo

    def ejecutar_tarea(self, nombre_clase, argumentos):
        """
        Ejecuta de forma estandarizada los módulos.
        REGLA: Todos los módulos DEBEN implementar el método .ejecutar(*args).
        """
        if nombre_clase not in self.catalogo:
            return {"success": False, "error": f"Módulo {nombre_clase} no registrado."}

        try:
            # Instanciamos el módulo desde el catálogo
            instancia = self.catalogo[nombre_clase]()
            
            # Ejecución estandarizada
            if hasattr(instancia, "ejecutar"):
                resultado = instancia.ejecutar(*argumentos)
                return {"success": True, "resultado": resultado}
            else:
                return {
                    "success": False, 
                    "error": f"El módulo {nombre_clase} no cumple con la interfaz: falta el método .ejecutar()"
                }
                
        except Exception as e:
            return {"success": False, "error": f"Error crítico al ejecutar {nombre_clase}: {str(e)}"}