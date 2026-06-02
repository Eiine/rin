import os
from google import genai
from google.genai import types
from dotenv import load_dotenv
from groq import Groq  # Importamos Groq

load_dotenv()

class GeminiClient:
    def __init__(self, nombre_manifiesto: str = "manifest_1.txt"):
        self.client = genai.Client()
        self.groq_client = Groq(api_key=os.getenv("GROK_API"))
        
        self.pipeline_modelos = [
            "gemini-1.5-flash", # Ajustado: 1.5 es más estable actualmente
            "gemini-1.5-pro",
            "gemini-1.0-pro"
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

    def generar_respuesta(self, prompt: str) -> str:
        configuracion = types.GenerateContentConfig(
            system_instruction=self.system_instruction,
            temperature=0.4,
            response_mime_type="application/json"
        )

        # 1. Intentar con el Pipeline de Gemini
        for modelo in self.pipeline_modelos:
            try:
                print(f"🤖 [IA-Rin]: Consultando Gemini -> ({modelo})...")
                respuesta = self.client.models.generate_content(
                    model=modelo, contents=prompt, config=configuracion
                )
                return respuesta.text
            except Exception as e:
                print(f"⚠️ Gemini ({modelo}) falló: {str(e)[:50]}...")
                continue

        # 2. Si todo Gemini falló, intentar con Groq (Llama 3)
        print("🚀 [IA-Rin]: Todos los modelos de Google saturados. Probando con Groq...")
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
            return '{"leer": "Lo siento, todos mis motores están caídos.", "metodo": false}'

    def __call__(self, prompt: str) -> str:
        return self.generar_respuesta(prompt)