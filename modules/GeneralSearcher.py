import os
import platform
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options

class GeneralSearcher:
    def ejecutar(self, *args):
        # 1. Extracción de argumentos
        termino = args[0]
        tipo = args[1] if len(args) > 1 else "texto"
        
        # 2. Construcción de URL
        if tipo == "imagenes":
            url = f"https://www.google.com/search?q={termino.replace(' ', '+')}&tbm=isch"
        else:
            url = f"https://www.google.com/search?q={termino.replace(' ', '+')}"
        
        # 3. Configuración del Driver (Reutilizando la lógica probada)
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        driver_name = "geckodriver.exe" if platform.system() == "Windows" else "geckodriver"
        driver_path = os.path.join(base_dir, "drivers", driver_name)

        options = Options()
        # Mismo perfil para mantener cookies y evitar detecciones
        perfil_path = "/home/miguel-notbock/.mozilla/firefox/x3a2dw1t.default-esr"
        options.add_argument("-profile")
        options.add_argument(perfil_path)
        
        # Capa anti-bot necesaria para que Google no bloquee la búsqueda
        options.set_preference("general.useragent.override", "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0")
        options.set_preference("dom.webdriver.enabled", False)
        
        service = Service(executable_path=driver_path)
        driver = webdriver.Firefox(service=service, options=options)
        
        # Ocultar marca de automatización
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        # 4. Acción
        driver.get(url)
        
        return f"Búsqueda de {tipo} iniciada para: {termino}"