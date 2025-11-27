import sys
import os
import json
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import (
    QApplication, QLabel, QVBoxLayout, QWidget, QMessageBox, 
    QPushButton, QLineEdit, QDialog, QHBoxLayout, QFrame, 
    QScrollArea, QCheckBox, QFileDialog, QInputDialog # <--- AGREGADO QInputDialog
)
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt

# ==========================================
# VENTANA 1: CONFIGURACIÓN DE LA ELECCIÓN
# ==========================================
class ConfigDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Configuración de Elecciones")
        self.resize(600, 500)
        self.setStyleSheet("""
            QDialog { background-color: #f5f5f5; }
            QLabel { font-size: 14px; font-weight: bold; }
            QLineEdit { padding: 5px; border: 1px solid #ccc; border-radius: 4px; }
            QPushButton { background-color: #2196F3; color: white; border-radius: 5px; padding: 8px; font-weight: bold;}
            QPushButton:hover { background-color: #1976D2; }
            QFrame { background-color: white; border-radius: 5px; padding: 10px; margin-bottom: 5px; border: 1px solid #ddd;}
        """)

        self.candidates_data = [] 

        self.layout = QVBoxLayout()
        
        # Título
        lbl_intro = QLabel("Paso 1: Configurar Candidatos")
        lbl_intro.setAlignment(Qt.AlignCenter)
        lbl_intro.setStyleSheet("font-size: 18px; color: #333; margin-bottom: 10px;")
        self.layout.addWidget(lbl_intro)

        # Área de scroll
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setAlignment(Qt.AlignTop)
        self.scroll.setWidget(self.scroll_content)
        self.layout.addWidget(self.scroll)

        # Botón agregar
        self.btn_add = QPushButton("+ Agregar Candidato")
        self.btn_add.clicked.connect(self.add_candidate_row)
        self.btn_add.setStyleSheet("background-color: #4CAF50;")
        self.layout.addWidget(self.btn_add)

        # Opciones extra
        self.chk_blanco = QCheckBox("Incluir opción de 'Voto en Blanco'")
        self.chk_blanco.setChecked(True) 
        self.chk_blanco.setStyleSheet("font-size: 14px; margin-top: 10px;")
        self.layout.addWidget(self.chk_blanco)

        # Botón Iniciar
        self.btn_start = QPushButton("Guardar y Comenzar Votación >>")
        self.btn_start.clicked.connect(self.validate_and_start)
        self.btn_start.setStyleSheet("background-color: #FF9800; font-size: 16px; padding: 12px; margin-top: 15px;")
        self.layout.addWidget(self.btn_start)

        self.setLayout(self.layout)
        
        # Agregar 2 filas por defecto
        self.add_candidate_row()
        self.add_candidate_row()

    def add_candidate_row(self):
        row_widget = QFrame()
        row_layout = QHBoxLayout()
        
        lbl_name = QLabel(f"Candidato:")
        txt_name = QLineEdit()
        txt_name.setPlaceholderText("Nombre completo...")
        
        txt_photo = QLineEdit()
        txt_photo.setPlaceholderText("Ruta de imagen...")
        txt_photo.setReadOnly(True)
        
        btn_browse = QPushButton("Buscar Foto")
        btn_browse.setStyleSheet("background-color: #607D8B; font-size: 12px;")
        btn_browse.clicked.connect(lambda: self.browse_photo(txt_photo))

        btn_del = QPushButton("X")
        btn_del.setFixedSize(30, 30)
        btn_del.setStyleSheet("background-color: #f44336; padding:0;")
        btn_del.clicked.connect(lambda: self.delete_row(row_widget, txt_name, txt_photo))

        row_layout.addWidget(lbl_name)
        row_layout.addWidget(txt_name)
        row_layout.addWidget(txt_photo)
        row_layout.addWidget(btn_browse)
        row_layout.addWidget(btn_del)
        
        row_widget.setLayout(row_layout)
        self.scroll_layout.addWidget(row_widget)
        
        self.candidates_data.append({
            "widget": row_widget,
            "name_input": txt_name,
            "photo_input": txt_photo
        })

    def browse_photo(self, text_field):
        filename, _ = QFileDialog.getOpenFileName(self, "Seleccionar Foto", "", "Imágenes (*.png *.jpg *.jpeg)")
        if filename:
            text_field.setText(filename)

    def delete_row(self, widget, name_input, photo_input):
        self.scroll_layout.removeWidget(widget)
        widget.deleteLater()
        self.candidates_data = [d for d in self.candidates_data if d["widget"] != widget]

    def validate_and_start(self):
        final_list = []
        for item in self.candidates_data:
            name = item["name_input"].text().strip()
            path = item["photo_input"].text().strip()
            
            if name: 
                final_list.append({"name": name, "image": path})
        
        if len(final_list) < 1:
            QMessageBox.warning(self, "Error", "Debes agregar al menos un candidato.")
            return

        if self.chk_blanco.isChecked():
            final_list.append({"name": "Voto en Blanco", "image": "blank_vote_default"})

        self.final_candidates = final_list
        self.accept() 

    def get_data(self):
        return self.final_candidates


# ==========================================
# VENTANA 2: SISTEMA DE VOTACIÓN (PRINCIPAL)
# ==========================================
class ElectionApp(QWidget):
    def __init__(self, candidates_list):
        super().__init__()
        self.setWindowTitle("Sistema de Votación Escolar")
        self.resize(1000, 700)
        
        self.candidates_info = candidates_list
        
        self.setStyleSheet("""
            QWidget { background-color: #f0f0f0; font-family: 'Segoe UI', sans-serif; }
            QFrame { background-color: white; border-radius: 15px; border: 1px solid #ddd; }
            QFrame:hover { border: 3px solid #4CAF50; background-color: #e8f5e9; }
            QPushButton#AdminBtn { background-color: #607D8B; color: white; border-radius: 5px; padding: 10px; font-weight: bold;}
        """)

        self.votes = {c["name"]: 0 for c in self.candidates_info}
        self.load_results() 
        
        self.voting_enabled = False
        self.init_ui()

    def init_ui(self):
        self.main_layout = QVBoxLayout()
        
        title = QLabel("Elecciones de Personería")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont('Arial', 26, QFont.Bold))
        title.setStyleSheet("color: #2c3e50; margin: 20px;")
        self.main_layout.addWidget(title)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background: transparent; border: none;")
        
        container = QWidget()
        self.candidates_layout = QHBoxLayout(container)
        self.candidates_layout.setSpacing(30)
        self.candidates_layout.setAlignment(Qt.AlignCenter)

        for info in self.candidates_info:
            self.add_candidate_card(info)

        scroll.setWidget(container)
        self.main_layout.addWidget(scroll)

        admin_frame = QFrame()
        admin_frame.setStyleSheet("background-color: #37474F; border-radius: 0;")
        admin_layout = QHBoxLayout(admin_frame)
        
        btn_start = QPushButton("HABILITAR URNA")
        btn_start.setObjectName("AdminBtn")
        btn_start.setStyleSheet("background-color: #4CAF50;")
        btn_start.clicked.connect(lambda: self.prompt_for_password(self.enable_voting))
        
        btn_results = QPushButton("VER GRÁFICA")
        btn_results.setObjectName("AdminBtn")
        btn_results.clicked.connect(lambda: self.prompt_for_password(self.show_results_chart))
        
        btn_reset = QPushButton("REINICIAR TODO")
        btn_reset.setObjectName("AdminBtn")
        btn_reset.setStyleSheet("background-color: #d32f2f;")
        btn_reset.clicked.connect(lambda: self.prompt_for_password(self.reset_votes))

        admin_layout.addStretch()
        admin_layout.addWidget(btn_start)
        admin_layout.addWidget(btn_results)
        admin_layout.addWidget(btn_reset)
        admin_layout.addStretch()

        self.main_layout.addWidget(admin_frame)
        self.setLayout(self.main_layout)

    def add_candidate_card(self, info):
        card = QFrame()
        card.setCursor(Qt.PointingHandCursor)
        card.setFixedSize(250, 320)
        
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        
        lbl_image = QLabel()
        lbl_image.setFixedSize(200, 200)
        lbl_image.setAlignment(Qt.AlignCenter)
        lbl_image.setStyleSheet("background-color: #eee; border-radius: 10px;")
        
        pixmap = QPixmap(info["image"])
        if not pixmap.isNull():
            lbl_image.setPixmap(pixmap.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            if info["name"] == "Voto en Blanco":
                lbl_image.setText("BLANCO")
                lbl_image.setStyleSheet("background-color: #fff; color: #aaa; font-size: 30px; border: 2px dashed #ccc;")
            else:
                lbl_image.setText("Sin Foto")
        
        lbl_name = QLabel(info["name"])
        lbl_name.setAlignment(Qt.AlignCenter)
        lbl_name.setFont(QFont('Arial', 14, QFont.Bold))
        lbl_name.setWordWrap(True)
        
        layout.addWidget(lbl_image)
        layout.addWidget(lbl_name)
        card.setLayout(layout)

        card.mousePressEvent = lambda event: self.vote(info["name"])
        self.candidates_layout.addWidget(card)

    def vote(self, candidate_name):
        if not self.voting_enabled:
            QMessageBox.warning(self, "Espera", "La votación está cerrada. Espera a que el jurado la habilite.")
            return

        self.votes[candidate_name] += 1
        self.save_results()
        
        msg = QMessageBox(self)
        msg.setWindowTitle("Voto Registrado")
        msg.setText(f"Has votado por:\n\n{candidate_name}")
        msg.setIcon(QMessageBox.Information)
        msg.exec_()

    def enable_voting(self):
        self.voting_enabled = True
        QMessageBox.information(self, "Listo", "La votación está habilitada.")

    def reset_votes(self):
        if QMessageBox.question(self, "Atención", "¿Borrar todos los votos?", QMessageBox.Yes|QMessageBox.No) == QMessageBox.Yes:
            for k in self.votes: self.votes[k] = 0
            self.save_results()
            QMessageBox.information(self, "Hecho", "Urna vacía.")

    def show_results_chart(self):
        names = list(self.votes.keys())
        values = list(self.votes.values())
        plt.figure(figsize=(10, 6))
        bars = plt.bar(names, values, color='#2196F3')
        plt.title('Resultados Parciales')
        
        for bar in bars:
            yval = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2, yval, int(yval), ha='center', va='bottom', fontsize=12, fontweight='bold')
            
        plt.show()

    def save_results(self):
        try:
            with open("resultados_votacion.json", "w") as f:
                json.dump(self.votes, f)
        except: pass

    def load_results(self):
        if os.path.exists("resultados_votacion.json"):
            try:
                with open("resultados_votacion.json", "r") as f:
                    saved_data = json.load(f)
                    for name, count in saved_data.items():
                        if name in self.votes:
                            self.votes[name] = count
            except: pass

    # --- AQUÍ ESTABA EL ERROR, CORREGIDO A QInputDialog ---
    def prompt_for_password(self, action):
        pwd, ok = QInputDialog.getText(self, "Seguridad", "Contraseña:", QLineEdit.Password)
        if ok and pwd == "1234": # CONTRASEÑA
            action()
        elif ok:
            QMessageBox.warning(self, "Error", "Contraseña incorrecta")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    config_window = ConfigDialog()
    
    if config_window.exec_() == QDialog.Accepted:
        candidates_data = config_window.get_data()
        
        voting_window = ElectionApp(candidates_data)
        voting_window.show()
        
        sys.exit(app.exec_())
    else:
        sys.exit()