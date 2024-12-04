import tkinter as tk
from tkinter import messagebox
import random
from docx import Document
import pandas as pd

# Cargar datos desde un archivo Excel
file_path = "preguntas.xlsx"
data = pd.read_excel(file_path)
data = data.astype(str)  # Convierte todos los valores en cadenas de texto

# Crear una instancia de Tk
window = tk.Tk()
window.title("Juego Trivia")

# Variables
question_index = 0
correct_answers = 0
answer_var = tk.StringVar()
responses = []  # Para almacenar las respuestas del estudiante
student_name = ""  # Variable para almacenar el nombre del estudiante

# Función para mostrar la pregunta
def show_question():
    if question_index < len(data):
        # Obtener las opciones mezcladas
        options = [data["Respuesta Correcta"][question_index], data["R1"][question_index], data["R2"][question_index], data["R3"][question_index]]
        random.shuffle(options)

        # Actualizar el texto de la pregunta y las opciones
        question_label.config(text=data["Pregunta"][question_index])
        for i in range(4):
            radio_buttons[i].config(text=options[i], value=options[i])
        update_status()
    else:
        # Calcular el porcentaje de respuestas correctas
        percentage = (correct_answers / len(data)) * 100
        # Mostrar porcentaje de respuestas correctas
        messagebox.showinfo("Fin del juego", 
                            f"Juego terminado. Respondiste {correct_answers} preguntas correctas de {len(data)}.\n"
                            f"Porcentaje de respuestas correctas: {percentage:.2f}%")
        save_responses_to_word(percentage)  # Guardar respuestas al finalizar
        window.destroy()

# Función para actualizar el estado de la pregunta
def update_status():
    status_label.config(text=f"Pregunta {question_index+1} de {len(data)}")

# Función para manejar la respuesta
def handle_answer():
    global question_index, correct_answers
    selected_answer = answer_var.get()
    correct_answer = data["Respuesta Correcta"][question_index]
    responses.append((data["Pregunta"][question_index], selected_answer, correct_answer))  # Guardar la respuesta del estudiante
    
    if selected_answer == correct_answer:
        correct_answers += 1
    else:
        messagebox.showerror("Respuesta Incorrecta", f"Incorrecto! La respuesta correcta era: {correct_answer}")
    
    question_index += 1  # Actualiza el índice para la próxima pregunta
    show_question()

# Función para guardar las respuestas en un archivo de Word
def save_responses_to_word(percentage):
    doc = Document()
    doc.add_heading('Respuestas del Estudiante', level=1)
    doc.add_heading('Nombre del Estudiante:', level=2)
    doc.add_paragraph(student_name)
    
    doc.add_heading('Porcentaje de Respuestas Correctas:', level=2)
    doc.add_paragraph(f"{percentage:.2f}%")
    
    for question, student_answer, correct_answer in responses:
        doc.add_heading('Pregunta:', level=2)
        doc.add_paragraph(question)
        doc.add_heading('Respuesta del Estudiante:', level=2)
        doc.add_paragraph(student_answer)
        doc.add_heading('Respuesta Correcta:', level=2)
        doc.add_paragraph(correct_answer)
        doc.add_paragraph()  # Añadir una línea en blanco

    doc.save('respuestas_estudiante.docx')

# Función para iniciar el juego
def start_game():
    global student_name
    student_name = name_entry.get()  # Capturar el nombre del estudiante
    if not student_name:
        messagebox.showwarning("Nombre Requerido", "Por favor, ingresa tu nombre antes de comenzar.")
    else:
        name_frame.pack_forget()  # Ocultar el marco del nombre
        question_frame.pack()     # Mostrar el marco de preguntas
        show_question()          # Mostrar la primera pregunta al iniciar el juego

# Widgets para ingresar el nombre del estudiante
name_frame = tk.Frame(window)
name_label = tk.Label(name_frame, text="Ingresa tu nombre:")
name_label.pack(pady=(20, 5))
name_entry = tk.Entry(name_frame)
name_entry.pack(pady=5)
start_button = tk.Button(name_frame, text="Comenzar", command=start_game)
start_button.pack(pady=20)
name_frame.pack(pady=20)

# Widgets para las preguntas
question_frame = tk.Frame(window)
question_label = tk.Label(question_frame, text="", wraplength=400)
question_label.pack(pady=(20, 10))

radio_buttons = []
for _ in range(4):
    rb = tk.Radiobutton(question_frame, text="", variable=answer_var, wraplength=300)
    rb.pack(anchor="w")
    radio_buttons.append(rb)

answer_button = tk.Button(question_frame, text="Responder", command=handle_answer)
answer_button.pack(pady=20)

status_label = tk.Label(question_frame, text="")
status_label.pack()

# Iniciar el bucle principal de la interfaz gráfica
window.mainloop()
