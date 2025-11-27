from tkinter import Tk, Label, PhotoImage, Button, Toplevel, messagebox, simpledialog, Frame
from PIL import Image, ImageTk
import os

class ElectionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Elecciones de Personería")
        self.root.geometry("800x600")
        self.candidates = {"Candidato 1": 0, "Candidato 2": 0, "Candidato 3": 0}
        self.voting_enabled = False

        # Layout principal
        self.main_frame = Frame(root)
        self.main_frame.pack(fill="both", expand=True)

        # Botones
        self.add_protected_button("Iniciar Votación", self.enable_voting)
        self.add_protected_button("Reiniciar Contadores", self.reset_votes)
        self.add_protected_button("Resultados", self.show_results_chart)

        # Layout para los candidatos
        self.candidate_frame = Frame(root)
        self.candidate_frame.pack()

        # Agregar candidatos
        for candidate in self.candidates.keys():
            self.add_candidate(candidate)

    def add_protected_button(self, text, action):
        button = Button(self.main_frame, text=text, command=lambda: self.prompt_for_password(action))
        button.pack(pady=10)

    def add_candidate(self, candidate_name):
        frame = Frame(self.candidate_frame)
        frame.pack(side="left", padx=10, pady=10)

        # Mostrar nombre del candidato
        name_label = Label(frame, text=candidate_name)
        name_label.pack()

        # Cargar imagen con Pillow
        image_path = f"{candidate_name}.jpg"
        if os.path.exists(image_path):
            try:
                img = Image.open(image_path)
                img = img.resize((150, 150))  # Redimensionar la imagen
                photo = ImageTk.PhotoImage(img)
                image_label = Label(frame, image=photo)
                image_label.image = photo  # Guardar una referencia para evitar que se borre
                image_label.pack()
                image_label.bind("<Button-1>", lambda event, name=candidate_name: self.vote(name) if self.voting_enabled else None)
            except Exception as e:
                error_label = Label(frame, text=f"Error al cargar {candidate_name}")
                error_label.pack()
        else:
            error_label = Label(frame, text=f"Imagen no encontrada: {candidate_name}")
            error_label.pack()

    def enable_voting(self):
        self.voting_enabled = True
        messagebox.showinfo("Votación Habilitada", "La votación ha comenzado. Puedes votar haciendo clic en las imágenes.")

    def reset_votes(self):
        for candidate in self.candidates.keys():
            self.candidates[candidate] = 0
        messagebox.showinfo("Contadores Reiniciados", "Los votos se han reiniciado.")

    def show_results_chart(self):
        votes = list(self.candidates.values())
        candidates = list(self.candidates.keys())
        print("Resultados:", dict(zip(candidates, votes)))
        messagebox.showinfo("Resultados", f"{dict(zip(candidates, votes))}")

    def vote(self, candidate_name):
        self.candidates[candidate_name] += 1
        messagebox.showinfo("Voto Registrado", f"¡Has votado por {candidate_name}!")

    def prompt_for_password(self, action):
        password = simpledialog.askstring("Contraseña", "Ingresa la contraseña:", show="*")
        if password == "asdf":  # Cambia la contraseña según sea necesario
            action()
        else:
            messagebox.showerror("Error", "Contraseña incorrecta.")


if __name__ == "__main__":
    root = Tk()
    app = ElectionApp(root)
    root.mainloop()
