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
    QHBoxLayout
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
import matplotlib.pyplot as plt
import json
import os


class ElectionApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Elecciones de Personería")
        self.setGeometry(100, 100, 800, 600)

        # Configuración de estilo
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
        self.voting_enabled = False

        # Cargar resultados previos
        self.load_results()

        # Layout principal
        self.layout = QVBoxLayout()

        # Botones protegidos
        self.add_protected_button("Iniciar Votación", self.enable_voting)
        self.add_protected_button("Reiniciar Contadores", self.reset_votes)

        self.results_button = QPushButton("Resultados")
        self.results_button.clicked.connect(self.show_results_chart)
        self.layout.addWidget(self.results_button)

        # Layout para candidatos
        self.candidate_layout = QHBoxLayout()
        self.candidate_labels = {}
        for candidate in self.candidates.keys():
            self.add_candidate(candidate)
        self.layout.addLayout(self.candidate_layout)

        self.setLayout(self.layout)
        self.update_button_states()

    def add_protected_button(self, text, action):
        # Crear un botón que requiere contraseña antes de realizar su acción
        button = QPushButton(text)
        button.clicked.connect(lambda: self.prompt_for_password(action))
        self.layout.addWidget(button)

    def add_candidate(self, candidate_name):
        candidate_widget = QWidget(self)
        candidate_layout = QVBoxLayout()

        name_label = QLabel(candidate_name)
        name_label.setAlignment(Qt.AlignCenter)
        name_label.setStyleSheet("color: #4CAF50;")
        candidate_layout.addWidget(name_label)

        candidate_label = QLabel(self)
        image_path = f"{candidate_name}.jpg"
        if os.path.exists(image_path):
            pixmap = QPixmap(image_path)
            pixmap = pixmap.scaled(200, 200, Qt.KeepAspectRatio)
            candidate_label.setPixmap(pixmap)
            candidate_label.setAlignment(Qt.AlignCenter)
            candidate_label.mousePressEvent = (
                lambda event, name=candidate_name: self.vote(name)
                if self.voting_enabled
                else None
            )
        else:
            candidate_label.setText(f"No se encontró la imagen de {candidate_name}")
            candidate_label.setAlignment(Qt.AlignCenter)

        candidate_layout.addWidget(candidate_label)
        candidate_widget.setLayout(candidate_layout)
        self.candidate_layout.addWidget(candidate_widget)

    def enable_voting(self):
        self.voting_enabled = True
        QMessageBox.information(self, "Votación Habilitada",
                                "¡La votación ha comenzado! Ahora puedes votar haciendo clic en las imágenes de los candidatos.")

    def reset_votes(self):
        reply = QMessageBox.question(self, "Confirmar Reinicio",
                                     "¿Estás seguro de que deseas reiniciar todos los contadores de votos?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            for candidate in self.candidates.keys():
                self.candidates[candidate] = 0
            self.save_results()
            QMessageBox.information(self, "Contadores Reiniciados", "Todos los contadores se han reiniciado a cero.")
        self.update_button_states()

    def show_results_chart(self):
        candidates = list(self.candidates.keys())
        votes = list(self.candidates.values())

        plt.figure(figsize=(8, 6))
        bars = plt.bar(candidates, votes, color=["#4CAF50", "#2196F3", "#FF9800"])

        for bar, vote in zip(bars, votes):
            plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.2, str(vote),
                     ha="center", fontsize=12, color="black", weight="bold")

        plt.title("Resultados de las Elecciones", fontsize=16)
        plt.xlabel("Candidatos", fontsize=12)
        plt.ylabel("Votos", fontsize=12)
        plt.xticks(fontsize=10)
        plt.yticks(fontsize=10)
        plt.grid(axis="y", linestyle="--", alpha=0.7)
        plt.tight_layout()
        plt.show()

    def vote(self, candidate_name):
        self.candidates[candidate_name] += 1
        self.save_results()
        QMessageBox.information(self, "Voto Registrado", f"¡Tu voto por el candidato ha sido registrado!")
        self.update_button_states()

    def save_results(self):
        try:
            with open("resultados_votacion.json", "w") as file:
                json.dump(self.candidates, file, indent=4)
        except IOError:
            QMessageBox.critical(self, "Error", "No se pudo guardar los resultados. Verifica los permisos del archivo.")

    def load_results(self):
        try:
            if os.path.exists("resultados_votacion.json"):
                with open("resultados_votacion.json", "r") as file:
                    self.candidates.update(json.load(file))
        except (json.JSONDecodeError, FileNotFoundError):
            print("No se pudieron cargar resultados previos. Se inicializarán los votos en cero.")

    def update_button_states(self):
        total_votes = sum(self.candidates.values())
        self.results_button.setEnabled(total_votes > 0)

    def prompt_for_password(self, action):
        dialog = QDialog(self)
        dialog.setWindowTitle("Autenticación Requerida")
        layout = QFormLayout()

        code_input = QLineEdit()
        code_input.setEchoMode(QLineEdit.Password)
        layout.addRow("Ingresa la contraseña para continuar:", code_input)

        validate_button = QPushButton("Validar")
        validate_button.clicked.connect(lambda: self.validate_action(dialog, code_input, action))
        layout.addWidget(validate_button)

        dialog.setLayout(layout)
        dialog.exec_()

    def validate_action(self, dialog, code_input, action):
        if code_input.text() == "asdf":
            dialog.accept()
            action()
        else:
            QMessageBox.warning(dialog, "Contraseña Incorrecta", "La contraseña ingresada es incorrecta. Intenta de nuevo.")


# Ejecutar la aplicación
if __name__ == "__main__":
    app = QApplication([])
    window = ElectionApp()
    window.show()
    app.exec_()
