import tkinter as tk
from tkinter import font, messagebox, filedialog
import ast
import operator as op
import math
from datetime import datetime

# --- CONFIGURACIÓN GLOBAL ---
COLORS = {
    'bg': "#2c3e50",
    'bg_dark': "#34495e", 
    'accent': "#9b59b6",
    'text': "#ecf0f1",
    'btn_num': "#34495e",
    'btn_op': "#e67e22",
    'btn_eq': "#27ae60",
    'btn_del': "#e74c3c",
    'btn_func': "#16a085"
}

# --- MOTOR MATEMÁTICO ---
class MathEngine:
    ALLOWED_FUNCTIONS = {
        'sin': math.sin, 'cos': math.cos, 'tan': math.tan,
        'asin': math.asin, 'acos': math.acos, 'atan': math.atan, 'atan2': math.atan2,
        'sqrt': math.sqrt, 'log': math.log, 'log10': math.log10, 'log2': math.log2,
        'exp': math.exp, 'abs': abs, 'pow': pow, 'sinh': math.sinh, 'cosh': math.cosh, 'tanh': math.tanh,
        'radians': math.radians, 'degrees': math.degrees, 'factorial': math.factorial,
        'floor': math.floor, 'ceil': math.ceil, 'gcd': math.gcd, 'comb': math.comb, 'perm': math.perm
    }

    ALLOWED_CONSTANTS = {
        'pi': math.pi, 'e': math.e, 'tau': math.tau, 'inf': math.inf
    }

    OPERATORS = {
        ast.Add: op.add, ast.Sub: op.sub, ast.Mult: op.mul,
        ast.Div: op.truediv, ast.Pow: op.pow, ast.Mod: op.mod,
        ast.USub: op.neg, ast.UAdd: op.pos
    }

    @staticmethod
    def evaluar(expresion_str, variables, funciones_usuario, angle_mode="RAD", depth=0):
        """Evalúa expresiones de forma segura con límite de recursión."""
        if depth > 50:
            raise RecursionError("Límite de recursión excedido (función circular detectada).")
        
        # Parsear AST
        try:
            tree = ast.parse(expresion_str, mode='eval')
        except SyntaxError:
            raise SyntaxError("Sintaxis inválida")

        def _eval_node(node):
            if isinstance(node, ast.Constant):
                return node.value
            
            elif isinstance(node, ast.Name):
                if node.id in variables:
                    return variables[node.id]
                elif node.id in funciones_usuario:
                    # Evaluar macro de usuario recursivamente
                    return MathEngine.evaluar(funciones_usuario[node.id], variables, 
                                            funciones_usuario, angle_mode, depth + 1)
                raise NameError(f"'{node.id}' no definido")
            
            elif isinstance(node, ast.BinOp):
                left = _eval_node(node.left)
                right = _eval_node(node.right)
                if isinstance(node.op, ast.Div) and right == 0:
                    raise ZeroDivisionError("División por cero")
                return MathEngine.OPERATORS[type(node.op)](left, right)
            
            elif isinstance(node, ast.UnaryOp):
                return MathEngine.OPERATORS[type(node.op)](_eval_node(node.operand))
            
            elif isinstance(node, ast.Call):
                func_name = node.func.id
                args = [_eval_node(arg) for arg in node.args]

                # Funciones estándar
                if func_name in MathEngine.ALLOWED_FUNCTIONS:
                    if angle_mode == "DEG":
                        if func_name in ('sin', 'cos', 'tan'):
                            args = [math.radians(a) for a in args]
                            return MathEngine.ALLOWED_FUNCTIONS[func_name](*args)
                        elif func_name in ('asin', 'acos', 'atan', 'atan2'):
                            res = MathEngine.ALLOWED_FUNCTIONS[func_name](*args)
                            return math.degrees(res)
                    return MathEngine.ALLOWED_FUNCTIONS[func_name](*args)
                
                # Funciones de usuario (Macros) - No aceptan argumentos
                elif func_name in funciones_usuario:
                    if args:
                        raise TypeError(f"'{func_name}' es una macro y no acepta argumentos.")
                    return MathEngine.evaluar(funciones_usuario[func_name], variables, 
                                            funciones_usuario, angle_mode, depth + 1)
                else:
                    raise NameError(f"Función desconocida: '{func_name}'")
            
            raise TypeError(f"Nodo no soportado: {type(node)}")

        return _eval_node(tree.body)

# --- COMPONENTE DE INTERFAZ REUTILIZABLE ---
class ScrollableFrame(tk.Frame):
    """Un frame con scrollbar vertical integrado y manejo de mousewheel."""
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        self.canvas = tk.Canvas(self, bg="white", highlightthickness=0)
        self.scrollbar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_content = tk.Frame(self.canvas, bg="white")

        self.scrollable_content.bind("<Configure>", 
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        self.canvas.create_window((0, 0), window=self.scrollable_content, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Bindings universales
        self.canvas.bind("<Enter>", self._bind_mouse)
        self.canvas.bind("<Leave>", self._unbind_mouse)

    def _bind_mouse(self, event):
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Button-4>", self._on_mousewheel) # Linux Scroll Up
        self.canvas.bind_all("<Button-5>", self._on_mousewheel) # Linux Scroll Down

    def _unbind_mouse(self, event):
        self.canvas.unbind_all("<MouseWheel>")
        self.canvas.unbind_all("<Button-4>")
        self.canvas.unbind_all("<Button-5>")

    def _on_mousewheel(self, event):
        if event.num == 5 or event.delta < 0:
            self.canvas.yview_scroll(1, "units")
        elif event.num == 4 or event.delta > 0:
            self.canvas.yview_scroll(-1, "units")

# --- VENTANAS SECUNDARIAS ---

class BaseSubWindow(tk.Toplevel):
    def __init__(self, parent, title, geometry="500x500"):
        super().__init__(parent)
        self.parent = parent
        self.title(title)
        self.geometry(geometry)
        self.config(bg="white")
        
    def create_btn(self, parent, text, cmd, color, side="right"):
        tk.Button(parent, text=text, command=cmd, bg=color, fg="white", 
                 font=("Segoe UI", 8), relief="flat", padx=8, pady=2, cursor="hand2").pack(side=side, padx=2)

class HistorialWindow(BaseSubWindow):
    def __init__(self, parent, historial_list):
        super().__init__(parent, "Historial", "500x600")
        self.historial = historial_list
        
        # Header Controls
        ctrl = tk.Frame(self, padx=10, pady=10, bg="white")
        ctrl.pack(fill="x")
        tk.Label(ctrl, text="📊 Historial", font=("Segoe UI", 12, "bold"), bg="white").pack(side="left")
        self.create_btn(ctrl, "🗑️ Limpiar", self.clear_history, COLORS['btn_del'])
        self.create_btn(ctrl, "💾 Exportar", self.export_history, COLORS['btn_op'])

        # List Area
        self.scroll_area = ScrollableFrame(self)
        self.scroll_area.pack(fill="both", expand=True, padx=10, pady=10)
        self.populate()

    def populate(self):
        for w in self.scroll_area.scrollable_content.winfo_children(): w.destroy()
        
        if not self.historial:
            tk.Label(self.scroll_area.scrollable_content, text="Sin historial", bg="white", fg="#999").pack(pady=20)
            return

        for i, entry in enumerate(reversed(self.historial)):
            f = tk.Frame(self.scroll_area.scrollable_content, bg="white", relief="solid", bd=1, padx=10, pady=5)
            f.pack(fill="x", pady=2)
            
            # Info Header
            h = tk.Frame(f, bg="white")
            h.pack(fill="x")
            tk.Label(h, text=f"🕐 {entry['timestamp']} [{entry['mode']}]", font=("Segoe UI", 8), fg="#7f8c8d", bg="white").pack(side="left")
            
            # Data
            tk.Label(f, text=f"Expr: {entry['expresion']}", font=("Consolas", 10), bg="white").pack(anchor="w")
            tk.Label(f, text=f"= {entry['resultado']}", font=("Consolas", 11, "bold"), fg=COLORS['btn_eq'], bg="white").pack(anchor="w")
            
            # Actions
            btns = tk.Frame(f, bg="white")
            btns.pack(fill="x", pady=5)
            self.create_btn(btns, "✕", lambda idx=len(self.historial)-1-i: self.delete_entry(idx), COLORS['btn_del'])
            self.create_btn(btns, "Usar Expr", lambda e=entry['expresion']: self.parent.set_display(e), COLORS['btn_op'])
            self.create_btn(btns, "Usar Res", lambda r=entry['resultado']: self.parent.append_to_display(str(r)), COLORS['btn_eq'])

    def delete_entry(self, idx):
        del self.historial[idx]
        self.populate()

    def clear_history(self):
        if messagebox.askyesno("Confirmar", "¿Borrar todo?", parent=self):
            self.historial.clear()
            self.populate()

    def export_history(self):
        if not self.historial: return
        fname = f"historial_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(fname, 'w', encoding='utf-8') as f:
            for e in self.historial:
                f.write(f"[{e['timestamp']}] {e['expresion']} = {e['resultado']}\n")
        messagebox.showinfo("Exportado", f"Guardado en {fname}", parent=self)

class ManagerWindow(BaseSubWindow):
    """Clase base para Variables y Funciones"""
    def __init__(self, parent, title, data_dict, is_function=False):
        super().__init__(parent, title)
        self.data = data_dict
        self.is_func = is_function
        
        # Formulario
        form = tk.LabelFrame(self, text="Nueva Entrada", padx=10, pady=10, bg="white")
        form.pack(fill="x", padx=10, pady=10)
        
        tk.Label(form, text="Nombre:", bg="white").grid(row=0, column=0)
        self.entry_name = tk.Entry(form)
        self.entry_name.grid(row=0, column=1, sticky="ew", padx=5)
        
        tk.Label(form, text="Expresión/Valor:", bg="white").grid(row=1, column=0)
        self.entry_val = tk.Entry(form)
        self.entry_val.grid(row=1, column=1, sticky="ew", padx=5)
        self.entry_val.bind('<Return>', lambda e: self.save())
        
        form.columnconfigure(1, weight=1)
        tk.Button(form, text="💾 Guardar", command=self.save, bg=COLORS['btn_eq'], fg="white").grid(row=2, column=0, columnspan=2, sticky="ew", pady=10)

        # Lista
        self.scroll_area = ScrollableFrame(self)
        self.scroll_area.pack(fill="both", expand=True, padx=10, pady=(0,10))
        self.populate()

    def populate(self):
        for w in self.scroll_area.scrollable_content.winfo_children(): w.destroy()
        
        # Recuperar constantes si es ventana de variables
        if not self.is_func:
            for k, v in MathEngine.ALLOWED_CONSTANTS.items():
                if k not in self.data: self.data[k] = v

        items = sorted(self.data.items())
        for name, val in items:
            f = tk.Frame(self.scroll_area.scrollable_content, bg="white", relief="solid", bd=1, pady=5)
            f.pack(fill="x", pady=2)
            
            txt = f"{name}() = {val}" if self.is_func else f"{name} = {val}"
            tk.Label(f, text=txt, font=("Consolas", 10), bg="white", anchor="w").pack(side="left", padx=10, fill="x", expand=True)
            
            is_const = name in MathEngine.ALLOWED_CONSTANTS
            if not is_const:
                self.create_btn(f, "✕", lambda n=name: self.delete(n), COLORS['btn_del'])
            
            self.create_btn(f, "Usar", lambda n=name: self.use(n), COLORS['btn_op'])
            if self.is_func:
                self.create_btn(f, "Eval", lambda n=name: self.eval_func(n), COLORS['btn_func'])

    def save(self):
        name = self.entry_name.get().strip()
        val = self.entry_val.get().strip()
        
        if not name.isidentifier():
            return messagebox.showerror("Error", "Nombre inválido", parent=self)
        
        if name in MathEngine.ALLOWED_CONSTANTS:
            return messagebox.showerror("Error", "Es una constante protegida", parent=self)
            
        try:
            # Validar y guardar
            if self.is_func:
                # Validar expresión
                MathEngine.evaluar(val, self.parent.variables, self.parent.funciones, self.parent.angle_mode)
                self.data[name] = val
            else:
                # Evaluar valor
                res = MathEngine.evaluar(val, self.parent.variables, self.parent.funciones, self.parent.angle_mode)
                self.data[name] = res
                
            self.populate()
            self.entry_name.delete(0, tk.END)
            self.entry_val.delete(0, tk.END)
        except Exception as e:
            messagebox.showerror("Error", str(e), parent=self)

    def delete(self, name):
        if messagebox.askyesno("Confirmar", f"¿Borrar {name}?"):
            del self.data[name]
            self.populate()

    def use(self, name):
        suffix = "()" if self.is_func else ""
        self.parent.append_to_display(name + suffix)

    def eval_func(self, name):
        try:
            res = MathEngine.evaluar(self.data[name], self.parent.variables, self.data, self.parent.angle_mode)
            messagebox.showinfo("Resultado", f"{res}", parent=self)
        except Exception as e:
            messagebox.showerror("Error", str(e), parent=self)

# --- APP PRINCIPAL ---

class CalculadoraApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Calculadora Científica")
        self.geometry("450x650")
        self.minsize(400, 600)
        self.configure(bg=COLORS['bg'])
        
        self.variables = MathEngine.ALLOWED_CONSTANTS.copy()
        self.funciones = {}
        self.history = []
        self.angle_mode = "RAD"
        
        self.display_var = tk.StringVar()
        self._init_ui()
        self._bind_keys()

    def _init_ui(self):
        # Top Bar
        top = tk.Frame(self, bg=COLORS['bg_dark'], pady=5)
        top.pack(fill="x", padx=5, pady=5)
        
        self.lbl_mode = tk.Button(top, text="RAD", command=self.toggle_mode, 
                                bg=COLORS['accent'], fg="white", relief="flat", width=6)
        self.lbl_mode.pack(side="left", padx=5)
        
        tk.Label(top, text="Calculadora Py", fg="#7f8c8d", bg=COLORS['bg_dark'], font=("Segoe UI", 9, "italic")).pack(side="right", padx=10)

        # Display
        entry = tk.Entry(self, textvariable=self.display_var, font=("Consolas", 24), 
                       bg="#ecf0f1", fg="#2c3e50", justify="right", bd=5, relief="flat")
        entry.pack(fill="x", padx=10, pady=10, ipady=10)
        entry.focus_set()
        self.display_entry = entry

        # Buttons
        btns_frame = tk.Frame(self, bg=COLORS['bg'])
        btns_frame.pack(expand=True, fill="both", padx=5, pady=5)
        
        layout = [
            [('sin', 'btn_func'), ('cos', 'btn_func'), ('tan', 'btn_func'), ('√', 'btn_func')],
            [('asin', 'btn_func'), ('acos', 'btn_func'), ('atan', 'btn_func'), ('^', 'btn_op')],
            [('ln', 'btn_func'), ('log', 'btn_func'), ('VAR', 'btn_func'), ('FUN', 'btn_func')],
            [('(', 'btn_num'), (')', 'btn_num'), ('C', 'btn_del'), ('AC', 'btn_del')],
            [('7', 'btn_num'), ('8', 'btn_num'), ('9', 'btn_num'), ('÷', 'btn_op')],
            [('4', 'btn_num'), ('5', 'btn_num'), ('6', 'btn_num'), ('×', 'btn_op')],
            [('1', 'btn_num'), ('2', 'btn_num'), ('3', 'btn_num'), ('-', 'btn_op')],
            [('0', 'btn_num'), ('.', 'btn_num'), ('HIST', 'btn_func'), ('+', 'btn_op')],
            [('=', 'btn_eq', 4)]
        ]

        for r, row in enumerate(layout):
            btns_frame.rowconfigure(r, weight=1)
            c_idx = 0
            for item in row:
                txt, color_key = item[0], item[1]
                colspan = item[2] if len(item) > 2 else 1
                
                cmd = lambda x=txt: self.handle_click(x)
                btn = tk.Button(btns_frame, text=txt, bg=COLORS[color_key], fg="white",
                              font=("Segoe UI", 12, "bold"), relief="flat", command=cmd)
                btn.grid(row=r, column=c_idx, columnspan=colspan, sticky="nsew", padx=2, pady=2)
                
                for k in range(colspan): btns_frame.columnconfigure(c_idx + k, weight=1)
                c_idx += colspan

    def _bind_keys(self):
        self.bind('<Return>', lambda e: self.calc())
        self.bind('<KP_Enter>', lambda e: self.calc())
        self.bind('<Escape>', lambda e: self.display_var.set(""))

    def toggle_mode(self):
        self.angle_mode = "DEG" if self.angle_mode == "RAD" else "RAD"
        self.lbl_mode.config(text=self.angle_mode)

    def handle_click(self, key):
        mapping = {'×': '*', '÷': '/', '^': '**', '√': 'sqrt(', 'ln': 'log(', 'log': 'log10('}
        
        if key == '=': self.calc()
        elif key == 'C': self.display_var.set("")
        elif key == 'AC': 
            self.display_var.set("")
            self.variables = MathEngine.ALLOWED_CONSTANTS.copy()
            self.funciones.clear()
            messagebox.showinfo("Reset", "Memoria borrada")
        elif key == 'VAR': ManagerWindow(self, "Variables", self.variables, False)
        elif key == 'FUN': ManagerWindow(self, "Funciones", self.funciones, True)
        elif key == 'HIST': HistorialWindow(self, self.history)
        elif key in ['sin', 'cos', 'tan', 'asin', 'acos', 'atan']: self.append_to_display(f"{key}(")
        else: self.append_to_display(mapping.get(key, key))

    def append_to_display(self, txt):
        curr = self.display_var.get()
        self.display_var.set(curr + txt)
        self.display_entry.icursor(tk.END)
        self.display_entry.focus()

    def set_display(self, txt):
        self.display_var.set(txt)
        self.display_entry.focus()

    def calc(self):
        expr = self.display_var.get()
        if not expr: return
        try:
            res = MathEngine.evaluar(expr, self.variables, self.funciones, self.angle_mode)
            
            # Formateo inteligente
            res_str = f"{int(res)}" if isinstance(res, float) and res.is_integer() else f"{res:.10g}"
            
            self.history.append({
                'timestamp': datetime.now().strftime("%H:%M:%S"),
                'mode': self.angle_mode, 'expresion': expr, 'resultado': res_str
            })
            self.display_var.set(res_str)
        except Exception as e:
            messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    app = CalculadoraApp()
    app.mainloop()