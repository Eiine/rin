import os
import requests

class WikimediaSearcher:
    def __init__(self):
        """Inicializa el buscador de Wikimedia Commons. No requiere API Key."""
        self.base_url = "https://commons.wikimedia.org/w/api.php"

    def buscar_imagenes(self, query: str, cantidad: int = 3) -> list:
        """
        Busca esquemas, diagramas y archivos técnicos en Wikimedia Commons.
        Retorna una lista con las URLs directas de las imágenes encontradas.
        """
        # Parámetros para la API de MediaWiki
        parametros = {
            "action": "query",
            "format": "json",
            "generator": "search",
            "gsrsearch": f"filetype:bitmap|drawing {query}", # Filtramos para evitar PDFs o audios
            "gsrnamespace": 6,                               # Espacio de nombres 6 es exclusivo para Archivos/Multimedia
            "gsrlimit": cantidad,
            "prop": "imageinfo",
            "iiprop": "url",                                 # Pedimos la URL directa del archivo original
            "iiurlwidth": 800                                # Forzamos un ancho base óptimo para el renderizado
        }

        # Encabezado obligatorio por políticas de Wikimedia (User-Agent identificable)
        headers = {
            "User-Agent": "RinAssistantBot/1.0 (miguel_analista_sistemas; contacto_local)"
        }

        try:
            print(f"🔍 [Wikimedia Commons API]: Buscando material técnico para '{query}'...")
            respuesta = requests.get(self.base_url, params=parametros, headers=headers)
            
            if respuesta.status_code == 200:
                datos = respuesta.json()
                paginas = datos.get("query", {}).get("pages", {})
                
                links = []
                for id_pag, info in paginas.items():
                    info_imagen = info.get("imageinfo", [])
                    if info_imagen:
                        # Obtenemos la URL de la imagen procesada al ancho que le pedimos
                        url_directa = info_imagen[0].get("url")
                        if url_directa:
                            links.append(url_directa)
                
                return links
            else:
                print(f"❌ Error en la petición a Wikimedia. Código: {respuesta.status_code}")
                return []

        except Exception as e:
            print(f"❌ Fallo crítico al conectar con la API de Wikimedia: {e}")
            return []

# ==========================================
# 🔥 PRUEBA DE EJECUCIÓN DIRECTA
# ==========================================
if __name__ == "__main__":
    buscador = WikimediaSearcher()
    
    # Probemos con una búsqueda técnica real de sistemas
    termino = "astolfo" 
    resultados = buscador.buscar_imagenes(termino, cantidad=3)
    
    print(f"\n================ RESULTADOS TÉCNICOS PARA '{termino}' ================")
    if resultados:
        for indice, link in enumerate(resultados, 1):
            print(f"🔗 Link [{indice}]: {link}")
    else:
        print("❌ No se encontraron esquemas para este término.")
    print("=======================================================================\n")