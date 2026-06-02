import requests

class WikimediaSearcher:
    """
    Busca imágenes en Wikimedia Commons con filtros estrictos de calidad.
    """

    def __init__(self):
        self.base_url = "https://commons.wikimedia.org/w/api.php"
        self.headers = {
            "User-Agent": "RinAgentSystem/2.0 (Multimedia Module)"
        }

    def ejecutar_busqueda(self, criterio_busqueda: str) -> list:
        if not criterio_busqueda or not isinstance(criterio_busqueda, str):
            return []

        # Mejoramos el criterio: añadimos negaciones para descartar ruido
        # El operador '-' excluye resultados que contengan esas palabras
        criterio_estricto = f"{criterio_busqueda} -logo -icon -flag -symbol -emblem -diagram -map -chart"

        parametros = {
            "action": "query",
            "format": "json",
            "generator": "search",
            "gsrsearch": criterio_estricto,
            "gsrnamespace": 6,
            "gsrlimit": 20, # Traemos más para filtrar mejor
            "prop": "imageinfo",
            "iiprop": "url|size|mime", # Solicitamos MIME y tamaño
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
                
                # 1. Filtro de Tamaño: Descartamos imágenes minúsculas (< 300px ancho)
                if imageinfo.get("width", 0) < 300:
                    continue

                url = imageinfo.get("url", "")
                titulo = info.get("title", "")

                # 2. Filtro de formato: Priorizamos imágenes reales sobre archivos de audio/pdf
                mime = imageinfo.get("mime", "")
                if "image" not in mime:
                    continue

                resultados.append({
                    "titulo": titulo,
                    "url": url,
                    "es_vector": "svg" in mime
                })

            # Orden: Priorizamos imágenes reales, dejamos los SVG al final si prefieres píxeles
            # o los subimos si el visor externo los maneja bien.
            return sorted(resultados, key=lambda x: x['es_vector'])[:10]

        except Exception as e:
            print(f"❌ Error crítico en WikimediaSearcher: {e}")
            return []

if __name__ == "__main__":
    modulo = WikimediaSearcher()
    # Prueba con una búsqueda más limpia
    resultados = modulo.ejecutar_busqueda("Astolfo Fate")

    print(f"\n=== RESULTADOS PARA 'Astolfo Fate' ===\n")
    for r in resultados:
        print(f"Titulo: {r['titulo']}")
        print(f"URL:    {r['url']}")
        print("-" * 50)