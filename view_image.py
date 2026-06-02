import os
import subprocess
import shutil
import webbrowser

class WebImageViewer:

    def __init__(self, url):

        self.url = url

        try:

            webbrowser.open_new(self.url)

        except Exception as e:

            print(f"[Rin Viewer] Error: {e}")

    def cerrar(self):
        pass

    def cerrar(self):

        try:

            if self.proceso:
                self.proceso.terminate()

        except:
            pass