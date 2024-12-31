from PyQt5.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget, QMessageBox
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
import json
import os

class ElectionApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Elecciones de Personería")
        self.setGeometry(100, 100, 400, 400)

        # Candidatos y votos
        self.candidates = {
            "Candidato 1": 0,
            "Candidato 2": 0,
            "Candidato 3": 0,
        }

        # Layout principal
        self.layout = QVBoxLayout()

        # Agregar imágenes de los candidatos
        for candidate in self.candidates.keys():
            self.add_candidate(candidate)

        self.setLayout(self.layout)

    def add_candidate(self, candidate_name):
        # Crear una etiqueta para mostrar la imagen del candidato
        candidate_label = QLabel(self)
        pixmap = QPixmap(f"{candidate_name}.jpg")  # Usa imágenes con nombres "Candidato 1.png", "Candidato 2.png", etc.
        pixmap = pixmap.scaled(150, 150, Qt.KeepAspectRatio)
        candidate_label.setPixmap(pixmap)
        candidate_label.setAlignment(Qt.AlignCenter)

        # Conectar el clic a la función de votación
        candidate_label.mousePressEvent = lambda event, name=candidate_name: self.vote(name)

        self.layout.addWidget(candidate_label)

    def vote(self, candidate_name):
        # Incrementar el conteo de votos
        self.candidates[candidate_name] += 1

        # Guardar resultados en un archivo JSON
        self.save_results()

        # Mostrar mensaje en una nueva ventana
        msg = QMessageBox()
        msg.setWindowTitle("Voto registrado")
        msg.setText(f"Ya votaste por {candidate_name}")
        msg.setIcon(QMessageBox.Information)
        msg.exec_()

    def save_results(self):
        # Guardar resultados en un archivo JSON
        results_file = "resultados_votacion.json"
        with open(results_file, "w") as file:
            json.dump(self.candidates, file, indent=4)

# Ejecutar la aplicación
if __name__ == "__main__":
    # Verificar si existe el archivo de resultados y cargarlo
    results_file = "resultados_votacion.json"
    if os.path.exists(results_file):
        with open(results_file, "r") as file:
            existing_results = json.load(file)
    else:
        existing_results = {}

    app = QApplication([])
    window = ElectionApp()

    # Si hay resultados previos, cargarlos
    if existing_results:
        window.candidates.update(existing_results)

    window.show()
    app.exec_()

