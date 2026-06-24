import mss
import pyautogui # Usamos esto para obtener la posición de la ventana activa fácilmente

class VisionCapture:
    def ejecutar(self, *args):
        # Captura la pantalla completa o el área activa de forma simplificada
        nombre_archivo = "temp_vision.png"
        
        try:
            # Captura toda la pantalla (o podrías definir un área específica)
            with mss.mss() as sct:
                # sct.monitors[1] es tu monitor principal
                sct.shot(mon=1, output=nombre_archivo)
                
            return f"Captura realizada correctamente: {nombre_archivo}"
        except Exception as e:
            return f"Error al capturar pantalla: {str(e)}"