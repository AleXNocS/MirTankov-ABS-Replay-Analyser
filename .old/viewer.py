import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from datetime import datetime
import csv

class TableViewer:
    def __init__(self, headers, data, total_battles, total_wins):
        self.headers = headers
        self.original_data = data
        self.data = data.copy()
        self.total_battles = total_battles
        self.total_wins = total_wins
        self.win_percentage = (total_wins / total_battles * 100) if total_battles > 0 else 0
        self.sort_column = None
        self.sort_reverse = False
        self.search_var = None
        self.dark_mode = True
        
        self.window = tk.Tk()
        self.window.title("📊 Результаты анализа реплеев")
        self.window.geometry("1400x800")
        
        # Делаем окно поверх всех только при запуске
        self.window.attributes('-topmost', True)
        self.window.after(500, lambda: self.window.attributes('-topmost', False))
        
        # Цветовые схемы
        self.setup_colors()
        self.setup_ui()
        self.apply_theme()
        
    def setup_colors(self):
        """Настраивает цвета в зависимости от темы"""
        if self.dark_mode:
            # Темная тема
            self.bg_color = '#2d2d2d'
            self.fg_color = '#ffffff'
            self.frame_bg = '#3d3d3d'
            self.entry_bg = '#4d4d4d'
            self.entry_fg = '#ffffff'
            self.button_bg = '#4d4d4d'
            self.button_fg = '#ffffff'
            self.tree_bg = '#3d3d3d'
            self.tree_fg = '#ffffff'
            self.tree_heading_bg = '#4d4d4d'
            self.tree_heading_fg = '#ffffff'
            self.status_bg = '#3d3d3d'
            self.status_fg = '#cccccc'
            self.highlight_color = '#5d5d5d'
        else:
            # Светлая тема
            self.bg_color = '#f0f0f0'
            self.fg_color = '#000000'
            self.frame_bg = '#e0e0e0'
            self.entry_bg = '#ffffff'
            self.entry_fg = '#000000'
            self.button_bg = '#e0e0e0'
            self.button_fg = '#000000'
            self.tree_bg = '#ffffff'
            self.tree_fg = '#000000'
            self.tree_heading_bg = '#e0e0e0'
            self.tree_heading_fg = '#000000'
            self.status_bg = '#e0e0e0'
            self.status_fg = '#333333'
            self.highlight_color = '#d0d0d0'
    
    def apply_theme(self):
        """Применяет текущую цветовую схему ко всем элементам"""
        self.window.configure(bg=self.bg_color)
        
        # Обновляем цвета для всех фреймов
        for widget in self.window.winfo_children():
            if isinstance(widget, tk.Frame):
                try:
                    widget.configure(bg=self.frame_bg)
                except:
                    pass
                self._apply_theme_to_children(widget)
        
        # Обновляем стиль Treeview
        style = ttk.Style()
        style.theme_use('default')
        
        style.configure("Custom.Treeview",
                       background=self.tree_bg,
                       foreground=self.tree_fg,
                       fieldbackground=self.tree_bg,
                       font=('Arial', 9),
                       rowheight=28)
        
        style.configure("Custom.Treeview.Heading",
                       background=self.tree_heading_bg,
                       foreground=self.tree_heading_fg,
                       font=('Arial', 9, 'bold'),
                       padding=(5, 5, 5, 15),
                       relief="raised")
        
        style.map('Custom.Treeview',
                  background=[('selected', self.highlight_color)],
                  foreground=[('selected', self.tree_fg)])
        
        self.tree.configure(style="Custom.Treeview")
        self.status_bar.configure(bg=self.status_bg, fg=self.status_fg)
        
        theme_text = "🌙 Темная" if not self.dark_mode else "☀️ Светлая"
        self.theme_btn.configure(text=theme_text)
    
    def _apply_theme_to_children(self, parent):
        """Рекурсивно применяет тему к дочерним элементам"""
        for child in parent.winfo_children():
            if isinstance(child, tk.Frame):
                try:
                    child.configure(bg=self.frame_bg)
                except:
                    pass
                self._apply_theme_to_children(child)
            elif isinstance(child, tk.Label):
                try:
                    child.configure(bg=self.frame_bg, fg=self.fg_color)
                except:
                    pass
            elif isinstance(child, tk.Entry):
                try:
                    child.configure(bg=self.entry_bg, fg=self.entry_fg,
                                  insertbackground=self.fg_color)
                except:
                    pass
            elif isinstance(child, tk.Button):
                try:
                    child.configure(bg=self.button_bg, fg=self.button_fg,
                                  activebackground=self.highlight_color)
                except:
                    pass
            elif isinstance(child, ttk.Combobox):
                try:
                    style = ttk.Style()
                    style.configure("Custom.TCombobox",
                                  fieldbackground=self.entry_bg,
                                  background=self.entry_bg,
                                  foreground=self.entry_fg,
                                  arrowcolor=self.fg_color)
                    child.configure(style="Custom.TCombobox")
                except:
                    pass
    
    def toggle_theme(self):
        """Переключает между темной и светлой темой"""
        self.dark_mode = not self.dark_mode
        self.setup_colors()
        self.apply_theme()
    
    def setup_ui(self):
        # Верхняя панель с информацией
        info_frame = tk.Frame(self.window)
        info_frame.pack(fill=tk.X, padx=10, pady=5)
        
        info_label = tk.Label(info_frame, 
                             text=f"🎮 Всего боёв: {self.total_battles}  |  🏆 Побед: {self.total_wins} ({self.win_percentage:.1f}%)",
                             font=('Arial', 11, 'bold'))
        info_label.pack(side=tk.LEFT)
        
        self.theme_btn = tk.Button(info_frame, 
                                   text="☀️ Светлая" if self.dark_mode else "🌙 Темная",
                                   command=self.toggle_theme,
                                   font=('Arial', 9), padx=10)
        self.theme_btn.pack(side=tk.RIGHT, padx=5)
        
        # Панель поиска и сортировки
        control_frame = tk.Frame(self.window)
        control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        search_label = tk.Label(control_frame, text="🔍 Поиск игрока:", font=('Arial', 9))
        search_label.pack(side=tk.LEFT, padx=5)
        
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.filter_data)
        search_entry = tk.Entry(control_frame, textvariable=self.search_var, 
                               width=30, font=('Arial', 9))
        search_entry.pack(side=tk.LEFT, padx=5)
        
        clear_btn = tk.Button(control_frame, text="✖", command=self.clear_search, 
                             font=('Arial', 8), width=2)
        clear_btn.pack(side=tk.LEFT, padx=2)
        
        tk.Frame(control_frame, width=20).pack(side=tk.LEFT)
        
        sort_label = tk.Label(control_frame, text="📊 Сортировать по:", font=('Arial', 9))
        sort_label.pack(side=tk.LEFT, padx=5)
        
        self.sort_var = tk.StringVar(value="Игрок (А-Я)")
        sort_combo = ttk.Combobox(control_frame, textvariable=self.sort_var, 
                                  values=["Игрок (А-Я)", "Игрок (Я-А)", 
                                          "Ср.урон (возр)", "Ср.урон (убыв)",
                                          "Боёв (возр)", "Боёв (убыв)"],
                                  state="readonly", width=15, font=('Arial', 9))
        sort_combo.pack(side=tk.LEFT, padx=5)
        sort_combo.bind('<<ComboboxSelected>>', self.sort_data)
        
        # Кнопки
        button_frame = tk.Frame(self.window)
        button_frame.pack(fill=tk.X, padx=10, pady=5)
        
        save_btn = tk.Button(button_frame, text="💾 Сохранить в CSV", 
                            command=self.save_csv, bg='#4CAF50', fg='white',
                            activebackground='#45a049',
                            font=('Arial', 10, 'bold'), padx=20)
        save_btn.pack(side=tk.LEFT, padx=5)
        
        reset_btn = tk.Button(button_frame, text="🔄 Сбросить", 
                             command=self.reset_view, bg='#FFA500', fg='white',
                             activebackground='#ff8c00',
                             font=('Arial', 10, 'bold'), padx=20)
        reset_btn.pack(side=tk.LEFT, padx=5)
        
        close_btn = tk.Button(button_frame, text="❌ Закрыть", 
                             command=self.window.quit, bg='#f44336', fg='white',
                             activebackground='#da190b',
                             font=('Arial', 10, 'bold'), padx=20)
        close_btn.pack(side=tk.LEFT, padx=5)
        
        self.filter_stats_label = tk.Label(button_frame, text="", font=('Arial', 9), fg='gray')
        self.filter_stats_label.pack(side=tk.RIGHT, padx=10)
        
        # Таблица
        table_frame = tk.Frame(self.window)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        vsb = tk.Scrollbar(table_frame, orient="vertical")
        hsb = tk.Scrollbar(table_frame, orient="horizontal")
        
        self.tree = ttk.Treeview(table_frame, 
                                 columns=list(range(len(self.headers))),
                                 show="headings",
                                 yscrollcommand=vsb.set,
                                 xscrollcommand=hsb.set)
        
        vsb.config(command=self.tree.yview)
        hsb.config(command=self.tree.xview)
        
        for i, header in enumerate(self.headers):
            self.tree.heading(i, text=header, anchor='center')
            
            if i == 0:
                self.tree.column(i, width=150, minwidth=100, anchor='w')
            elif i == 1 or i == 2:
                self.tree.column(i, width=90, minwidth=70, anchor='center')
            else:
                self.tree.column(i, width=250, minwidth=200, anchor='center')  # Увеличил ширину
        
        self.refresh_table()
        
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)
        
        self.status_bar = tk.Label(self.window, text="Готово", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def refresh_table(self):
        """Обновляет таблицу с текущими данными"""
        for row in self.tree.get_children():
            self.tree.delete(row)
        
        for row in self.data:
            self.tree.insert("", tk.END, values=row)
        
        total_players = len(self.original_data)
        shown_players = len(self.data)
        if shown_players < total_players:
            self.filter_stats_label.config(text=f"Показано: {shown_players} из {total_players}")
        else:
            self.filter_stats_label.config(text="")
    
    def filter_data(self, *args):
        """Фильтрует данные по введенному тексту"""
        search_text = self.search_var.get().lower().strip()
        
        if not search_text:
            self.data = self.original_data.copy()
        else:
            self.data = [row for row in self.original_data 
                        if search_text in row[0].lower()]
        
        self.apply_sort()
        self.refresh_table()
    
    def clear_search(self):
        """Очищает поле поиска"""
        self.search_var.set("")
        self.filter_data()
    
    def sort_data(self, event=None):
        """Сортирует данные по выбранному критерию"""
        sort_by = self.sort_var.get()
        
        if sort_by == "Игрок (А-Я)":
            self.data.sort(key=lambda x: x[0].lower())
        elif sort_by == "Игрок (Я-А)":
            self.data.sort(key=lambda x: x[0].lower(), reverse=True)
        elif sort_by == "Ср.урон (возр)":
            self.data.sort(key=lambda x: x[1] if isinstance(x[1], (int, float)) else 0)
        elif sort_by == "Ср.урон (убыв)":
            self.data.sort(key=lambda x: x[1] if isinstance(x[1], (int, float)) else 0, reverse=True)
        elif sort_by == "Боёв (возр)":
            self.data.sort(key=lambda x: x[2] if isinstance(x[2], (int, float)) else 0)
        elif sort_by == "Боёв (убыв)":
            self.data.sort(key=lambda x: x[2] if isinstance(x[2], (int, float)) else 0, reverse=True)
        
        self.refresh_table()
    
    def apply_sort(self):
        """Применяет текущую сортировку к данным"""
        sort_by = self.sort_var.get()
        if sort_by:
            self.sort_data()
    
    def reset_view(self):
        """Сбрасывает все фильтры и сортировку"""
        self.search_var.set("")
        self.sort_var.set("Игрок (А-Я)")
        self.data = self.original_data.copy()
        self.sort_data()
        self.refresh_table()
        self.status_bar.config(text="🔄 Вид сброшен")
    
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
                writer.writerows(self.original_data)
            
            self.status_bar.config(text=f"✅ Файл сохранен: {save_path}")
            messagebox.showinfo("Готово", f"Файл успешно сохранен:\n{save_path}")
    
    def run(self):
        self.window.mainloop()