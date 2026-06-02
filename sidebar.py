import tkinter as tk
from tkinter.scrolledtext import ScrolledText
import os
from PIL import Image, ImageTk  # Requiere: pip install Pillow

class FloatingSidebar:
    def __init__(self, width=380, height=650):
        self.width = width
        self.height = height
        
        # Inicialización del entorno gráfico en el hilo principal
        self.root = tk.Tk()
        self.root.withdraw()

        self.window = tk.Toplevel(self.root)
        self.window.withdraw()
        self.window.overrideredirect(True)
        self.window.attributes("-topmost", True)
        self.window.configure(bg="#111")

        # Puntero base para la referencia de la imagen
        self.imagen_tk = None 

        self._position()
        self._build_ui()

    def iniciar_interfaz(self):
        """Mantiene vivo el loop de la interfaz gráfica en el hilo principal."""
        self.root.mainloop()

    def _position(self):
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x = sw - self.width - 10
        y = int((sh - self.height) / 2)
        self.window.geometry(f"{self.width}x{self.height}+{x}+{y}")

    def _build_ui(self):
        fuente_titulo = ("sans-serif", 11, "bold")
        fuente_seccion = ("sans-serif", 10, "bold")
        fuente_texto = ("monospace", 10)

        # HEADER
        header = tk.Frame(self.window, bg="#111")
        header.pack(fill="x", pady=(0, 5), padx=10)

        title = tk.Label(
            header, text="🤖 Rin Assistant", fg="#eee", bg="#111",
            font=fuente_titulo
        )
        title.pack(side="left", pady=10)

        close_btn = tk.Button(
            header, text="✕", fg="#fff", bg="#222",
            command=self._close_app,
            relief="flat", width=3, cursor="hand2"
        )
        close_btn.pack(side="right", pady=10)

        # CONTENEDOR PRINCIPAL
        self.frame = tk.Frame(self.window, bg="#111")
        self.frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Secciones de Texto
        self.info = self._section(self.frame, "📚 Explicación / Info", 6, fuente_seccion, fuente_texto)
        self.metodo = self._section(self.frame, "💻 Código / Método", 10, fuente_seccion, fuente_texto)

        # SECCIÓN MULTIMEDIA (Label contenedor de imágenes)
        self.titulo_imagen = tk.Label(self.frame, text="🖼️ Visualización / Esquema", bg="#111", fg="#aaa", font=fuente_seccion)
        self.imagen_label = tk.Label(self.frame, bg="#1e1e1e", relief="flat")
        
        # Inicialmente los ocultamos del Layout manager (.pack_forget)
        self.titulo_imagen.pack_forget()
        self.imagen_label.pack_forget()

    def _section(self, parent, title, height, f_title, f_text):
        tk.Label(parent, text=title, bg="#111", fg="#aaa", font=f_title).pack(anchor="w", pady=(5, 2))

        box = ScrolledText(
            parent, height=height, wrap="word",
            bg="#1e1e1e", fg="#eee", insertbackground="white",
            font=f_text, relief="flat", padx=5, pady=5
        )
        box.pack(fill="x", pady=(0, 5))
        box.config(state="disabled")
        return box

    def show(self, data: dict):
        """Recibe el diccionario de datos y actualiza los widgets de forma asíncrona y segura."""
        def _update():
            self._clear()
            self.window.deiconify()
            self.window.lift()
            self.window.attributes("-topmost", True)

            # 1. Renderizar Texto (Info / Leer)
            texto_info = data.get("info") if data.get("info") else data.get("leer", "")
            if texto_info:
                self._insert(self.info, texto_info)

            # 2. Renderizar Código / Método
            if data.get("metodo"):
                self._insert(self.metodo, data["metodo"])

            # 3. 📌 PROCESAMIENTO ULTRA SEGURO DE IMAGEN (Fix de Garbage Collector)
            ruta_imagen = data.get("imagen")
            if ruta_imagen:
                r_imagen = str(ruta_imagen).strip()
                if os.path.exists(r_imagen):
                    try:
                        # Cargamos el archivo físico con Pillow
                        img = Image.open(r_imagen)
                        
                        # Ajustamos proporcionalmente al ancho de la barra
                        ancho_max = self.width - 30
                        w_percent = (ancho_max / float(img.size[0]))
                        h_size = int((float(img.size[1]) * float(w_percent)))
                        
                        # Remuestreo de alta calidad
                        img = img.resize((ancho_max, h_size), Image.Resampling.LANCZOS)
                        
                        # Generamos la estructura de píxeles compatible con Tkinter
                        foto = ImageTk.PhotoImage(img)
                        
                        # 🚨 AMARRE DE MEMORIA DUPLO: 
                        # Lo guardamos en la instancia de clase y en la propiedad interna del label widget
                        self.imagen_tk = foto
                        self.imagen_label.config(image=foto)
                        self.imagen_label.image = foto  # <--- Evita la recolección de basura
                        
                        # Posicionamos los elementos dinámicamente en el layout abajo de método
                        self.titulo_imagen.pack(anchor="w", pady=(5, 2))
                        self.imagen_label.pack(fill="x", pady=5)
                        
                        # Sincronizamos las tareas inactivas de la pantalla de X11 en Linux
                        self.window.update_idletasks()
                        print(f"🖼️ [Sidebar GUI]: Imagen inyectada con éxito: {r_imagen}")
                        
                    except Exception as e:
                        print(f"❌ Error al procesar imagen en UI: {e}")
                else:
                    print(f"⚠️ Alerta: No existe el archivo gráfico especificado en: {r_imagen}")

        # Delegamos la ejecución de la UI de forma segura al hilo principal
        self.root.after(0, _update)

    def _insert(self, widget, text):
        widget.config(state="normal")
        widget.insert("1.0", text)
        widget.config(state="disabled")

    def _clear(self):
        # Limpieza de búferes de texto
        for box in (self.info, self.metodo):
            box.config(state="normal")
            box.delete("1.0", tk.END)
            box.config(state="disabled")
            
        # Ocultamos la sección multimedia del layout y desvinculamos referencias
        self.titulo_imagen.pack_forget()
        self.imagen_label.pack_forget()
        self.imagen_label.config(image="")
        self.imagen_label.image = None
        self.imagen_tk = None

    # 📌 REVISÁ QUE ESTÉ EXACTAMENTE ASÍ AL FINAL DEL ARCHIVO:
    def _close_app(self):
        """Mata el proceso completo de forma segura al tocar la X"""
        os._exit(0)