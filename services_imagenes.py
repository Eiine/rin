import requests
import requests

class WikimediaSearcher:
    """
    Busca imágenes en Wikimedia Commons con filtros estrictos de calidad.
    Interfaz estandarizada para el Orquestador Rin.
    """

    def __init__(self):
        self.base_url = "https://commons.wikimedia.org/w/api.php"
        self.headers = {
            "User-Agent": "RinAgentSystem/2.0 (Multimedia Module)"
        }

    def ejecutar(self, criterio_busqueda: str) -> dict:
        """
        Método de interfaz unificada. 
        Recibe el criterio, ejecuta la búsqueda y devuelve un dict para el orquestador.
        """
        resultados = self._realizar_busqueda(criterio_busqueda)
        
        if not resultados:
            return {"error": f"No se encontraron imágenes para: {criterio_busqueda}"}

        # Tomamos el mejor resultado
        mejor = resultados[0]
        return {
            "imagen": mejor['url'],
            "imagen_titulo": mejor['titulo']
        }

    def _realizar_busqueda(self, criterio_busqueda: str) -> list:
        """Lógica interna de consulta a la API."""
        if not criterio_busqueda or not isinstance(criterio_busqueda, str):
            return []

        criterio_estricto = f"{criterio_busqueda} -logo -icon -flag -symbol -emblem -diagram -map -chart"

        parametros = {
            "action": "query",
            "format": "json",
            "generator": "search",
            "gsrsearch": criterio_estricto,
            "gsrnamespace": 6,
            "gsrlimit": 20,
            "prop": "imageinfo",
            "iiprop": "url|size|mime",
        }

        try:
            respuesta = requests.get(
                self.base_url,
                params=parametros,
                headers=self.headers,
                timeout=10
            )
            respuesta.raise_for_status()
            datos = respuesta.json()
            paginas = datos.get("query", {}).get("pages", {})
            resultados = []

            for _, info in paginas.items():
                imageinfo = info.get("imageinfo", [{}])[0]
                
                # Filtros de calidad
                if imageinfo.get("width", 0) < 300:
                    continue

                url = imageinfo.get("url", "")
                mime = imageinfo.get("mime", "")
                
                if "image" not in mime:
                    continue

                resultados.append({
                    "titulo": info.get("title", ""),
                    "url": url,
                    "es_vector": "svg" in mime
                })

            return sorted(resultados, key=lambda x: x['es_vector'])[:10]

        except Exception as e:
            print(f"❌ Error en WikimediaSearcher: {e}")
            return []

if __name__ == "__main__":
    # Prueba de funcionamiento local
    modulo = WikimediaSearcher()
    resultado = modulo.ejecutar("Astolfo Fate")
    print(resultado)