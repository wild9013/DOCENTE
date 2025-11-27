import sys
import os
import json
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import (
    QApplication, QLabel, QVBoxLayout, QWidget, QMessageBox, 
    QPushButton, QLineEdit, QDialog, QFormLayout, QHBoxLayout, QFrame
)
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt

class ElectionApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistema de Votación Escolar")
        self.resize(900, 700) # Tamaño inicial
        
        # 1. SOLUCIÓN DE RUTAS: Obtener la carpeta donde está este script
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        print(f"Buscando imágenes en: {self.base_dir}")

        # Configuración de estilo (CSS moderno)
        self.setStyleSheet("""
            QWidget {
                background-color: #f0f0f0;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QLabel {
                color: #333;
            }
            /* Tarjetas de candidatos */
            QFrame {
                background-color: white;
                border-radius: 15px;
                border: 1px solid #ddd;
            }
            QFrame:hover {
                border: 2px solid #4CAF50;
                background-color: #e8f5e9;
            }
            /* Botones de control */
            QPushButton#AdminBtn {
                background-color: #607D8B;
                color: white;
                border-radius: 5px;
                padding: 8px;
                font-size: 14px;
            }
            QPushButton#AdminBtn:hover {
                background-color: #546E7A;
            }
        """)

        # Definir Candidatos y nombres de archivo de imagen
        # Asegúrate de que las imágenes estén en la misma carpeta que el script
        self.candidates_info = [
            {"name": "Candidato 1", "image": "candidato1.jpg"},
            {"name": "Candidato 2", "image": "candidato2.jpg"},
            {"name": "Candidato 3", "image": "candidato3.jpg"},
            {"name": "Voto en Blanco", "image": "blanco.jpg"} 
        ]

        # Inicializar conteo (se llenará con load_results)
        self.votes = {c["name"]: 0 for c in self.candidates_info}
        self.voting_enabled = False

        self.load_results()
        self.init_ui()

    def init_ui(self):
        self.main_layout = QVBoxLayout()
        self.main_layout.setSpacing(20)
        self.main_layout.setContentsMargins(40, 40, 40, 40)

        # Título
        title = QLabel("Elecciones de Personería 2025")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont('Arial', 24, QFont.Bold))
        title.setStyleSheet("color: #2c3e50; margin-bottom: 20px;")
        self.main_layout.addWidget(title)

        # Área de Candidatos
        self.candidates_layout = QHBoxLayout()
        self.candidates_layout.setSpacing(20)

        for info in self.candidates_info:
            self.add_candidate_card(info)

        self.main_layout.addLayout(self.candidates_layout)

        # Barra de Herramientas (Admin)
        self.admin_layout = QHBoxLayout()
        
        self.btn_start = QPushButton("Habilitar Votación")
        self.btn_start.setObjectName("AdminBtn")
        self.btn_start.clicked.connect(lambda: self.prompt_for_password(self.enable_voting))
        
        self.btn_reset = QPushButton("Reiniciar Todo")
        self.btn_reset.setObjectName("AdminBtn")
        self.btn_reset.setStyleSheet("background-color: #d32f2f;") # Rojo para peligro
        self.btn_reset.clicked.connect(lambda: self.prompt_for_password(self.reset_votes))

        self.btn_results = QPushButton("Ver Gráfica")
        self.btn_results.setObjectName("AdminBtn")
        self.btn_results.clicked.connect(lambda: self.prompt_for_password(self.show_results_chart))

        self.admin_layout.addStretch()
        self.admin_layout.addWidget(self.btn_start)
        self.admin_layout.addWidget(self.btn_results)
        self.admin_layout.addWidget(self.btn_reset)
        self.admin_layout.addStretch()

        self.main_layout.addLayout(self.admin_layout)
        self.setLayout(self.main_layout)

    def add_candidate_card(self, info):
        # Crear un marco (tarjeta) para cada candidato
        card = QFrame()
        card.setCursor(Qt.PointingHandCursor)
        card_layout = QVBoxLayout()
        
        # Ruta completa de la imagen
        image_path = os.path.join(self.base_dir, info["image"])
        
        lbl_image = QLabel()
        lbl_image.setAlignment(Qt.AlignCenter)
        lbl_image.setFixedSize(200, 200)
        
        # 2. CARGA DE IMAGEN SEGURA
        if os.path.exists(image_path):
            pixmap = QPixmap(image_path)
            lbl_image.setPixmap(pixmap.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            # Placeholder si no hay imagen
            lbl_image.setText(f"Sin imagen\n({info['image']})")
            lbl_image.setStyleSheet("background-color: #ddd; color: #555; border: 1px dashed #999;")
            print(f"AVISO: No se encontró {image_path}")

        lbl_name = QLabel(info["name"])
        lbl_name.setAlignment(Qt.AlignCenter)
        lbl_name.setFont(QFont('Arial', 14, QFont.Bold))
        
        card_layout.addWidget(lbl_image)
        card_layout.addWidget(lbl_name)
        card.setLayout(card_layout)

        # Evento de clic en la tarjeta entera
        card.mousePressEvent = lambda event: self.vote(info["name"])
        
        self.candidates_layout.addWidget(card)

    def vote(self, candidate_name):
        if not self.voting_enabled:
            QMessageBox.warning(self, "Espera", "La votación está cerrada por el administrador.")
            return

        self.votes[candidate_name] += 1
        self.save_results()
        
        # Feedback visual rápido
        msg = QMessageBox(self)
        msg.setWindowTitle("Voto Exitoso")
        msg.setText(f"¡Voto registrado para {candidate_name}!")
        msg.setIcon(QMessageBox.Information)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

    def enable_voting(self):
        self.voting_enabled = True
        QMessageBox.information(self, "Listo", "¡Urna abierta! Los estudiantes pueden votar.")

    def reset_votes(self):
        confirm = QMessageBox.question(self, "Peligro", "¿Borrar todos los votos a cero?", 
                                       QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.Yes:
            self.votes = {k: 0 for k in self.votes}
            self.save_results()
            QMessageBox.information(self, "Reiniciado", "Contadores a cero.")

    def show_results_chart(self):
        names = list(self.votes.keys())
        values = list(self.votes.values())
        
        plt.figure(figsize=(10, 6))
        bars = plt.bar(names, values, color=['#4CAF50', '#2196F3', '#FFC107', '#9E9E9E'])
        
        plt.title('Resultados en Tiempo Real', fontsize=16)
        plt.ylabel('Cantidad de Votos')
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        
        # Poner número sobre la barra
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height)}',
                    ha='center', va='bottom', fontsize=12, fontweight='bold')
        
        plt.tight_layout()
        plt.show()

    def save_results(self):
        with open(os.path.join(self.base_dir, "resultados.json"), "w") as f:
            json.dump(self.votes, f)

    def load_results(self):
        path = os.path.join(self.base_dir, "resultados.json")
        if os.path.exists(path):
            try:
                with open(path, "r") as f:
                    data = json.load(f)
                    # Actualizar solo si las claves coinciden (por seguridad)
                    for k, v in data.items():
                        if k in self.votes:
                            self.votes[k] = v
            except:
                print("Error leyendo archivo de votos.")

    def prompt_for_password(self, action_callback):
        dialog = QDialog(self)
        dialog.setWindowTitle("Seguridad")
        layout = QVBoxLayout()
        
        lbl = QLabel("Contraseña de Jurado:")
        txt = QLineEdit()
        txt.setEchoMode(QLineEdit.Password)
        btn = QPushButton("Acceder")
        
        layout.addWidget(lbl)
        layout.addWidget(txt)
        layout.addWidget(btn)
        dialog.setLayout(layout)

        def check():
            if txt.text() == "1234": # CONTRASEÑA
                dialog.accept()
                action_callback()
            else:
                QMessageBox.warning(dialog, "Error", "Contraseña incorrecta")

        btn.clicked.connect(check)
        dialog.exec_()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ElectionApp()
    window.show()
    sys.exit(app.exec_())