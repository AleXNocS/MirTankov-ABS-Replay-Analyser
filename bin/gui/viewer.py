import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from datetime import datetime
import csv

class TableViewer:
    def __init__(self, headers, data, total_battles, total_wins):
        self.headers = headers
        self.data = data
        self.total_battles = total_battles
        self.total_wins = total_wins
        self.win_percentage = (total_wins / total_battles * 100) if total_battles > 0 else 0
        self.window = tk.Tk()
        self.window.title("📊 Результаты анализа реплеев")
        self.window.geometry("1400x750")
        
        # Делаем окно поверх всех
        self.window.attributes('-topmost', True)
        
        self.setup_ui()
        
    def setup_ui(self):
        # Верхняя панель с информацией
        info_frame = tk.Frame(self.window)
        info_frame.pack(fill=tk.X, padx=10, pady=5)
        
        info_label = tk.Label(info_frame, 
                             text=f"🎮 Всего боёв: {self.total_battles}  |  🏆 Побед: {self.total_wins} ({self.win_percentage:.1f}%)",
                             font=('Arial', 11, 'bold'))
        info_label.pack(side=tk.LEFT)
        
        # Кнопки
        button_frame = tk.Frame(self.window)
        button_frame.pack(fill=tk.X, padx=10, pady=5)
        
        save_btn = tk.Button(button_frame, text="💾 Сохранить в CSV", 
                            command=self.save_csv, bg='#4CAF50', fg='white',
                            font=('Arial', 10, 'bold'), padx=20)
        save_btn.pack(side=tk.LEFT, padx=5)
        
        close_btn = tk.Button(button_frame, text="❌ Закрыть", 
                             command=self.window.quit, bg='#f44336', fg='white',
                             font=('Arial', 10, 'bold'), padx=20)
        close_btn.pack(side=tk.LEFT, padx=5)
        
        # Таблица
        table_frame = tk.Frame(self.window)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Создаем Scrollbar
        vsb = tk.Scrollbar(table_frame, orient="vertical")
        hsb = tk.Scrollbar(table_frame, orient="horizontal")
        
        # Создаем Treeview
        self.tree = ttk.Treeview(table_frame, 
                                 columns=list(range(len(self.headers))),
                                 show="headings",
                                 yscrollcommand=vsb.set,
                                 xscrollcommand=hsb.set)
        
        vsb.config(command=self.tree.yview)
        hsb.config(command=self.tree.xview)
        
        # НАСТРОЙКА СТИЛЕЙ
        style = ttk.Style()
        
        # Стиль для Treeview (строки данных)
        style.configure("Custom.Treeview", 
                       font=('Arial', 9),
                       rowheight=28,
                       background="white",
                       fieldbackground="white")
        
        # Стиль для заголовков с увеличенным отступом снизу
        style.configure("Custom.Treeview.Heading", 
                       font=('Arial', 9, 'bold'),
                       padding=(5, 5, 5, 15),
                       relief="raised")
        
        # Применяем стили
        self.tree.configure(style="Custom.Treeview")
        
        # Настраиваем заголовки
        for i, header in enumerate(self.headers):
            self.tree.heading(i, text=header, anchor='center')
            
            # Устанавливаем ширину колонок
            if i == 0:
                self.tree.column(i, width=150, minwidth=100, anchor='w')
            elif i == 1 or i == 2:
                self.tree.column(i, width=90, minwidth=70, anchor='center')
            else:
                self.tree.column(i, width=200, minwidth=160, anchor='center')
        
        # Добавляем данные
        for row in self.data:
            self.tree.insert("", tk.END, values=row)
        
        # Размещаем таблицу и скроллы
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)
        
        # Статус бар
        self.status_bar = tk.Label(self.window, text="Готово", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def save_csv(self):
        """Сохраняет данные в CSV"""
        save_path = filedialog.asksaveasfilename(
            title="Сохранить CSV файл",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile=f"battle_matrix_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
        )
        
        if save_path:
            with open(save_path, 'w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(self.headers)
                writer.writerows(self.data)
            
            self.status_bar.config(text=f"✅ Файл сохранен: {save_path}")
            messagebox.showinfo("Готово", f"Файл успешно сохранен:\n{save_path}")
    
    def run(self):
        self.window.mainloop()