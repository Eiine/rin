import tkinter as tk
from tkinter.scrolledtext import ScrolledText
import platform 

class FloatingSidebar:
    def __init__(self, width=380, height=650):
        self.width = width
        self.height = height
        self.estado = "oculta"
        
        self.root = tk.Tk()
        self.root.withdraw()

        self.window = tk.Toplevel(self.root)
        self.window.withdraw()
        self.window.overrideredirect(True)
        self.window.attributes("-topmost", True)
        self.window.configure(bg="#111")

        self._position()
        self._build_ui()
        self._build_tab() 

    def iniciar_interfaz(self):
        """Mantiene vivo el loop de la interfaz gráfica."""
        self.root.mainloop()

    def _position(self):
        self.sw = self.root.winfo_screenwidth()
        self.sh = self.root.winfo_screenheight()
        
        self.offset_x = 15 if platform.system() == "Windows" else 25
        self.x_visible = self.sw - self.width - self.offset_x
        self.y_pos = int((self.sh - self.height) / 2)
        self.x_oculto = self.sw - 4 
        
        self.window.geometry(f"{self.width}x{self.height}+{self.x_visible}+{self.y_pos}")
        
        if platform.system() != "Windows":
            self.window.bind("<Map>", lambda e: self.window.attributes("-topmost", True))

    def _build_ui(self):
        fuente_titulo = ("sans-serif", 11, "bold")
        fuente_seccion = ("sans-serif", 10, "bold")
        fuente_texto = ("monospace", 10)

        # HEADER
        header = tk.Frame(self.window, bg="#111")
        header.pack(fill="x", pady=(0, 5), padx=10)

        title = tk.Label(header, text="🤖 Rin Assistant", fg="#eee", bg="#111", font=fuente_titulo)
        title.pack(side="left", pady=10)

        close_btn = tk.Button(header, text="✕", fg="#fff", bg="#222", command=self.deslizar_ventana, relief="flat", width=3, cursor="hand2")
        close_btn.pack(side="right", pady=10)

        # CONTENEDOR PRINCIPAL
        self.frame = tk.Frame(self.window, bg="#111")
        self.frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self.info = self._section(self.frame, "📚 Explicación / Info", 6, fuente_seccion, fuente_texto)
        self.metodo = self._section(self.frame, "💻 Código / Método", 10, fuente_seccion, fuente_texto)

        # Etiqueta y Label para la imagen (se configuran externamente)
        self.titulo_imagen = tk.Label(self.frame, text="🖼️ Visualización / Esquema", bg="#111", fg="#aaa", font=fuente_seccion)
        self.imagen_label = tk.Label(self.frame, bg="#1e1e1e", relief="flat")
        
        self.titulo_imagen.pack_forget()
        self.imagen_label.pack_forget()

    def _build_tab(self):
        self.tab = tk.Toplevel(self.root)
        self.tab.withdraw()
        self.tab.overrideredirect(True)
        self.tab.attributes("-topmost", True)
        self.tab.configure(bg="#00ADB5")  

        tab_w, tab_h = 12, 80
        tab_x = self.sw - tab_w
        tab_y = int((self.sh - tab_h) / 2)
        self.tab.geometry(f"{tab_w}x{tab_h}+{tab_x}+{tab_y}")

        lbl = tk.Label(self.tab, text="⋮", fg="#fff", bg="#00ADB5", font=("sans-serif", 12, "bold"))
        lbl.pack(fill="both", expand=True)
        lbl.bind("<Button-1>", lambda e: self.deslizar_ventana())

    def deslizar_ventana(self):
        if self.estado == "visible":
            self._animar_slide(self.x_visible, self.x_oculto, 25, True)
        else:
            self.tab.withdraw()
            self.window.deiconify()
            self._animar_slide(self.x_oculto, self.x_visible, -25, False)

    def _animar_slide(self, actual, destino, paso, ocultar_al_final):
        if (paso > 0 and actual < destino) or (paso < 0 and actual > destino):
            actual += paso
            self.window.geometry(f"{self.width}x{self.height}+{actual}+{self.y_pos}")
            self.window.after(10, lambda: self._animar_slide(actual, destino, paso, ocultar_al_final))
        else:
            if ocultar_al_final:
                self.window.withdraw()
                self.tab.deiconify()
                self.estado = "oculta"
            else:
                self.window.lift()
                self.estado = "visible"

    def _section(self, parent, title, height, f_title, f_text):
        tk.Label(parent, text=title, bg="#111", fg="#aaa", font=f_title).pack(anchor="w", pady=(5, 2))
        box = ScrolledText(parent, height=height, wrap="word", bg="#1e1e1e", fg="#eee", insertbackground="white", font=f_text, relief="flat", padx=5, pady=5)
        box.pack(fill="x", pady=(0, 5))
        box.config(state="disabled")
        return box

    def show(self, data: dict, imagen_tk=None):
        def _update():
            
            
            self.window.deiconify()
            self.window.lift()
            self.window.attributes("-topmost", True)
            self._clear()
            self._clear()
            if self.estado == "oculta": self.deslizar_ventana()
            
            texto_info = data.get("leer", "").strip()
            if texto_info: self._insert(self.info, texto_info)
            if data.get("metodo"): self._insert(self.metodo, data["metodo"])

            if imagen_tk:
                self.imagen_label.config(image=imagen_tk)
                self.imagen_label.image = imagen_tk
                self.titulo_imagen.pack(anchor="w", pady=(5, 2))
                self.imagen_label.pack(fill="x", pady=5)

        self.root.after(0, _update)

    def _insert(self, widget, text):
        widget.config(state="normal")
        widget.insert("1.0", text)
        widget.config(state="disabled")

    def _clear(self):
        for box in (self.info, self.metodo):
            box.config(state="normal")
            box.delete("1.0", tk.END)
            box.config(state="disabled")
        self.titulo_imagen.pack_forget()
        self.imagen_label.pack_forget()