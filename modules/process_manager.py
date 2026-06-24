import psutil

class ProcessManager:
    def ejecutar(self, *args):
        if not args:
            return "No especificaste qué programa cerrar."
        
        nombre_programa = args[0].lower()
        procesos_cerrados = []
        
        # Iteramos sobre todos los procesos activos
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                # Comprobamos si el nombre del proceso contiene lo que pidió el usuario
                if nombre_programa in proc.info['name'].lower():
                    pid = proc.info['pid']
                    proc.terminate() # Enviamos señal de terminación (más seguro que kill -9)
                    procesos_cerrados.append(str(pid))
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        
        if procesos_cerrados:
            return f"He cerrado el programa. Procesos terminados (PID): {', '.join(procesos_cerrados)}"
        else:
            return f"No encontré ningún proceso activo que coincida con '{nombre_programa}'."