import tkinter as tk
from tkinter.scrolledtext import ScrolledText
import platform
import os
import sys

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

    def _position(self):
        self.sw = self.root.winfo_screenwidth()
        self.sh = self.root.winfo_screenheight()
        self.offset_x = 15 if platform.system() == "Windows" else 25
        self.x_visible = self.sw - self.width - self.offset_x
        self.y_pos = int((self.sh - self.height) / 2)
        self.window.geometry(f"{self.width}x{self.height}+{self.x_visible}+{self.y_pos}")

    def _build_ui(self):
        # HEADER CON BOTONES DE CONTROL
        header = tk.Frame(self.window, bg="#111")
        header.pack(fill="x", pady=5, padx=10)

        tk.Label(header, text="🤖 Rin Assistant", fg="#eee", bg="#111", font=("sans-serif", 11, "bold")).pack(side="left")

        # Botón CERRAR (Mata el proceso)
        btn_cerrar = tk.Button(header, text="✕", fg="#ff4444", bg="#222", command=self._matar_proceso, relief="flat", width=3)
        btn_cerrar.pack(side="right", padx=2)

        # Botón MINIMIZAR (Se oculta al lateral)
        btn_minimizar = tk.Button(header, text="─", fg="#fff", bg="#222", command=self.deslizar_ventana, relief="flat", width=3)
        btn_minimizar.pack(side="right", padx=2)

        self.frame = tk.Frame(self.window, bg="#111")
        self.frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        self.info = self._section(self.frame, "📚 Información", 10, ("sans-serif", 10, "bold"), ("monospace", 10))
        self.tecnica = self._section(self.frame, "💻 Detalles Técnicos", 15, ("sans-serif", 10, "bold"), ("monospace", 10))

    def _matar_proceso(self):
        """Cierra la ventana y termina el proceso completo del sistema."""
        self.root.destroy()
        os._exit(0) # Fuerza la salida inmediata del proceso

    def _build_tab(self):
        self.tab = tk.Toplevel(self.root)
        self.tab.withdraw()
        self.tab.overrideredirect(True)
        self.tab.attributes("-topmost", True)
        self.tab.configure(bg="#00ADB5")
        tab_w, tab_h = 12, 80
        tab_x = self.root.winfo_screenwidth() - tab_w
        tab_y = int((self.root.winfo_screenheight() - tab_h) / 2)
        self.tab.geometry(f"{tab_w}x{tab_h}+{tab_x}+{tab_y}")
        lbl = tk.Label(self.tab, text="⋮", fg="#fff", bg="#00ADB5", font=("sans-serif", 12, "bold"))
        lbl.pack(fill="both", expand=True)
        lbl.bind("<Button-1>", lambda e: self.deslizar_ventana())

    def deslizar_ventana(self):
        if self.estado == "visible":
            self.window.withdraw()
            self.tab.deiconify()
            self.estado = "oculta"
        else:
            self.tab.withdraw()
            self.window.deiconify()
            self.estado = "visible"

    def show(self, ui_data: dict):
        def _update():
            self.window.deiconify()
            self.window.lift()
            self._clear()
            if self.estado == "oculta": self.deslizar_ventana()
            if "info" in ui_data: self._insert(self.info, ui_data["info"])
            if "detalles_tecnicos" in ui_data: self._insert(self.tecnica, ui_data["detalles_tecnicos"])
        self.root.after(0, _update)

    def _insert(self, widget, text):
        widget.config(state="normal")
        widget.insert("1.0", text)
        widget.config(state="disabled")

    def _clear(self):
        for box in (self.info, self.tecnica):
            box.config(state="normal")
            box.delete("1.0", tk.END)
            box.config(state="disabled")

    def _section(self, parent, title, height, f_title, f_text):
        tk.Label(parent, text=title, bg="#111", fg="#aaa", font=f_title).pack(anchor="w", pady=(5, 2))
        box = ScrolledText(parent, height=height, wrap="word", bg="#1e1e1e", fg="#eee", font=f_text, relief="flat", padx=5, pady=5)
        box.pack(fill="both", expand=True, pady=(0, 5))
        box.config(state="disabled")
        return box

    def iniciar_interfaz(self):
        self.root.mainloop()