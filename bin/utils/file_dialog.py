import tkinter as tk
from tkinter import filedialog

def select_files_gui():
    """Открывает диалог выбора файлов"""
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    
    file_paths = filedialog.askopenfilenames(
        title="Выберите файлы реплеев (.mtreplay)",
        filetypes=[("MT Replay files", "*.mtreplay"), ("All files", "*.*")]
    )
    
    root.destroy()
    return list(file_paths)