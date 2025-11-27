import pandas as pd
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from collections import Counter
import plotly.graph_objects as go
from plotly.io import to_html
import webbrowser
import os
import tempfile

class ExamAnalysisApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Exam Analysis Tool")
        self.root.geometry("600x500")
        
        # Instance variables
        self.df_students = None
        self.correct_answers = None
        self.results = []
        self.total_students = 0
        self.num_questions = 20
        self.current_question = 0
        self.chart_windows = {}  # Track open chart windows
        
        # Configure styles
        self.style = ttk.Style()
        self.style.configure("TButton", padding=6, font=('Arial', 10))
        self.style.configure("TLabel", font=('Arial', 11))
        
        # Initialize interface
        self.create_interface()
        
    def create_interface(self):
        """Set up the main GUI layout."""
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Control frame
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=5)
        
        # File loading button
        ttk.Button(control_frame, text="Load Excel File", command=self.load_excel).pack(side=tk.LEFT, padx=5)
        
        # Navigation buttons
        self.btn_prev = ttk.Button(control_frame, text="← Previous", command=self.previous_question, state=tk.DISABLED)
        self.btn_prev.pack(side=tk.LEFT, padx=5)
        
        self.btn_next = ttk.Button(control_frame, text="Next →", command=self.next_question, state=tk.DISABLED)
        self.btn_next.pack(side=tk.LEFT, padx=5)
        
        # Show all charts button
        self.btn_all_charts = ttk.Button(control_frame, text="Show All Charts", command=self.show_all_charts, state=tk.DISABLED)
        self.btn_all_charts.pack(side=tk.LEFT, padx=5)
        
        # Question label
        self.lbl_question = ttk.Label(control_frame, text=f"Question: 0/{self.num_questions}", font=('Arial', 12, 'bold'))
        self.lbl_question.pack(side=tk.LEFT, padx=20)
        
        # Statistics frame
        stats_frame = ttk.Frame(main_frame)
        stats_frame.pack(fill=tk.X, pady=10)
        
        # Summary labels
        self.lbl_summary = ttk.Label(stats_frame, text="Summary: No data loaded", font=('Arial', 10, 'bold'))
        self.lbl_summary.pack(anchor=tk.W, pady=2)
        
        self.lbl_correct = ttk.Label(stats_frame, text="Correct Answer: -", font=('Arial', 10))
        self.lbl_correct.pack(anchor=tk.W, pady=2)
        
        self.lbl_correct_count = ttk.Label(stats_frame, text="Correct Responses: - (-%)", font=('Arial', 10))
        self.lbl_correct_count.pack(anchor=tk.W, pady=2)
        
        self.lbl_distribution = ttk.Label(stats_frame, text="Distribution: -", font=('Arial', 10))
        self.lbl_distribution.pack(anchor=tk.W, pady=2)
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, orient=tk.HORIZONTAL, length=300, mode='determinate')
        self.progress.pack(pady=10)
        
        # Listbox for question selection
        self.question_listbox = tk.Listbox(main_frame, height=10, font=('Arial', 10))
        self.question_listbox.pack(fill=tk.X, pady=5)
        self.question_listbox.bind('<<ListboxSelect>>', self.on_question_select)
    
    def load_excel(self):
        """Load and process Excel file."""
        file_path = filedialog.askopenfilename(
            title="Select Excel File",
            filetypes=[("Excel files", "*.xlsx *.xls"), ("All files", "*.*")]
        )
        
        if not file_path:
            return
            
        try:
            self.df_students, self.correct_answers = self.read_exam(file_path)
            self.results, self.total_students = self.analyze_questions()
            self.current_question = 0
            self.update_interface()
            self.update_listbox()
            self.btn_prev.config(state=tk.NORMAL)
            self.btn_next.config(state=tk.NORMAL)
            self.btn_all_charts.config(state=tk.NORMAL)
            messagebox.showinfo("Success", "Excel file loaded successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load file: {str(e)}")
    
    def read_exam(self, file_path):
        """Read exam data from Excel file."""
        df = pd.read_excel(file_path, header=None, engine='openpyxl')
        
        if df.shape[1] < self.num_questions + 1:
            raise ValueError(f"Excel file must contain at least {self.num_questions + 1} columns")
            
        names = df.iloc[2:, 0].dropna().tolist()
        correct_answers = df.iloc[1, 1:self.num_questions + 1].tolist()
        student_responses = df.iloc[2:, 1:self.num_questions + 1]
        
        df_students = pd.DataFrame(
            student_responses.values,
            index=names,
            columns=[f"Q{i+1}" for i in range(self.num_questions)]
        )
        
        return df_students, correct_answers
    
    def analyze_questions(self):
        """Analyze response distribution for each question."""
        total_students = len(self.df_students)
        results = []
        
        # Preprocess responses once
        responses = self.df_students.astype(str).apply(lambda x: x.str.strip())
        
        for i in range(self.num_questions):
            question = f"Q{i+1}"
            correct_answer = str(self.correct_answers[i]).strip()
            response_counts = Counter(responses[question])
            
            # Ensure all options are included
            for option in ['1', '2', '3', '4']:
                response_counts.setdefault(option, 0)
            
            correct_count = response_counts.get(correct_answer, 0)
            percentage = (correct_count / total_students * 100) if total_students > 0 else 0
            
            results.append({
                'number': i + 1,
                'correct': correct_answer,
                'correct_count': correct_count,
                'percentage': percentage,
                'distribution': dict(sorted(response_counts.items())),
                'options': sorted(response_counts.keys())
            })
        
        return results, total_students
    
    def create_chart(self, question):
        """Create a Plotly bar chart for a question."""
        options = question['options']
        counts = [question['distribution'].get(opt, 0) for opt in options]
        colors = ['#4CAF50' if opt == question['correct'] else '#2196F3' for opt in options]
        
        fig = go.Figure(data=[
            go.Bar(
                x=options,
                y=counts,
                marker_color=colors,
                text=counts,
                textposition='auto',
                hovertemplate='Option %{x}: %{y} students<extra></extra>'
            )
        ])
        
        fig.update_layout(
            title=f"Question {question['number']} - Response Distribution",
            xaxis_title="Response Options",
            yaxis_title="Number of Students",
            yaxis=dict(range=[0, max(counts) * 1.2]),
            showlegend=False,
            template='plotly_white',
            width=600,
            height=400
        )
        
        return fig
    
    def show_chart(self, question_num):
        """Show the chart for a specific question in a new window."""
        if not self.results:
            return
            
        question = self.results[question_num - 1]
        
        # Create or focus existing chart window
        if question_num in self.chart_windows:
            chart_window = self.chart_windows[question_num]
            if chart_window.winfo_exists():
                chart_window.lift()
                return
            else:
                del self.chart_windows[question_num]
        
        # Create new chart window
        chart_window = tk.Toplevel(self.root)
        chart_window.title(f"Chart - Question {question_num}")
        chart_window.geometry("650x450")
        
        # Create chart
        fig = self.create_chart(question)
        
        # Save chart to temporary HTML file
        with tempfile.NamedTemporaryFile('w', delete=False, suffix='.html') as f:
            f.write(to_html(fig, include_plotlyjs='cdn'))
            temp_file = f.name
        
        # Open chart in browser
        webbrowser.open(f'file://{temp_file}')
        
        # Clean up on window close
        def on_close():
            try:
                os.unlink(temp_file)
            except:
                pass
            if question_num in self.chart_windows:
                del self.chart_windows[question_num]
            chart_window.destroy()
        
        chart_window.protocol("WM_DELETE_WINDOW", on_close)
        self.chart_windows[question_num] = chart_window
    
    def show_all_charts(self):
        """Show charts for all questions."""
        for i in range(self.num_questions):
            self.show_chart(i + 1)
    
    def update_interface(self):
        """Update the main GUI with current question data."""
        if not self.results:
            return
        
        question = self.results[self.current_question]
        
        # Update summary
        easiest = max(self.results, key=lambda x: x['percentage'])['number']
        hardest = min(self.results, key=lambda x: x['percentage'])['number']
        self.lbl_summary.config(text=f"Summary: {self.total_students} students | Easiest: Q{easiest} | Hardest: Q{hardest}")
        
        # Update question details
        self.lbl_question.config(text=f"Question: {question['number']}/{self.num_questions}")
        self.lbl_correct.config(text=f"Correct Answer: Option {question['correct']}")
        self.lbl_correct_count.config(text=f"Correct Responses: {question['correct_count']} ({question['percentage']:.1f}%)")
        
        dist_text = " | ".join([f"Option {k}: {v}" for k, v in question['distribution'].items()])
        self.lbl_distribution.config(text=f"Distribution: {dist_text}")
        
        # Update progress bar
        self.progress['value'] = (self.current_question + 1) / self.num_questions * 100
        
        # Update navigation buttons
        self.btn_prev.config(state=tk.NORMAL if self.current_question > 0 else tk.DISABLED)
        self.btn_next.config(state=tk.NORMAL if self.current_question < self.num_questions - 1 else tk.DISABLED)
    
    def update_listbox(self):
        """Populate listbox with question numbers."""
        self.question_listbox.delete(0, tk.END)
        for i in range(self.num_questions):
            self.question_listbox.insert(tk.END, f"Question {i + 1}")
        self.question_listbox.select_set(0)
    
    def on_question_select(self, event):
        """Handle question selection from listbox."""
        selection = self.question_listbox.curselection()
        if selection:
            self.current_question = selection[0]
            self.update_interface()
            self.show_chart(self.current_question + 1)
    
    def next_question(self):
        """Navigate to the next question."""
        if self.current_question < self.num_questions - 1:
            self.current_question += 1
            self.question_listbox.select_clear(0, tk.END)
            self.question_listbox.select_set(self.current_question)
            self.update_interface()
    
    def previous_question(self):
        """Navigate to the previous question."""
        if self.current_question > 0:
            self.current_question -= 1
            self.question_listbox.select_clear(0, tk.END)
            self.question_listbox.select_set(self.current_question)
            self.update_interface()

if __name__ == "__main__":
    root = tk.Tk()
    app = ExamAnalysisApp(root)
    root.mainloop()