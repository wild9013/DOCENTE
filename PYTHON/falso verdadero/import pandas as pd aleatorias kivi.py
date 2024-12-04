import pandas as pd
import random
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.filechooser import FileChooser
from kivy.uix.popup import Popup

# Función para leer el archivo Excel
def leer_preguntas(archivo_excel):
    df = pd.read_excel(archivo_excel)
    preguntas = df.to_dict(orient='records')
    return preguntas

# Ventana para seleccionar el archivo
class FileSelectorPopup(Popup):
    def __init__(self, seleccionar_callback, **kwargs):
        super().__init__(**kwargs)
        self.title = "Selecciona el archivo de preguntas"
        layout = BoxLayout(orientation='vertical')
        self.filechooser = FileChooser()
        layout.add_widget(self.filechooser)

        boton_seleccionar = Button(text="Seleccionar")
        boton_seleccionar.bind(on_release=lambda x: seleccionar_callback(self.filechooser.path, self.filechooser.selection))
        layout.add_widget(boton_seleccionar)

        self.add_widget(layout)

# Ventana principal de las preguntas
class VentanaPreguntas(BoxLayout):
    def __init__(self, preguntas, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        self.preguntas = preguntas
        random.shuffle(self.preguntas)
        self.index_pregunta = 0
        self.crear_widgets()
        self.mostrar_pregunta()

    def crear_widgets(self):
        self.pregunta_label = Label(text="", font_size=34)
        self.add_widget(self.pregunta_label)

        botones_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=100)
        self.boton_verdadero = Button(text="Verdadero", font_size=32)
        self.boton_falso = Button(text="Falso", font_size=32)

        self.boton_verdadero.bind(on_release=lambda x: self.responder('V'))
        self.boton_falso.bind(on_release=lambda x: self.responder('F'))

        botones_layout.add_widget(self.boton_verdadero)
        botones_layout.add_widget(self.boton_falso)

        self.add_widget(botones_layout)

    def mostrar_pregunta(self):
        if self.index_pregunta < len(self.preguntas):
            pregunta = self.preguntas[self.index_pregunta]['Pregunta']
            self.pregunta_label.text = pregunta
        else:
            self.pregunta_label.text = "Has respondido todas las preguntas."
            self.boton_verdadero.disabled = True
            self.boton_falso.disabled = True

    def responder(self, respuesta_usuario):
        respuesta_correcta = self.preguntas[self.index_pregunta]['Respuesta']
        if respuesta_usuario == respuesta_correcta:
            print("¡Correcto!")
        else:
            print("Incorrecto.")
        self.index_pregunta += 1
        self.mostrar_pregunta()

# Aplicación principal
class PreguntasApp(App):
    def build(self):
        return FileSelectorPopup(self.seleccionar_archivo)

    def seleccionar_archivo(self, path, selection):
        if not selection:
            print("No se seleccionó ningún archivo.")
            return

        archivo_excel = selection[0]
        try:
            preguntas = leer_preguntas(archivo_excel)
        except Exception as e:
            print(f"Error al leer el archivo: {e}")
            return

        # Abrir la ventana de preguntas
        self.root.dismiss()  # Cerrar el selector de archivos
        self.root = VentanaPreguntas(preguntas)

if __name__ == "__main__":
    PreguntasApp().run()
