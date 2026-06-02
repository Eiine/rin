import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Cargamos el archivo .env al arrancar
load_dotenv()

class GeminiClient:
    def __init__(self, nombre_manifiesto: str = "manifest_1.txt"):
        """
        Inicializa el cliente de Gemini configurando un modelo principal
        y un modelo de respaldo en caso de fallos.
        """
        self.client = genai.Client()
        
        # 📌 DEFINIMOS LA CADENA DE MODELOS
        self.modelo_principal = "gemini-2.5-flash"
        self.modelo_respaldo = "gemini-2.5-pro"
        
        # Construimos la ruta dinámica hacia la carpeta 'manifest/'
        ruta_base = os.path.dirname(os.path.abspath(__file__))
        self.ruta_manifiesto = os.path.join(ruta_base, "manifest", nombre_manifiesto)
        
        # Cargamos las instrucciones del archivo
        self.system_instruction = self._load_manifest()

    def _load_manifest(self) -> str:
        """Lee el archivo de texto del manifiesto de forma segura."""
        try:
            with open(self.ruta_manifiesto, "r", encoding="utf-8") as f:
                return f.read().strip()
        except FileNotFoundError:
            print(f"⚠️ Advertencia: No se encontró el manifiesto en '{self.ruta_manifiesto}'. Usando configuración básica.")
            return "Eres Rin. Responde siempre en JSON."

    def generar_respuesta(self, prompt: str) -> str:
        """
        Intenta generar la respuesta con el modelo principal.
        Si falla, conmuta automáticamente al modelo de respaldo.
        """
        # Configuración base obligatoria para asegurar el JSON de Rin
        configuracion = types.GenerateContentConfig(
            system_instruction=self.system_instruction,
            temperature=0.4,
            response_mime_type="application/json"
        )

        # 🚀 INTENTO 1: Con el modelo rápido (Flash)
        try:
            print(f"🤖 [Rin]: Consultando a modelo principal ({self.modelo_principal})...")
            respuesta = self.client.models.generate_content(
                model=self.modelo_principal,
                contents=prompt,
                config=configuracion
            )
            return respuesta.text

        except Exception as error_principal:
            # Si el modelo principal falla, atrapamos el error y saltamos al plan B
            print(f"⚠️ Alerta: Falló el modelo principal. Motivo: {error_principal}")
            print(f"🔄 Conmutando automáticamente al modelo de respaldo ({self.modelo_respaldo})...")
            
            # 🚀 INTENTO 2: Con el modelo de respaldo (Pro)
            try:
                respuesta_respaldo = self.client.models.generate_content(
                    model=self.modelo_respaldo,
                    contents=prompt,
                    config=configuracion
                )
                print(f"✅ Continuidad asegurada con éxito mediante {self.modelo_respaldo}.")
                return respuesta_respaldo.text
                
            except Exception as error_respaldo:
                # Si ambos modelos fallan (por ejemplo, si te quedaste sin internet)
                return (
                    f'{{"leer": "Lo siento, ambos motores de procesamiento fallaron.", '
                    f'"metodo": false, '
                    f'"imagenes": false, '
                    f'"info": "Error Principal: {str(error_principal)}. Error Respaldo: {str(error_respaldo)}"}}'
                )

    def __call__(self, prompt: str) -> str:
        return self.generar_respuesta(prompt)