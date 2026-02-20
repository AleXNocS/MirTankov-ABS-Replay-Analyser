import json
import sys
import os
import glob
from pathlib import Path
from collections import defaultdict
from datetime import datetime
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import csv

class BattleMatrixAnalyzer:
    def __init__(self):
        self.players = set()
        self.battles = []
        self.battle_data = defaultdict(dict)
        self.player_battles = defaultdict(int)
        
    def extract_json_from_replay(self, replay_path):
        """Извлекает metadata и results из .mtreplay файла"""
        try:
            with open(replay_path, 'rb') as f:
                data = f.read()
        except Exception as e:
            print(f"  ❌ Ошибка чтения файла: {e}")
            return None, None
        
        # Ищем JSON блоки
        metadata = None
        results = None
        pos = 0
        
        while pos < len(data) - 1000 and (not metadata or not results):
            if data[pos] == ord('{'):
                end, depth, in_str, esc = pos, 0, False, False
                while end < len(data):
                    b = data[end]
                    if not in_str:
                        if b == ord('{'): depth += 1
                        elif b == ord('}'): 
                            depth -= 1
                            if depth == 0: break
                    elif b == ord('"') and not esc: in_str = not in_str
                    if b == ord('\\') and not esc: esc = True
                    else: esc = False
                    end += 1
                
                if depth == 0:
                    try:
                        j = json.loads(data[pos:end+1].decode('utf-8', errors='ignore'))
                        if 'clientVersionFromXml' in j: 
                            metadata = j
                        if 'vehicles' in j and 'personal' in j and 'common' in j: 
                            results = j
                    except: 
                        pass
            pos += 1
        
        return metadata, results
    
    def process_replay(self, replay_path):
        """Обрабатывает один реплей"""
        print(f"\n📁 Обработка: {Path(replay_path).name}")
        
        metadata, results = self.extract_json_from_replay(replay_path)
        
        if not metadata or not results:
            print("  ⚠️ Не удалось извлечь данные, пропускаем")
            return False
        
        # Получаем информацию о бое
        map_name = metadata.get('mapDisplayName', 'Неизвестно')
        date_time = metadata.get('dateTime', 'Неизвестно')
        
        # Создаем ID для боя
        battle_id = f"{date_time}_{map_name}"
        
        # Добавляем бой в список
        self.battles.append({
            'id': battle_id,
            'date': date_time,
            'map': map_name,
            'file': Path(replay_path).name
        })
        
        # Собираем всех игроков
        vehicles_meta = metadata.get('vehicles', {})
        vehicles_stats = results.get('vehicles', {})
        
        battle_players = set()
        
        for vid, v in vehicles_meta.items():
            if not isinstance(v, dict):
                continue
            
            player_name = v.get('name', 'Unknown')
            
            # Добавляем игрока в общий список
            self.players.add(player_name)
            battle_players.add(player_name)
            
            # Получаем урон
            stats = vehicles_stats.get(vid, [{}])[0]
            damage = stats.get('damageDealt', 0)
            
            # Сохраняем урон для этого боя (даже если 0)
            self.battle_data[battle_id][player_name] = damage
        
        # Увеличиваем счетчик боёв для каждого игрока в этом бою
        for player in battle_players:
            self.player_battles[player] += 1
        
        print(f"  ✅ Добавлен бой: {date_time} - {map_name}")
        print(f"     Участников: {len(battle_players)}")
        return True
    
    def process_files(self, file_paths):
        """Обрабатывает список файлов"""
        if not file_paths:
            print("❌ Файлы не выбраны")
            return False
        
        print(f"\n{'='*80}")
        print(f"🔍 Выбрано файлов для анализа: {len(file_paths)}")
        print(f"{'='*80}")
        
        processed = 0
        for file_path in sorted(file_paths):
            if self.process_replay(file_path):
                processed += 1
        
        print(f"\n{'='*80}")
        print(f"✅ Успешно обработано файлов: {processed}/{len(file_paths)}")
        print(f"👥 Уникальных игроков: {len(self.players)}")
        print(f"{'='*80}")
        
        return processed > 0
    
    def get_table_data(self):
        """Возвращает данные для таблицы"""
        # Сортируем бои по дате
        self.battles.sort(key=lambda x: x['date'])
        
        # Сортируем игроков по алфавиту
        sorted_players = sorted(self.players)
        
        # ФОРМИРУЕМ ЗАГОЛОВКИ: дата + карта в одной строке
        headers = ['Игрок', 'Ср.урон', 'Боёв']
        for battle in self.battles:
            date_part = battle['date'][:16]  # "19.02.2026 20:55"
            map_part = battle['map']
            headers.append(f"{date_part} {map_part}")
        
        # Создаем данные
        data = []
        for player in sorted_players:
            total_damage = 0
            battles_list = []
            
            for battle in self.battles:
                if player in self.battle_data[battle['id']]:
                    damage = self.battle_data[battle['id']][player]
                    battles_list.append(damage)
                    total_damage += damage
                else:
                    battles_list.append('-')
            
            battles_count = self.player_battles[player]
            avg_damage = round(total_damage / battles_count) if battles_count > 0 else 0
            
            row = [player, avg_damage, battles_count] + battles_list
            data.append(row)
        
        return headers, data, len(self.battles)
    
    def export_to_csv(self, filename):
        """Экспортирует матрицу боев в CSV"""
        headers, data, _ = self.get_table_data()
        
        with open(filename, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(headers)  # Убрали replace, так как переносов строк нет
            writer.writerows(data)
        
        print(f"\n💾 Матрица боев экспортирована в {filename}")
        return True

class TableViewer:
    def __init__(self, headers, data, total_battles):
        self.headers = headers
        self.data = data
        self.total_battles = total_battles
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
        
        total_players = len(self.data)
        
        info_label = tk.Label(info_frame, 
                             text=f"🎮 Всего боёв: {self.total_battles}  |  👥 Всего игроков: {total_players}",
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
                       padding=(5, 5, 5, 15),  # Большой отступ снизу для запаса
                       relief="raised")
        
        # Применяем стили
        self.tree.configure(style="Custom.Treeview")
        
        # Настраиваем заголовки
        for i, header in enumerate(self.headers):
            self.tree.heading(i, text=header, anchor='center')
            
            # Устанавливаем ширину колонок
            if i == 0:  # Игрок
                self.tree.column(i, width=150, minwidth=100, anchor='w')
            elif i == 1 or i == 2:  # Ср.урон и Боёв
                self.tree.column(i, width=90, minwidth=70, anchor='center')
            else:  # Колонки с уроном
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
                writer.writerow(self.headers)  # Переносов строк нет
                writer.writerows(self.data)
            
            self.status_bar.config(text=f"✅ Файл сохранен: {save_path}")
            messagebox.showinfo("Готово", f"Файл успешно сохранен:\n{save_path}")
    
    def run(self):
        self.window.mainloop()

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

def main():
    print("\n" + "=" * 60)
    print("🎮 АНАЛИЗАТОР РЕПЛЕЕВ МИР ТАНКОВ")
    print("=" * 60)
    print("\n📂 Открывается окно выбора файлов...")
    
    # Выбираем файлы через проводник
    file_paths = select_files_gui()
    
    if not file_paths:
        print("❌ Файлы не выбраны. Выход.")
        input("\nНажмите Enter для выхода...")
        return
    
    # Создаем анализатор
    analyzer = BattleMatrixAnalyzer()
    
    # Анализируем выбранные файлы
    if analyzer.process_files(file_paths):
        # Получаем данные для таблицы
        headers, data, total_battles = analyzer.get_table_data()
        
        # Показываем таблицу
        print("\n📊 Открывается окно с таблицей результатов...")
        viewer = TableViewer(headers, data, total_battles)
        viewer.run()
        
        print("\n✅ Работа завершена")
    else:
        print("\n❌ Не удалось обработать файлы")
    
    # input("\nНажмите Enter для выхода...")

if __name__ == "__main__":
    main()