import os
from google import genai
from google.genai import types
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

class GeminiClient:
    def __init__(self, nombre_manifiesto: str = "manifest_1.txt"):
        self.client = genai.Client()
        self.groq_client = Groq(api_key=os.getenv("GROK_API"))
        
        self.pipeline_modelos = [
            "gemini-1.5-flash",       # El mejor equilibrio entre velocidad y visión (Recomendado)
            "gemini-1.5-flash-8b",    # Extremadamente rápido y ligero, ideal si tienes cuotas bajas
            "gemini-1.5-pro"          # Solo úsalo si los anteriores fallan, es más pesado
]
        
        ruta_base = os.path.dirname(os.path.abspath(__file__))
        self.ruta_manifiesto = os.path.join(ruta_base, "manifest", nombre_manifiesto)
        self.system_instruction = self._load_manifest()

    def _load_manifest(self) -> str:
        try:
            with open(self.ruta_manifiesto, "r", encoding="utf-8") as f:
                return f.read().strip()
        except:
            return "Eres Rin. Responde siempre en JSON."

    def generar_respuesta(self, prompt: str, ruta_imagen: str = None) -> str:
        """
        Genera respuesta. Si ruta_imagen se proporciona, Rin usará su capacidad visual.
        """
        configuracion = types.GenerateContentConfig(
            system_instruction=self.system_instruction,
            temperature=0.4,
            response_mime_type="application/json"
        )

        # Preparar el contenido
        contenido = [prompt]
        
        # Si hay imagen, cargamos los bytes
        if ruta_imagen and os.path.exists(ruta_imagen):
            with open(ruta_imagen, "rb") as f:
                img_bytes = f.read()
                contenido.append(types.Part.from_bytes(data=img_bytes, mime_type="image/png"))

        # 1. Intentar con el Pipeline de Gemini (Soporta visión)
        for modelo in self.pipeline_modelos:
            try:
                print(f"🤖 [IA-Rin]: Consultando Gemini -> ({modelo})...")
                respuesta = self.client.models.generate_content(
                    model=modelo, 
                    contents=contenido, 
                    config=configuracion
                )
                return respuesta.text
            except Exception as e:
                print(f"⚠️ Gemini ({modelo}) falló: {str(e)[:50]}...")
                continue

        # 2. Si Gemini falló, intentar con Groq (NO soporta imagen, así que ignoramos imagen)
        print("🚀 [IA-Rin]: Todos los modelos de Google saturados. Probando con Groq (Sin visión)...")
        try:
            chat_completion = self.groq_client.chat.completions.create(
                messages=[
                    {"role": "system", "content": self.system_instruction},
                    {"role": "user", "content": prompt}
                ],
                model="llama-3.3-70b-versatile",
                response_format={"type": "json_object"}
            )
            return chat_completion.choices[0].message.content
        except Exception as e:
            print(f"❌ Error crítico en Groq: {e}")
            return '{"error": "Todos mis motores están caídos.", "metodo": false}'

    def __call__(self, prompt: str, ruta_imagen: str = None) -> str:
        return self.generar_respuesta(prompt, ruta_imagen)