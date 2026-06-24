import os
import platform
import time
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class BrowserPlayer:
    def ejecutar(self, *args):
        if not args:
            return "No se especificó qué reproducir."
        
        # 1. Definir la ruta local al driver dentro del proyecto
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        driver_name = "geckodriver.exe" if platform.system() == "Windows" else "geckodriver"
        driver_path = os.path.join(base_dir, "drivers", driver_name)

        if not os.path.exists(driver_path):
            return f"Error: No se encontró el driver en {driver_path}"
        
        MI_PLAYLIST = "https://www.youtube.com/watch?v=c-fLfLXqyas&list=PL61M0q4ynSbafJ43CwNiAGbTfQsSp_Num"
        cancion = args[0].lower()
        
        options = Options()
        options.add_argument("-profile")
        options.add_argument("/home/miguel-notbock/.mozilla/firefox/x3a2dw1t.default-esr")
        
        # 2. Usar el servicio con la ruta local en lugar de GeckoDriverManager
        service = Service(executable_path=driver_path)
        driver = webdriver.Firefox(service=service, options=options)
        
        driver.set_window_size(1024, 768)
        driver.set_window_position(-2000, 0)
        
        try:
            if "lista" in cancion or "playlist" in cancion:
                driver.get(MI_PLAYLIST)
            else:
                # Búsqueda de video
                url = f"https://www.youtube.com/results?search_query={args[0].replace(' ', '+')}"
                driver.get(url)
                
                # --- MEJORA: Espera a que carguen los resultados ---
                wait = WebDriverWait(driver, 15)
                primer_video = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "ytd-video-renderer a#video-title")))
                primer_video.click()

            # --- BUCLE DE ESPERA INTELIGENTE ---
            for i in range(30):
                time.sleep(1)
                try:
                    # Intentar saltar anuncio
                    skip_btn = driver.find_element(By.CLASS_NAME, "ytp-skip-ad-button")
                    if skip_btn:
                        skip_btn.click()
                except:
                    pass
                
                # Intentar dar play
                driver.execute_script("""
                    var video = document.querySelector('video');
                    if (video && video.paused) {
                        video.muted = false;
                        video.play();
                    }
                """)
                
                # Verificación de reproducción
                if driver.execute_script("return document.querySelector('video') && document.querySelector('video').paused == false"):
                    break
            
            return f"Reproduciendo: {args[0]}"
            
        except Exception as e:
            try: driver.quit()
            except: pass
            return f"Error en la ejecución: {str(e)}"