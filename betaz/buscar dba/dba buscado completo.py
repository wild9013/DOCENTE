import tkinter as tk
from tkinter import filedialog, messagebox
import json

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("DBA Matemáticas - Buscar Evidencias")
        self.datos = None
        
        # Frame principal
        self.main_frame = tk.Frame(self.root, padx=10, pady=10)
        self.main_frame.pack(fill="both", expand=True)
        
        # Botón para abrir archivo
        self.btn_abrir = tk.Button(self.main_frame, text="Abrir archivo", command=self.abrir_archivo)
        self.btn_abrir.pack(pady=5)
        
        # Frame para selección de grado
        self.frame_grado = tk.Frame(self.main_frame)
        self.frame_grado.pack(fill="x", pady=5)
        
        tk.Label(self.frame_grado, text="Grado:").pack(side="left")
        self.grado_var = tk.StringVar()
        self.grado_menu = tk.OptionMenu(self.frame_grado, self.grado_var, "")
        self.grado_menu.pack(side="left")
        self.grado_var.trace("w", self.actualizar_dbas)
        
        # Frame para listas
        self.frame_listas = tk.Frame(self.main_frame)
        self.frame_listas.pack(fill="both", expand=True, pady=5)
        
        # Listbox para DBAs
        self.frame_dbas = tk.Frame(self.frame_listas)
        self.frame_dbas.pack(side="left", fill="y", padx=5)
        tk.Label(self.frame_dbas, text="DBAs").pack()
        self.lista_dbas = tk.Listbox(self.frame_dbas, width=50, height=10)
        self.lista_dbas.pack(fill="y")
        self.lista_dbas.bind("<<ListboxSelect>>", self.actualizar_evidencias)
        
        # Listbox para Evidencias
        self.frame_evidencias = tk.Frame(self.frame_listas)
        self.frame_evidencias.pack(side="left", fill="y", padx=5)
        tk.Label(self.frame_evidencias, text="Evidencias de Aprendizaje").pack()
        self.lista_evidencias = tk.Listbox(self.frame_evidencias, width=50, height=10)
        self.lista_evidencias.pack(fill="y")
        self.lista_evidencias.bind("<<ListboxSelect>>", self.mostrar_evidencia)
        
        # Área de texto para mostrar evidencia seleccionada
        self.frame_texto = tk.Frame(self.main_frame)
        self.frame_texto.pack(fill="both", expand=True, pady=5)
        tk.Label(self.frame_texto, text="Detalles de la Evidencia").pack()
        self.texto_evidencia = tk.Text(self.frame_texto, height=4, wrap="word")
        self.texto_evidencia.pack(fill="both", expand=True)
        
        # Nuevo frame para mostrar DBA y Evidencia seleccionados en la parte inferior
        self.frame_seleccion = tk.Frame(self.main_frame, bd=2, relief="groove")
        self.frame_seleccion.pack(fill="x", pady=10)
        
        # Label para DBA seleccionado
        tk.Label(self.frame_seleccion, text="DBA Seleccionado:", font=("Arial", 10, "bold")).pack(anchor="w")
        self.label_dba = tk.Label(self.frame_seleccion, text="", wraplength=600, justify="left")
        self.label_dba.pack(anchor="w", padx=5)
        
        # Label para Evidencia seleccionada
        tk.Label(self.frame_seleccion, text="Evidencia Seleccionada:", font=("Arial", 10, "bold")).pack(anchor="w", pady=(5, 0))
        self.label_evidencia = tk.Label(self.frame_seleccion, text="", wraplength=600, justify="left")
        self.label_evidencia.pack(anchor="w", padx=5)
        
    def abrir_archivo(self):
        archivo = filedialog.askopenfilename(filetypes=[("Archivos JSON", "*.json")])
        if archivo:
            try:
                with open(archivo, "r", encoding="utf-8") as f:
                    self.datos = json.load(f)
                grados = sorted(set(item["Grado"] for item in self.datos))
                self.grado_menu["menu"].delete(0, "end")
                for grado in grados:
                    self.grado_menu["menu"].add_command(label=grado, command=lambda g=grado: self.grado_var.set(g))
                self.grado_var.set(grados[0] if grados else "")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo abrir el archivo: {e}")
                
    def actualizar_dbas(self, *args):
        if not self.datos:
            return
        grado = self.grado_var.get()
        self.lista_dbas.delete(0, tk.END)
        self.lista_evidencias.delete(0, tk.END)
        self.texto_evidencia.delete(1.0, tk.END)
        self.label_dba.config(text="")
        self.label_evidencia.config(text="")
        dbas = [item for item in self.datos if item["Grado"] == grado]
        for item in sorted(dbas, key=lambda x: int(x["DBA"])):
            self.lista_dbas.insert(tk.END, f"DBA {item['DBA']}: {item['Enunciado_DBA']}")
            
    def actualizar_evidencias(self, event):
        if not self.datos:
            return
        seleccion = self.lista_dbas.curselection()
        if not seleccion:
            return
        indice_dba = seleccion[0]
        grado = self.grado_var.get()
        dbas = [item for item in self.datos if item["Grado"] == grado]
        dba_seleccionado = sorted(dbas, key=lambda x: int(x["DBA"]))[indice_dba]
        self.lista_evidencias.delete(0, tk.END)
        for evidencia in dba_seleccionado["Evidencias_de_Aprendizaje"]:
            self.lista_evidencias.insert(tk.END, evidencia)
        # Actualizar el label de DBA seleccionado
        self.label_dba.config(text=dba_seleccionado["Enunciado_DBA"])
        self.label_evidencia.config(text="")
        self.texto_evidencia.delete(1.0, tk.END)
        
    def mostrar_evidencia(self, event):
        seleccion = self.lista_evidencias.curselection()
        if not seleccion:
            return
        indice_evidencia = seleccion[0]
        evidencia = self.lista_evidencias.get(indice_evidencia)
        self.texto_evidencia.delete(1.0, tk.END)
        self.texto_evidencia.insert(tk.END, evidencia)
        # Actualizar el label de Evidencia seleccionada
        self.label_evidencia.config(text=evidencia)

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.geometry("800x600")
    root.mainloop()