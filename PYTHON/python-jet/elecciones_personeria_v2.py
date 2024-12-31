from PyQt5.QtWidgets import (
    QApplication,
    QLabel,
    QVBoxLayout,
    QWidget,
    QMessageBox,
    QPushButton,
    QLineEdit,
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QStackedWidget
)
from PyQt5.QtGui import QPixmap, QColor, QFont, QPalette
from PyQt5.QtCore import Qt
import matplotlib.pyplot as plt
import json
import os


class ElectionApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Elecciones de Personería")
        self.setGeometry(100, 100, 800, 600)

        # Configuración de la paleta de colores para un diseño moderno
        self.setStyleSheet("""
            QWidget {
                background-color: #2E2E2E;
                color: white;
            }
            QPushButton {
                background-color: #4CAF50;
                border: 2px solid #4CAF50;
                border-radius: 10px;
                padding: 10px 20px;
                font-size: 16px;
                color: white;
                transition: background-color 0.3s ease;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QLineEdit {
                background-color: #444;
                border: 2px solid #666;
                border-radius: 5px;
                color: white;
                padding: 10px;
                font-size: 14px;
            }
            QDialog {
                background-color: #333;
                border-radius: 10px;
            }
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #FFF;
            }
        """)

        # Candidatos y votos
        self.candidates = {
            "Candidato 1": 0,
            "Candidato 2": 0,
            "Candidato 3": 0,
        }
        self.voting_enabled = False  # Bandera para habilitar/deshabilitar la votación

        # Layout principal
        self.layout = QVBoxLayout()

        # Agregar botones de control (todos requieren contraseña)
        self.add_protected_button("Iniciar Votación", self.enable_voting)
        self.add_protected_button("Reiniciar Contadores", self.reset_votes)
        self.add_protected_button("Resultados", self.show_results_chart)

        # Layout para las imágenes de los candidatos (horizontal)
        self.candidate_layout = QHBoxLayout()

        # Agregar imágenes de los candidatos
        self.candidate_labels = {}  # Diccionario para guardar las etiquetas de los candidatos
        for candidate in self.candidates.keys():
            self.add_candidate(candidate)

        # Añadir el layout de candidatos al layout principal
        self.layout.addLayout(self.candidate_layout)

        self.setLayout(self.layout)

    def add_protected_button(self, text, action):
        # Crear un botón que requiere contraseña antes de realizar su acción
        button = QPushButton(text)
        button.clicked.connect(lambda: self.prompt_for_password(action))
        self.layout.addWidget(button)

    def add_candidate(self, candidate_name):
        # Crear un widget para contener la imagen y el nombre
        candidate_widget = QWidget(self)
        candidate_layout = QVBoxLayout()

        # Crear una etiqueta para mostrar el nombre
        name_label = QLabel(candidate_name)
        name_label.setAlignment(Qt.AlignCenter)
        name_label.setStyleSheet("color: #4CAF50;")  # Modernizar el color del nombre
        candidate_layout.addWidget(name_label)

        # Crear una etiqueta para mostrar la imagen del candidato
        candidate_label = QLabel(self)
        image_path = f"{candidate_name}.jpg"  # Ruta de la imagen
        if os.path.exists(image_path):  # Comprobar si la imagen existe
            pixmap = QPixmap(image_path)
            pixmap = pixmap.scaled(200, 200, Qt.KeepAspectRatio)
            candidate_label.setPixmap(pixmap)
            candidate_label.setAlignment(Qt.AlignCenter)

            # Guardar referencia para habilitar/deshabilitar clics más tarde
            candidate_label.mousePressEvent = (
                lambda event, name=candidate_name: self.vote(name)
                if self.voting_enabled
                else None
            )
        else:
            candidate_label.setText(f"No se encontró la imagen de {candidate_name}")
            candidate_label.setAlignment(Qt.AlignCenter)

        # Añadir la etiqueta de la imagen al layout
        candidate_layout.addWidget(candidate_label)
        candidate_widget.setLayout(candidate_layout)

        # Añadir el widget con imagen y nombre al layout horizontal
        self.candidate_layout.addWidget(candidate_widget)

    def enable_voting(self):
        # Habilitar la votación
        self.voting_enabled = True
        msg = QMessageBox()
        msg.setWindowTitle("Votación Habilitada")
        msg.setText(
            "¡La votación ha comenzado! Ahora puedes votar haciendo clic en las imágenes de los candidatos."
        )
        msg.setIcon(QMessageBox.Information)
        msg.exec_()

    def reset_votes(self):
        # Reiniciar los contadores de votos
        for candidate in self.candidates.keys():
            self.candidates[candidate] = 0

        # Guardar los resultados reiniciados en el archivo JSON
        self.save_results()

        # Mostrar mensaje confirmando el reinicio
        msg = QMessageBox()
        msg.setWindowTitle("Contadores Reiniciados")
        msg.setText("¡Todos los contadores de votos han sido reiniciados a cero!")
        msg.setIcon(QMessageBox.Information)
        msg.exec_()

    def show_results_chart(self):
        # Crear un gráfico con los resultados
        candidates = list(self.candidates.keys())
        votes = list(self.candidates.values())

        plt.figure(figsize=(8, 6))
        plt.bar(candidates, votes, color=["#4CAF50", "#2196F3", "#FF9800"])
        plt.title("Resultados de las Elecciones", fontsize=16)
        plt.xlabel("Candidatos", fontsize=12)
        plt.ylabel("Votos", fontsize=12)
        plt.xticks(fontsize=10)
        plt.yticks(fontsize=10)

        # Mostrar el gráfico en una nueva ventana
        plt.show()

    def save_results(self):
        # Guardar resultados en un archivo JSON
        results_file = "resultados_votacion.json"
        with open(results_file, "w") as file:
            json.dump(self.candidates, file, indent=4)

    def vote(self, candidate_name):
        # Incrementar el conteo de votos
        self.candidates[candidate_name] += 1

        # Guardar resultados en un archivo JSON
        self.save_results()

        # Mostrar ventana emergente para confirmar el voto
        self.show_vote_dialog(candidate_name)

    def show_vote_dialog(self, candidate_name):
        # Ventana emergente personalizada
        dialog = QDialog(self)
        dialog.setWindowTitle("Confirmación de Voto")
        layout = QFormLayout()

        # Mensaje de información
        label = QLabel(f"¡Ya votaste por {candidate_name}!")
        layout.addWidget(label)

        # Cuadro de texto para ingresar el código
        code_input = QLineEdit()
        code_input.setEchoMode(QLineEdit.Password)
        layout.addRow("Ingresa el código para cerrar:", code_input)

        # Botón para validar el código
        validate_button = QPushButton("Validar")
        validate_button.clicked.connect(lambda: self.validate_code(dialog, code_input))
        layout.addWidget(validate_button)

        dialog.setLayout(layout)
        dialog.exec_()

    def validate_code(self, dialog, code_input):
        # Validar si el código es correcto
        if code_input.text() == "   ":
            dialog.accept()  # Cerrar la ventana
        else:
            QMessageBox.warning(dialog, "Código Incorrecto", "El código ingresado es incorrecto. Intenta de nuevo.")

    def prompt_for_password(self, action):
        # Solicitar la contraseña para ejecutar la acción
        dialog = QDialog(self)
        dialog.setWindowTitle("Autenticación Requerida")
        layout = QFormLayout()

        # Mensaje para ingresar la contraseña
        code_input = QLineEdit()
        code_input.setEchoMode(QLineEdit.Password)
        layout.addRow("Ingresa la contraseña para continuar:", code_input)

        # Botón para validar la contraseña
        validate_button = QPushButton("Validar")
        validate_button.clicked.connect(lambda: self.validate_action(dialog, code_input, action))
        layout.addWidget(validate_button)

        dialog.setLayout(layout)
        dialog.exec_()

    def validate_action(self, dialog, code_input, action):
        # Validar si la contraseña es correcta
        if code_input.text() == "asdf":
            dialog.accept()
            action()  # Ejecutar la acción solicitada
        else:
            QMessageBox.warning(dialog, "Contraseña Incorrecta", "La contraseña ingresada es incorrecta. Intenta de nuevo.")


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
