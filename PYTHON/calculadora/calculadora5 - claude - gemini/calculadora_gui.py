import tkinter as tk
from tkinter import font, messagebox, ttk
import ast
import operator as op
import math
from datetime import datetime

# --- Motor de Evaluación Mejorado ---

ALLOWED_FUNCTIONS = {
    'sin': math.sin,
    'cos': math.cos,
    'tan': math.tan,
    'sqrt': math.sqrt,
    'log': math.log,  # Logaritmo natural (ln)
    'log10': math.log10,  # Logaritmo base 10
    'log2': math.log2,  # Logaritmo base 2
    'exp': math.exp,
    'abs': abs,
    'pow': pow,
    'asin': math.asin,
    'acos': math.acos,
    'atan': math.atan,
    'atan2': math.atan2,
    'sinh': math.sinh,
    'cosh': math.cosh,
    'tanh': math.tanh,
    'radians': math.radians,
    'degrees': math.degrees,
    'factorial': math.factorial,
    'floor': math.floor,
    'ceil': math.ceil,
    'trunc': math.trunc,
    'gcd': math.gcd,
    'lcm': math.lcm,
    'comb': math.comb,  # Combinaciones
    'perm': math.perm,  # Permutaciones
}

ALLOWED_CONSTANTS = {
    'pi': math.pi,
    'e': math.e,
    'tau': math.tau,
    'inf': math.inf,
}

OPERADORES_SOPORTADOS = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.Pow: op.pow,
    ast.Mod: op.mod,
    ast.FloorDiv: op.floordiv,
    ast.USub: op.neg,
    ast.UAdd: op.pos,
}

# --- CORRECCIÓN ---
# Se añade 'angle_mode' como parámetro para manejarlo dentro del evaluador,
# lo cual es más robusto que reemplazar texto.
def evaluar_expresion(expresion_str: str, variables: dict, 
                      funciones_usuario: dict = None, angle_mode: str = "RAD"):
    """Evalúa una cadena de expresión de forma segura con soporte para funciones."""
    if funciones_usuario is None:
        funciones_usuario = {}
    
    try:
        # --- CORRECCIÓN ---
        # Se elimina el reemplazo de texto para constantes (ej: .replace('pi', ...)).
        # Era frágil (ej: "pinta" se convertiría en "3.1415...nta").
        # Las constantes ya están en el dict 'variables' y se resuelven
        # de forma segura en el 'ast.Name' handler.
        tree = ast.parse(expresion_str, mode='eval')
    except SyntaxError as e:
        raise SyntaxError(f"Sintaxis inválida: {e}")

    def _eval_nodo(node):
        if isinstance(node, ast.Constant):
            return node.value
        elif isinstance(node, ast.Name):
            # Buscar primero en variables (que incluye las constantes)
            if node.id in variables:
                return variables[node.id]
            # Si no está en variables, podría ser una función de usuario sin argumentos
            elif node.id in funciones_usuario:
                # Evaluar la función sin argumentos
                # --- CORRECCIÓN --- Se pasa el angle_mode
                return evaluar_expresion(funciones_usuario[node.id], variables, 
                                         funciones_usuario, angle_mode)
            else:
                raise NameError(f"Variable o función '{node.id}' no definida")
        elif isinstance(node, ast.BinOp):
            operador = OPERADORES_SOPORTADOS.get(type(node.op))
            if not operador:
                raise TypeError(f"Operador no soportado: {type(node.op).__name__}")
            izquierda = _eval_nodo(node.left)
            derecha = _eval_nodo(node.right)
            if isinstance(node.op, ast.Div) and derecha == 0:
                raise ZeroDivisionError("División por cero")
            return operador(izquierda, derecha)
        elif isinstance(node, ast.UnaryOp):
            operador = OPERADORES_SOPORTADOS.get(type(node.op))
            if not operador:
                raise TypeError(f"Operador no soportado: {type(node.op).__name__}")
            return operador(_eval_nodo(node.operand))
        elif isinstance(node, ast.Call):
            if not isinstance(node.func, ast.Name):
                raise TypeError("Solo se permiten llamadas directas a funciones")
            func_name = node.func.id
            
            # Evaluar argumentos
            args = [_eval_nodo(arg) for arg in node.args]
            
            # Buscar en funciones permitidas
            if func_name in ALLOWED_FUNCTIONS:
                try:
                    # --- CORRECCIÓN ---
                    # Lógica mejorada para modo angular (DEG)
                    if angle_mode == "DEG":
                        if func_name in ('sin', 'cos', 'tan'):
                            # Convertir argumentos a radianes antes de llamar
                            rad_args = [math.radians(arg) for arg in args]
                            return ALLOWED_FUNCTIONS[func_name](*rad_args)
                        elif func_name in ('asin', 'acos', 'atan', 'atan2'):
                            # Llamar a la función (que devuelve radianes) y convertir
                            # el resultado a grados.
                            rad_result = ALLOWED_FUNCTIONS[func_name](*args)
                            return math.degrees(rad_result)
                    
                    # Comportamiento normal (RAD o funciones no trigonométricas)
                    return ALLOWED_FUNCTIONS[func_name](*args)
                
                except (ValueError, TypeError) as e:
                    raise ValueError(f"Error en {func_name}: {e}")
            
            # Buscar en funciones de usuario
            elif func_name in funciones_usuario:
                # --- CORRECCIÓN ---
                # Las funciones de usuario (macros) no aceptan argumentos.
                # Si se proporcionan argumentos (ej: f(5)), lanzamos un error
                # en lugar de ignorarlos silenciosamente.
                if args:
                    raise TypeError(
                        f"La función de usuario '{func_name}' no acepta argumentos.\n"
                        f"Defina las variables (ej: x=5) y llame la función como '{func_name}()'."
                    )
                
                func_expr = funciones_usuario[func_name]
                # --- CORRECCIÓN --- Se pasa el angle_mode
                return evaluar_expresion(func_expr, variables, 
                                         funciones_usuario, angle_mode)
            else:
                raise NameError(f"Función no permitida: '{func_name}'")
        else:
            raise TypeError(f"Tipo de nodo no soportado: {type(node).__name__}")

    return _eval_nodo(tree.body)

# --- Ventana de Historial ---

class HistorialWindow(tk.Toplevel):
    def __init__(self, parent, historial_list):
        super().__init__(parent)
        self.parent = parent
        self.historial = historial_list
        self.title("Historial de Cálculos")
        self.geometry("500x600")
        self.resizable(True, True)
        self.minsize(450, 400)
        
        self._configurar_ui()
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def _configurar_ui(self):
        control_frame = tk.Frame(self, padx=10, pady=10)
        control_frame.pack(fill="x")
        
        tk.Label(control_frame, text="📊 Historial de Operaciones", 
                 font=("Segoe UI", 12, "bold")).pack(side="left")
        
        clear_btn = tk.Button(control_frame, text="🗑️ Limpiar Todo", 
                              command=self.clear_history,
                              bg="#e74c3c", fg="white", font=("Segoe UI", 9, "bold"),
                              cursor="hand2", relief="flat", padx=10, pady=5)
        clear_btn.pack(side="right", padx=5)
        
        export_btn = tk.Button(control_frame, text="💾 Exportar", 
                               command=self.export_history,
                               bg="#3498db", fg="white", font=("Segoe UI", 9, "bold"),
                               cursor="hand2", relief="flat", padx=10, pady=5)
        export_btn.pack(side="right")
        
        list_frame = tk.Frame(self, padx=10, pady=10)
        list_frame.pack(expand=True, fill="both")
        
        self.canvas = tk.Canvas(list_frame, bg="white", highlightthickness=1, 
                                highlightbackground="#bdc3c7")
        scrollbar = tk.Scrollbar(list_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg="white")
        
        self.scrollable_frame.bind("<Configure>", 
                                   lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # --- CORRECCIÓN ---
        # Se cambia bind_all por bind.
        # bind_all hacía que *todas* las ventanas (incluida la principal)
        # controlaran el scroll de esta ventana, incluso sin foco.
        # Ahora solo se activa el scroll cuando el cursor está sobre el canvas.
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)
        # También se debe vincular el frame interno y sus hijos
        self.scrollable_frame.bind("<MouseWheel>", self._on_mousewheel)
        
        self.populate_history()

    def _on_mousewheel(self, event):
        # Multiplicador para ajustar la velocidad de scroll si es necesario
        scroll_speed = int(-1*(event.delta/120))
        self.canvas.yview_scroll(scroll_speed, "units")

    def populate_history(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        if not self.historial:
            tk.Label(self.scrollable_frame, text="No hay cálculos en el historial.", 
                     font=("Segoe UI", 10, "italic"), bg="white", fg="#999").pack(pady=30)
            return
        
        for i, entry in enumerate(reversed(self.historial)):
            self._create_history_entry(entry, i)
            # --- CORRECCIÓN --- Vincular los nuevos frames al scroll también
            self.scrollable_frame.winfo_children()[-1].bind("<MouseWheel>", self._on_mousewheel)
            for child in self.scrollable_frame.winfo_children()[-1].winfo_children():
                child.bind("<MouseWheel>", self._on_mousewheel)


    def _create_history_entry(self, entry, index):
        frame = tk.Frame(self.scrollable_frame, bg="white", relief="solid", 
                         borderwidth=1, padx=10, pady=8)
        frame.pack(fill="x", pady=3)
        
        header_frame = tk.Frame(frame, bg="white")
        header_frame.pack(fill="x")
        
        timestamp = entry.get('timestamp', 'N/A')
        tk.Label(header_frame, text=f"🕐 {timestamp}", font=("Segoe UI", 8), 
                 bg="white", fg="#7f8c8d").pack(side="left")
        
        mode_text = f"[{entry.get('mode', 'RAD')}]"
        tk.Label(header_frame, text=mode_text, font=("Segoe UI", 8, "bold"), 
                 bg="white", fg="#9b59b6").pack(side="right")
        
        expr_frame = tk.Frame(frame, bg="white")
        expr_frame.pack(fill="x", pady=(5, 2))
        
        tk.Label(expr_frame, text="Expresión:", font=("Segoe UI", 8), 
                 bg="white", fg="#555").pack(side="left")
        
        expr_label = tk.Label(expr_frame, text=entry['expresion'], 
                              font=("Consolas", 10), bg="white", fg="#2c3e50")
        expr_label.pack(side="left", padx=5)
        
        result_frame = tk.Frame(frame, bg="white")
        result_frame.pack(fill="x", pady=(2, 5))
        
        tk.Label(result_frame, text="Resultado:", font=("Segoe UI", 8, "bold"), 
                 bg="white", fg="#555").pack(side="left")
        
        result_label = tk.Label(result_frame, text=str(entry['resultado']), 
                                font=("Consolas", 11, "bold"), bg="white", fg="#27ae60")
        result_label.pack(side="left", padx=5)
        
        btn_frame = tk.Frame(frame, bg="white")
        btn_frame.pack(fill="x", pady=(5, 0))
        
        use_result_btn = tk.Button(btn_frame, text="Usar Resultado", 
                                   command=lambda r=entry['resultado']: self.use_value(r),
                                   bg="#27ae60", fg="white", font=("Segoe UI", 8),
                                   cursor="hand2", relief="flat", padx=8, pady=3)
        use_result_btn.pack(side="right", padx=2)
        
        use_expr_btn = tk.Button(btn_frame, text="Usar Expresión", 
                                 command=lambda e=entry['expresion']: self.use_expression(e),
                                 bg="#3498db", fg="white", font=("Segoe UI", 8),
                                 cursor="hand2", relief="flat", padx=8, pady=3)
        use_expr_btn.pack(side="right", padx=2)
        
        delete_btn = tk.Button(btn_frame, text="✕", 
                               command=lambda idx=len(self.historial)-1-index: self.delete_entry(idx),
                               bg="#e74c3c", fg="white", font=("Segoe UI", 8, "bold"),
                               cursor="hand2", relief="flat", padx=6, pady=3)
        delete_btn.pack(side="right", padx=2)

    def use_value(self, value):
        self.parent.append_to_display(str(value))

    def use_expression(self, expression):
        self.parent.set_display(expression)

    def delete_entry(self, index):
        if 0 <= index < len(self.historial):
            del self.historial[index]
            self.populate_history()

    def clear_history(self):
        if not self.historial:
            messagebox.showinfo("Información", "El historial ya está vacío.", parent=self)
            return
        
        if messagebox.askyesno("Confirmar", 
                               f"¿Borrar todo el historial ({len(self.historial)} entradas)?", 
                               parent=self):
            self.historial.clear()
            self.populate_history()
            messagebox.showinfo("Éxito", "Historial limpiado.", parent=self)

    def export_history(self):
        if not self.historial:
            messagebox.showinfo("Información", "No hay historial para exportar.", parent=self)
            return
        
        try:
            filename = f"historial_calculadora_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("=" * 60 + "\n")
                f.write("HISTORIAL DE CALCULADORA CIENTÍFICA\n")
                f.write("=" * 60 + "\n\n")
                
                for i, entry in enumerate(self.historial, 1):
                    f.write(f"[{i}] {entry.get('timestamp', 'N/A')} - Modo: {entry.get('mode', 'RAD')}\n")
                    f.write(f"    Expresión: {entry['expresion']}\n")
                    f.write(f"    Resultado: {entry['resultado']}\n")
                    f.write("-" * 60 + "\n\n")
            
            messagebox.showinfo("Éxito", f"Historial exportado a:\n{filename}", parent=self)
        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar: {e}", parent=self)

    def on_close(self):
        # --- CORRECCIÓN ---
        # Cambiado unbind_all por unbind.
        # unbind_all rompía el scroll de otras ventanas si estaban abiertas.
        self.canvas.unbind("<MouseWheel>")
        self.scrollable_frame.unbind("<MouseWheel>")
        self.destroy()

# --- Ventana de Funciones de Usuario ---

class FuncionesWindow(tk.Toplevel):
    def __init__(self, parent, funciones_dict, variables_dict):
        super().__init__(parent)
        self.parent = parent
        self.funciones = funciones_dict
        self.variables = variables_dict
        self.title("Gestor de Funciones Algebraicas")
        self.geometry("500x500")
        self.resizable(True, True)
        self.minsize(450, 400)
        
        self._configurar_ui()
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def _configurar_ui(self):
        add_frame = tk.LabelFrame(self, text="Nueva Función Algebraica", padx=15, pady=15)
        add_frame.pack(fill="x", padx=10, pady=10)
        
        tk.Label(add_frame, text="Nombre:", font=("Segoe UI", 10)).grid(row=0, column=0, sticky="w", pady=5)
        self.name_entry = tk.Entry(add_frame, font=("Segoe UI", 10))
        self.name_entry.grid(row=0, column=1, sticky="ew", pady=5)
        self.name_entry.bind('<Return>', lambda e: self.value_entry.focus_set())
        
        tk.Label(add_frame, text="Expresión:", font=("Segoe UI", 10)).grid(row=1, column=0, sticky="w", pady=5)
        self.value_entry = tk.Entry(add_frame, font=("Segoe UI", 10))
        self.value_entry.grid(row=1, column=1, sticky="ew", pady=5)
        self.value_entry.bind('<Return>', lambda e: self.save_function())
        
        add_frame.grid_columnconfigure(1, weight=1)
        
        # --- CORRECCIÓN ---
        # Se actualiza el texto de ayuda para reflejar cómo funcionan
        # realmente las funciones (como macros, sin argumentos).
        info_label = tk.Label(add_frame, 
                              text="💡 Ejemplo: Nombre: f, Expresión: 2*x + 1\n"
                                   "Defina 'x' en el gestor de variables (ej: x=5).\n"
                                   "Use f() en la calculadora para evaluar (resultado: 11).",
                              font=("Segoe UI", 8, "italic"), fg="#7f8c8d", justify="left")
        info_label.grid(row=2, column=0, columnspan=2, sticky="w", pady=5)
        
        save_button = tk.Button(add_frame, text="💾 Guardar Función", command=self.save_function, 
                                bg="#9b59b6", fg="white", font=("Segoe UI", 10, "bold"), 
                                cursor="hand2", relief="flat", padx=10, pady=5)
        save_button.grid(row=3, column=0, columnspan=2, pady=10, sticky="ew")
        
        list_frame = tk.LabelFrame(self, text="Funciones Guardadas", padx=10, pady=10)
        list_frame.pack(expand=True, fill="both", padx=10, pady=(0, 10))
        
        clear_all_frame = tk.Frame(list_frame)
        clear_all_frame.pack(fill="x", pady=(0, 5))
        
        clear_all_btn = tk.Button(clear_all_frame, text="🗑️ Borrar Todas las Funciones", 
                                  command=self.clear_all_functions,
                                  bg="#e74c3c", fg="white", font=("Segoe UI", 9, "bold"),
                                  cursor="hand2", relief="flat", padx=10, pady=5)
        clear_all_btn.pack(fill="x")
        
        self.canvas = tk.Canvas(list_frame, bg="white", highlightthickness=0)
        scrollbar = tk.Scrollbar(list_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg="white")
        
        self.scrollable_frame.bind("<Configure>", 
                                   lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # --- CORRECCIÓN ---
        # Se cambia bind_all por bind (igual que en HistorialWindow).
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)
        self.scrollable_frame.bind("<MouseWheel>", self._on_mousewheel)
        
        self.populate_function_list()
        self.name_entry.focus_set()

    def _on_mousewheel(self, event):
        scroll_speed = int(-1*(event.delta/120))
        self.canvas.yview_scroll(scroll_speed, "units")

    def populate_function_list(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        if not self.funciones:
            tk.Label(self.scrollable_frame, text="No hay funciones guardadas.", 
                     font=("Segoe UI", 10, "italic"), bg="white", fg="#999").pack(pady=20)
            return
        
        for name, expr in self.funciones.items():
            self._create_function_row(name, expr)
            # --- CORRECCIÓN --- Vincular los nuevos frames al scroll
            self.scrollable_frame.winfo_children()[-1].bind("<MouseWheel>", self._on_mousewheel)
            for child in self.scrollable_frame.winfo_children()[-1].winfo_children():
                child.bind("<MouseWheel>", self._on_mousewheel)

    def _create_function_row(self, name, expr):
        frame = tk.Frame(self.scrollable_frame, bg="white", relief="solid", 
                         borderwidth=1, padx=10, pady=8)
        frame.pack(fill="x", pady=3)
        
        func_text = f"{name}() = {expr}"
        label = tk.Label(frame, text=func_text, anchor="w", font=("Consolas", 10), 
                         bg="white", fg="#9b59b6", wraplength=350)
        label.pack(side="left", fill="x", expand=True, padx=5)
        
        eval_btn = tk.Button(frame, text="Evaluar", command=lambda n=name: self.evaluate_function(n),
                             bg="#27ae60", fg="white", font=("Segoe UI", 8),
                             cursor="hand2", relief="flat", padx=8, pady=3)
        eval_btn.pack(side="right", padx=2)
        
        use_button = tk.Button(frame, text="Usar", command=lambda n=name: self.use_function(n),
                               bg="#3498db", fg="white", font=("Segoe UI", 8), 
                               cursor="hand2", relief="flat", padx=8, pady=3)
        use_button.pack(side="right", padx=2)
        
        delete_button = tk.Button(frame, text="✕", command=lambda n=name: self.delete_function(n),
                                  bg="#e74c3c", fg="white", font=("Segoe UI", 8, "bold"), 
                                  cursor="hand2", relief="flat", padx=6, pady=3)
        delete_button.pack(side="right", padx=2)

    def use_function(self, name):
        self.parent.append_to_display(f"{name}()")

    def evaluate_function(self, name):
        """Evalúa la función con las variables actuales."""
        try:
            # --- CORRECCIÓN ---
            # Se pasa el modo angular del padre para una evaluación correcta.
            result = evaluar_expresion(self.funciones[name], self.variables, 
                                     self.funciones, self.parent.angle_mode)
            messagebox.showinfo("Resultado", 
                                f"{name}() = {result:.10g}" if isinstance(result, float) else f"{name}() = {result}", 
                                parent=self)
        except Exception as e:
            messagebox.showerror("Error", f"Error al evaluar {name}:\n{e}", parent=self)

    def save_function(self):
        name = self.name_entry.get().strip()
        expr = self.value_entry.get().strip()
        
        if not name:
            messagebox.showwarning("Advertencia", "Ingrese un nombre para la función.", parent=self)
            self.name_entry.focus_set()
            return
            
        if not name.isidentifier():
            messagebox.showerror("Error", f"'{name}' no es un nombre de función válido.\n"
                                 "Use solo letras, números y guiones bajos.", parent=self)
            self.name_entry.focus_set()
            return
            
        if name in ALLOWED_FUNCTIONS or name in ALLOWED_CONSTANTS:
            messagebox.showerror("Error", f"No puede redefinir la función/constante '{name}'.", parent=self)
            self.name_entry.focus_set()
            return
            
        if not expr:
            messagebox.showerror("Error", "La expresión no puede estar vacía.", parent=self)
            self.value_entry.focus_set()
            return
        
        # Validar la expresión
        try:
            # --- CORRECCIÓN ---
            # Se pasa el modo angular del padre para una validación correcta.
            evaluar_expresion(expr, self.variables, self.funciones, self.parent.angle_mode)
            self.funciones[name] = expr
            self.name_entry.delete(0, tk.END)
            self.value_entry.delete(0, tk.END)
            self.populate_function_list()
            messagebox.showinfo("Éxito", f"Función '{name}' guardada:\n{name}() = {expr}", parent=self)
            self.name_entry.focus_set()
        except Exception as e:
            messagebox.showerror("Error de Validación", 
                                 f"La expresión tiene errores:\n{e}\n\n"
                                 "Asegúrese de que todas las variables estén definidas.", 
                                 parent=self)
            self.value_entry.focus_set()

    def delete_function(self, name):
        if messagebox.askyesno("Confirmar", f"¿Eliminar la función '{name}'?", parent=self):
            del self.funciones[name]
            self.populate_function_list()

    def clear_all_functions(self):
        if not self.funciones:
            messagebox.showinfo("Información", "No hay funciones para borrar.", parent=self)
            return
        
        if messagebox.askyesno("Confirmar", 
                               f"¿Borrar todas las {len(self.funciones)} funciones?", 
                               parent=self):
            self.funciones.clear()
            self.populate_function_list()
            messagebox.showinfo("Éxito", "Todas las funciones han sido eliminadas.", parent=self)

    def on_close(self):
        # --- CORRECCIÓN ---
        # Cambiado unbind_all por unbind.
        self.canvas.unbind("<MouseWheel>")
        self.scrollable_frame.unbind("<MouseWheel>")
        self.destroy()

# --- Ventana de Variables ---

class VariablesWindow(tk.Toplevel):
    def __init__(self, parent, variables_dict):
        super().__init__(parent)
        self.parent = parent
        self.variables = variables_dict
        self.title("Gestor de Variables")
        self.geometry("400x500")
        self.resizable(True, True)
        self.minsize(350, 400)
        
        self._configurar_ui()
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def _configurar_ui(self):
        add_frame = tk.LabelFrame(self, text="Nueva Variable", padx=15, pady=15)
        add_frame.pack(fill="x", padx=10, pady=10)
        
        tk.Label(add_frame, text="Nombre:", font=("Segoe UI", 10)).grid(row=0, column=0, sticky="w", pady=5)
        self.name_entry = tk.Entry(add_frame, font=("Segoe UI", 10))
        self.name_entry.grid(row=0, column=1, sticky="ew", pady=5)
        self.name_entry.bind('<Return>', lambda e: self.value_entry.focus_set())
        
        tk.Label(add_frame, text="Valor/Expresión:", font=("Segoe UI", 10)).grid(row=1, column=0, sticky="w", pady=5)
        self.value_entry = tk.Entry(add_frame, font=("Segoe UI", 10))
        self.value_entry.grid(row=1, column=1, sticky="ew", pady=5)
        self.value_entry.bind('<Return>', lambda e: self.save_variable())
        
        add_frame.grid_columnconfigure(1, weight=1)
        
        save_button = tk.Button(add_frame, text="💾 Guardar Variable", command=self.save_variable, 
                                bg="#27ae60", fg="white", font=("Segoe UI", 10, "bold"), 
                                cursor="hand2", relief="flat", padx=10, pady=5)
        save_button.grid(row=2, column=0, columnspan=2, pady=10, sticky="ew")
        
        list_frame = tk.LabelFrame(self, text="Variables Guardadas", padx=10, pady=10)
        list_frame.pack(expand=True, fill="both", padx=10, pady=(0, 10))
        
        clear_all_frame = tk.Frame(list_frame)
        clear_all_frame.pack(fill="x", pady=(0, 5))
        
        clear_all_btn = tk.Button(clear_all_frame, text="🗑️ Borrar Todas las Variables", 
                                  command=self.clear_all_user_variables,
                                  bg="#e74c3c", fg="white", font=("Segoe UI", 9, "bold"),
                                  cursor="hand2", relief="flat", padx=10, pady=5)
        clear_all_btn.pack(fill="x")
        
        self.canvas = tk.Canvas(list_frame, bg="white", highlightthickness=0)
        scrollbar = tk.Scrollbar(list_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg="white")
        
        self.scrollable_frame.bind("<Configure>", 
                                   lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # --- CORRECCIÓN ---
        # Se cambia bind_all por bind (igual que en HistorialWindow).
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)
        self.scrollable_frame.bind("<MouseWheel>", self._on_mousewheel)
        
        self.populate_variable_list()
        self.name_entry.focus_set()

    def _on_mousewheel(self, event):
        scroll_speed = int(-1*(event.delta/120))
        self.canvas.yview_scroll(scroll_speed, "units")

    def populate_variable_list(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        # --- CORRECCIÓN --- 
        # Asegurarse de que las constantes siempre estén presentes
        # en la lista de variables, incluso si se borraron por error.
        for k, v in ALLOWED_CONSTANTS.items():
            if k not in self.variables:
                self.variables[k] = v
                
        if not self.variables:
            tk.Label(self.scrollable_frame, text="No hay variables guardadas.", 
                     font=("Segoe UI", 10, "italic"), bg="white", fg="#999").pack(pady=20)
            return
        
        constants = {k: v for k, v in self.variables.items() if k in ALLOWED_CONSTANTS}
        user_vars = {k: v for k, v in self.variables.items() if k not in ALLOWED_CONSTANTS}
        
        row = 0
        
        if constants:
            tk.Label(self.scrollable_frame, text="Constantes:", font=("Segoe UI", 9, "bold"), 
                     bg="white", fg="#555").grid(row=row, column=0, sticky="w", pady=(5, 2))
            row += 1
            
            for name, value in sorted(constants.items()):
                self._create_variable_row(name, value, row, is_constant=True)
                row += 1
        
        if user_vars:
            if constants:
                tk.Label(self.scrollable_frame, text="", bg="white").grid(row=row, column=0)
                row += 1
            
            tk.Label(self.scrollable_frame, text="Variables de Usuario:", font=("Segoe UI", 9, "bold"), 
                     bg="white", fg="#555").grid(row=row, column=0, sticky="w", pady=(5, 2))
            row += 1
            
            for name, value in sorted(user_vars.items()):
                self._create_variable_row(name, value, row, is_constant=False)
                row += 1
        
        self.scrollable_frame.grid_columnconfigure(0, weight=1)
        
        # --- CORRECCIÓN --- Vincular los nuevos frames al scroll
        for child in self.scrollable_frame.winfo_children():
            child.bind("<MouseWheel>", self._on_mousewheel)
            if isinstance(child, tk.Frame):
                for grandchild in child.winfo_children():
                    grandchild.bind("<MouseWheel>", self._on_mousewheel)

    def _create_variable_row(self, name, value, row, is_constant):
        frame = tk.Frame(self.scrollable_frame, bg="white")
        frame.grid(row=row, column=0, sticky="ew", pady=2)
        
        try:
            display_value = f"{value:.10g}" if isinstance(value, float) else str(value)
        except (ValueError, TypeError):
            display_value = str(value)
        
        var_text = f"{name} = {display_value}"
        label = tk.Label(frame, text=var_text, anchor="w", font=("Segoe UI", 10), 
                         bg="white", fg="#333")
        label.pack(side="left", fill="x", expand=True, padx=5)
        
        use_button = tk.Button(frame, text="Usar", command=lambda n=name: self.use_variable(n),
                               bg="#3498db", fg="white", font=("Segoe UI", 8), 
                               cursor="hand2", relief="flat", padx=8, pady=2)
        use_button.pack(side="right", padx=2)
        
        if not is_constant:
            delete_button = tk.Button(frame, text="✕", command=lambda n=name: self.delete_variable(n),
                                      bg="#e74c3c", fg="white", font=("Segoe UI", 8, "bold"), 
                                      cursor="hand2", relief="flat", padx=6, pady=2)
            delete_button.pack(side="right", padx=2)

    def use_variable(self, name):
        self.parent.append_to_display(name)
        self.name_entry.focus_set()

    def save_variable(self):
        name = self.name_entry.get().strip()
        expr = self.value_entry.get().strip()
        
        if not name:
            messagebox.showwarning("Advertencia", "Ingrese un nombre para la variable.", parent=self)
            self.name_entry.focus_set()
            return
            
        if not name.isidentifier():
            messagebox.showerror("Error", f"'{name}' no es un nombre de variable válido.\n"
                                 "Use solo letras, números y guiones bajos.", parent=self)
            self.name_entry.focus_set()
            return
            
        if name in ALLOWED_CONSTANTS:
            messagebox.showerror("Error", f"No puede redefinir la constante '{name}'.", parent=self)
            self.name_entry.focus_set()
            return
            
        if not expr:
            messagebox.showerror("Error", "La expresión no puede estar vacía.", parent=self)
            self.value_entry.focus_set()
            return
        
        try:
            # --- CORRECCIÓN ---
            # Se pasa el modo angular del padre y sus funciones
            # para evaluar la variable correctamente.
            value = evaluar_expresion(expr, self.variables, 
                                    self.parent.funciones, self.parent.angle_mode)
            self.variables[name] = value
            self.name_entry.delete(0, tk.END)
            self.value_entry.delete(0, tk.END)
            self.populate_variable_list()
            if isinstance(value, float):
                formatted_value = f"{value:.10g}"
            else:
                formatted_value = str(value)
            messagebox.showinfo("Éxito", f"Variable '{name}' guardada con valor {formatted_value}", parent=self)
            self.name_entry.focus_set()
        except Exception as e:
            messagebox.showerror("Error de Evaluación", str(e), parent=self)
            self.value_entry.focus_set()

    def delete_variable(self, name):
        if name in self.variables and name not in ALLOWED_CONSTANTS:
            if messagebox.askyesno("Confirmar", f"¿Eliminar la variable '{name}'?", parent=self):
                del self.variables[name]
                self.populate_variable_list()

    def clear_all_user_variables(self):
        user_vars = [k for k in self.variables.keys() if k not in ALLOWED_CONSTANTS]
        
        if not user_vars:
            messagebox.showinfo("Información", "No hay variables de usuario para borrar.", parent=self)
            return
        
        if messagebox.askyesno("Confirmar", 
                               f"¿Borrar todas las {len(user_vars)} variables de usuario?\n"
                               "Las constantes (pi, e, tau) se mantendrán.", 
                               parent=self):
            for var in user_vars:
                del self.variables[var]
            self.populate_variable_list()
            messagebox.showinfo("Éxito", "Todas las variables de usuario han sido eliminadas.", parent=self)

    def on_close(self):
        # --- CORRECCIÓN ---
        # Cambiado unbind_all por unbind.
        self.canvas.unbind("<MouseWheel>")
        self.scrollable_frame.unbind("<MouseWheel>")
        self.destroy()

# --- Clase Principal de la Calculadora ---

class CalculadoraApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Calculadora Científica Avanzada")
        self.geometry("500x750")
        self.resizable(True, True)
        self.minsize(450, 700)
        
        self.variables = ALLOWED_CONSTANTS.copy()
        self.funciones = {}  # Funciones algebraicas definidas por el usuario
        self.display_var = tk.StringVar()
        self.history = []
        self.angle_mode = "RAD"
        self.var_window = None
        self.hist_window = None
        self.func_window = None
        
        self._configurar_estilos()
        self._configurar_ui()
        self._configurar_atajos()

    def _configurar_estilos(self):
        self.main_font = font.Font(family="Segoe UI", size=10)
        self.display_font = font.Font(family="Consolas", size=20, weight="bold")
        self.configure(bg="#2c3e50")

    def _configurar_ui(self):
        mode_frame = tk.Frame(self, bg="#34495e", padx=10, pady=5)
        mode_frame.pack(fill="x", padx=5, pady=(5, 0))
        
        tk.Label(mode_frame, text="Modo Angular:", bg="#34495e", fg="white", 
                 font=("Segoe UI", 9)).pack(side="left")
        
        self.mode_label = tk.Label(mode_frame, text=self.angle_mode, 
                                    bg="#9b59b6", fg="white", 
                                    font=("Segoe UI", 10, "bold"), 
                                    padx=15, pady=3, relief="raised")
        self.mode_label.pack(side="left", padx=10)
        
        toggle_btn = tk.Button(mode_frame, text="⇄ Cambiar", 
                               command=self.toggle_angle_mode,
                               bg="#8e44ad", fg="white", font=("Segoe UI", 9, "bold"),
                               cursor="hand2", relief="flat", padx=10, pady=3)
        toggle_btn.pack(side="left")
        
        self.mode_info = tk.Label(mode_frame, 
                                  text="Radianes (funciones trig en radianes)", 
                                  bg="#34495e", fg="#ecf0f1", 
                                  font=("Segoe UI", 8, "italic"))
        self.mode_info.pack(side="right")
        
        display_frame = tk.Frame(self, bd=0, bg="#34495e", padx=10, pady=10)
        display_frame.pack(fill="x", padx=5, pady=5)
        
        self.display_entry = tk.Entry(display_frame, textvariable=self.display_var, 
                                      font=self.display_font, bg="#ecf0f1", fg="#2c3e50", 
                                      bd=2, relief="flat", justify="right", 
                                      insertbackground="#e74c3c", insertwidth=3)
        self.display_entry.pack(fill="x", ipady=15)
        self.display_entry.focus_set()
        
        button_frame = tk.Frame(self, bg="#2c3e50", padx=5, pady=5)
        button_frame.pack(expand=True, fill="both")
        
        botones = [
            # Fila 0: Funciones trigonométricas
            ('sin', 0, 0, 'trig'), ('cos', 0, 1, 'trig'), ('tan', 0, 2, 'trig'), ('asin', 0, 3, 'trig'),
            # Fila 1: Funciones inversas y raíz
            ('acos', 1, 0, 'trig'), ('atan', 1, 1, 'trig'), ('√', 1, 2, 'func'), ('^', 1, 3, 'oper'),
            # Fila 2: Logaritmos
            ('ln', 2, 0, 'func'), ('log', 2, 1, 'func'), ('exp', 2, 2, 'func'), ('n!', 2, 3, 'func'),
            # Fila 3: Gestión
            ('VAR', 3, 0, 'var'), ('FUN', 3, 1, 'func_btn'), ('HIST', 3, 2, 'hist'), ('(', 3, 3, 'paren'),
            # Fila 4: Paréntesis y Clear
            (')', 4, 0, 'paren'), ('C', 4, 1, 'clear'), ('AC', 4, 2, 'allclear'), ('7', 4, 3, 'num'),
            # Fila 5
            ('8', 5, 0, 'num'), ('9', 5, 1, 'num'), ('÷', 5, 2, 'oper'), ('4', 5, 3, 'num'),
            # Fila 6
            ('5', 6, 0, 'num'), ('6', 6, 1, 'num'), ('×', 6, 2, 'oper'), ('1', 6, 3, 'num'),
            # Fila 7
            ('2', 7, 0, 'num'), ('3', 7, 1, 'num'), ('-', 7, 2, 'oper'), ('0', 7, 3, 'num'),
            # Fila 8
            ('.', 8, 0, 'num'), ('+', 8, 1, 'oper'), ('=', 8, 2, 'equal', 2),
        ]
        
        colores = {
            'num': '#34495e',
            'oper': '#e67e22',
            'paren': '#95a5a6',
            'var': '#3498db',
            'func_btn': '#9b59b6',
            'hist': '#1abc9c',
            'trig': '#8e44ad',
            'func': '#16a085',
            'clear': '#e74c3c',
            'allclear': '#c0392b',
            'equal': '#27ae60'
        }
        
        for item in botones:
            texto = item[0]
            fila, col = item[1], item[2]
            categoria = item[3]
            colspan = item[4] if len(item) > 4 else 1
            
            action = lambda x=texto: self.manejar_clic(x)
            color_bg = colores.get(categoria, '#555')
            
            # Ajustar tamaño de fuente para botones con más texto
            btn_font = font.Font(family="Segoe UI", size=9 if len(texto) > 2 else 11)
            
            btn = tk.Button(button_frame, text=texto, font=btn_font, 
                            bg=color_bg, fg="white", bd=0, relief="flat",
                            activebackground="#2c3e50", activeforeground="white", 
                            cursor="hand2", command=action)
            
            btn.grid(row=fila, column=col, columnspan=colspan, sticky="nsew", padx=2, pady=2)
        
        for i in range(9):
            button_frame.grid_rowconfigure(i, weight=1)
        for i in range(4):
            button_frame.grid_columnconfigure(i, weight=1)

    def _configurar_atajos(self):
        self.bind('<Return>', lambda e: self.calcular_resultado())
        self.bind('<KP_Enter>', lambda e: self.calcular_resultado()) # Keypad Enter
        self.bind('<Escape>', lambda e: self.limpiar_display())
        self.bind('<Control-v>', lambda e: self.open_variables_window())
        self.bind('<Control-h>', lambda e: self.open_history_window())
        self.bind('<Control-f>', lambda e: self.open_functions_window())
        self.bind('<Control-m>', lambda e: self.toggle_angle_mode())

    def toggle_angle_mode(self):
        if self.angle_mode == "RAD":
            self.angle_mode = "DEG"
            self.mode_label.config(text="DEG", bg="#e67e22")
            self.mode_info.config(text="Grados sexagesimales (360°)")
        else:
            self.angle_mode = "RAD"
            self.mode_label.config(text="RAD", bg="#9b59b6")
            self.mode_info.config(text="Radianes (funciones trig en radianes)")

    def manejar_clic(self, char):
        if char == "=":
            self.calcular_resultado()
        elif char == "C":
            self.limpiar_display()
        elif char == "AC":
            self.clear_all()
        elif char == "VAR":
            self.open_variables_window()
        elif char == "FUN":
            self.open_functions_window()
        elif char == "HIST":
            self.open_history_window()
        elif char == 'ln':
            self.append_to_display('log(')
        elif char == 'log':
            self.append_to_display('log10(')
        elif char == 'n!':
            self.append_to_display('factorial(')
        elif char in ['sin', 'cos', 'tan', 'asin', 'acos', 'atan', 'exp']:
            self.append_to_display(char + '(')
        elif char == '√':
            self.append_to_display('sqrt(')
        elif char == '^':
            self.append_to_display('**')
        elif char == '×':
            self.append_to_display('*')
        elif char == '÷':
            self.append_to_display('/')
        else:
            self.append_to_display(char)

    def clear_all(self):
        # --- CORRECCIÓN ---
        # El botón "AC" (All Clear) ahora es más potente que "C".
        # Ofrece limpiar también variables y funciones.
        self.limpiar_display()
        if messagebox.askyesno("Limpieza Total", 
                               "¿Desea borrar también todas las variables y funciones de usuario?",
                               parent=self):
            
            user_vars = [k for k in self.variables.keys() if k not in ALLOWED_CONSTANTS]
            for var in user_vars:
                del self.variables[var]
            
            self.funciones.clear()
            
            # Refrescar ventanas si están abiertas
            if self.var_window and self.var_window.winfo_exists():
                self.var_window.populate_variable_list()
            if self.func_window and self.func_window.winfo_exists():
                self.func_window.populate_function_list()
                
            messagebox.showinfo("Limpieza Total", "Variables y funciones borradas.", parent=self)


    def open_variables_window(self):
        if self.var_window and self.var_window.winfo_exists():
            self.var_window.lift()
            self.var_window.focus_set()
        else:
            self.var_window = VariablesWindow(self, self.variables)

    def open_functions_window(self):
        if self.func_window and self.func_window.winfo_exists():
            self.func_window.lift()
            self.func_window.focus_set()
        else:
            self.func_window = FuncionesWindow(self, self.funciones, self.variables)

    def open_history_window(self):
        if self.hist_window and self.hist_window.winfo_exists():
            self.hist_window.lift()
            self.hist_window.focus_set()
        else:
            self.hist_window = HistorialWindow(self, self.history)

    def append_to_display(self, text):
        current_text = self.display_var.get()
        self.display_var.set(current_text + text)
        self.display_entry.icursor(len(current_text) + len(text))
        self.display_entry.focus_set()

    def set_display(self, text):
        self.display_var.set(text)
        self.display_entry.icursor(len(text))
        self.display_entry.focus_set()

    def calcular_resultado(self):
        expresion_actual = self.display_var.get()
        if not expresion_actual:
            return
        
        # --- CORRECCIÓN ---
        # Se elimina el reemplazo de texto (string replace) para el modo DEG.
        # Toda la lógica se ha movido al interior de 'evaluar_expresion'
        # para un manejo mucho más robusto y seguro.
        
        try:
            # --- CORRECCIÓN ---
            # Ahora pasamos el 'angle_mode' actual al evaluador.
            resultado = evaluar_expresion(
                expresion_actual,
                self.variables,
                self.funciones,
                self.angle_mode
            )
            
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.history.append({
                'expresion': expresion_actual,
                'resultado': resultado,
                'mode': self.angle_mode,
                'timestamp': timestamp
            })
            
            if self.hist_window and self.hist_window.winfo_exists():
                self.hist_window.populate_history()
            
            result_str = ""
            if isinstance(resultado, float):
                if resultado.is_integer():
                    result_str = str(int(resultado))
                else:
                    # Formato 'g' para eliminar ceros innecesarios
                    result_str = f"{resultado:.10g}" 
            else:
                result_str = str(resultado)
                
            self.set_display(result_str)
                
        except (SyntaxError, NameError, ZeroDivisionError, TypeError, ValueError) as e:
            messagebox.showerror("Error", str(e), parent=self)
        except Exception as e:
            messagebox.showerror("Error Inesperado", f"Ha ocurrido un error: {e}", parent=self)

    def limpiar_display(self):
        """Limpia el display."""
        self.set_display("")

if __name__ == "__main__":
    app = CalculadoraApp()
    app.mainloop()