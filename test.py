# Asegúrate de importar tu módulo desde la carpeta 'modules'
from modules.browser_player import BrowserPlayer

def test_puro():
    print("🚀 Iniciando test directo del método .ejecutar()...")
    
    # 1. Instanciamos la clase directamente
    modulo = BrowserPlayer()
    
    # 2. Llamamos a la función con un argumento de prueba
    cancion = "opening latino digimon"
    resultado = modulo.ejecutar(cancion)
    
    # 3. Validamos la salida
    print(f"📡 Resultado obtenido: {resultado}")

if __name__ == "__main__":
    test_puro()