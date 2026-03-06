import sys
import os
from pathlib import Path
from datetime import datetime
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTableWidget, QTableWidgetItem,
    QHeaderView, QLineEdit, QFileDialog,
    QMessageBox, QStatusBar, QMenuBar, QMenu, QFrame,
    QButtonGroup, QRadioButton, QApplication
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QFont
from PyQt6.QtGui import QAction, QFont, QColor
import qdarkstyle

# Добавляем путь к родительской папке для импорта моделей
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.analyzer import BattleMatrixAnalyzer
from models.analyzer_random import RandomBattleAnalyzer
from utils.file_dialog import select_files_gui
from utils.clan_extractor import ClanExtractor  # Добавляем импорт для кланов

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.abs_analyzer = None
        self.random_analyzer = None
        self.current_mode = "abs"  # "abs" или "random"
        self.current_abs_data = []  # Сохраняем текущие данные АБС режима для сброса
        self.battle_clans = []  # Список кланов для каждого боя
        
        self.init_ui()
        self.apply_dark_theme()
        
    def init_ui(self):
        """Инициализация интерфейса"""
        self.setWindowTitle("🎮 MirTankov ABS Replay Analyzer")
        self.setMinimumSize(1400, 800)
        
        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Главный вертикальный layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Создаем меню
        self.create_menu()
        
        # Верхняя панель с информацией и режимами
        top_layout = QHBoxLayout()
        
        # Группа выбора режима
        mode_group = QFrame()
        mode_group.setFrameShape(QFrame.Shape.StyledPanel)
        mode_layout = QHBoxLayout(mode_group)
        mode_layout.setContentsMargins(5, 5, 5, 5)
        
        mode_label = QLabel("🎯 Режим:")
        mode_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        mode_layout.addWidget(mode_label)
        
        self.abs_radio = QRadioButton("АБС (все игроки)")
        self.abs_radio.setChecked(True)
        self.abs_radio.toggled.connect(self.change_mode)
        mode_layout.addWidget(self.abs_radio)
        
        self.random_radio = QRadioButton("Случайные (только вы)")
        self.random_radio.toggled.connect(self.change_mode)
        mode_layout.addWidget(self.random_radio)
        
        top_layout.addWidget(mode_group)
        top_layout.addStretch()
        
        # Информационная метка
        self.info_label = QLabel("🎮 Выберите файлы для анализа")
        self.info_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        top_layout.addWidget(self.info_label)
        
        main_layout.addLayout(top_layout)
        
        # Панель поиска и сброса
        control_layout = QHBoxLayout()
        
        # Поиск
        search_label = QLabel("🔍 Поиск игрока:")
        search_label.setFont(QFont("Arial", 10))
        control_layout.addWidget(search_label)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Введите имя игрока...")
        self.search_input.setFixedWidth(300)
        self.search_input.textChanged.connect(self.filter_table)
        control_layout.addWidget(self.search_input)
        
        # Разделитель
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.VLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setFixedWidth(2)
        control_layout.addWidget(separator)
        
        # Кнопка сброса поиска
        self.reset_search_btn = QPushButton("🔄 Сбросить поиск")
        self.reset_search_btn.setFont(QFont("Arial", 10))
        self.reset_search_btn.setFixedWidth(150)
        self.reset_search_btn.clicked.connect(self.reset_search)
        self.reset_search_btn.setEnabled(False)
        control_layout.addWidget(self.reset_search_btn)
        
        control_layout.addStretch()
        
        main_layout.addLayout(control_layout)
        
        # Таблица
        self.table = QTableWidget()
        self.table.setSortingEnabled(True)  # Включаем сортировку по заголовкам
        self.table.setAlternatingRowColors(True)
        self.table.setWordWrap(True)
        
        # Настройка заголовков таблицы
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        header.setStretchLastSection(False)
        header.setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setSectionsClickable(True)  # Заголовки кликабельны для сортировки
        
        # Высота строк
        self.table.verticalHeader().setDefaultSectionSize(30)
        
        main_layout.addWidget(self.table, 1)
        
        # Панель кнопок
        button_layout = QHBoxLayout()
        
        self.select_btn = QPushButton("📂 Выбрать файлы")
        self.select_btn.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        self.select_btn.setFixedHeight(40)
        self.select_btn.clicked.connect(self.select_files)
        button_layout.addWidget(self.select_btn)
        
        self.save_btn = QPushButton("💾 Сохранить в CSV")
        self.save_btn.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        self.save_btn.setFixedHeight(40)
        self.save_btn.clicked.connect(self.save_csv)
        self.save_btn.setEnabled(False)
        button_layout.addWidget(self.save_btn)
        
        button_layout.addStretch()
        
        main_layout.addLayout(button_layout)
        
        # Статус бар
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Готов к работе")
        
        # Статистика фильтрации
        self.filter_stats_label = QLabel()
        self.status_bar.addPermanentWidget(self.filter_stats_label)
    
    def create_menu(self):
        """Создает меню приложения"""
        menubar = self.menuBar()
        
        # Меню Файл
        file_menu = menubar.addMenu("Файл")
        
        select_action = QAction("📂 Выбрать файлы", self)
        select_action.triggered.connect(self.select_files)
        file_menu.addAction(select_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("🚪 Выход", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Меню Режим
        mode_menu = menubar.addMenu("Режим")
        
        abs_action = QAction("🎯 АБС (все игроки)", self)
        abs_action.triggered.connect(lambda: self.set_mode("abs"))
        mode_menu.addAction(abs_action)
        
        random_action = QAction("🎲 Случайные (только вы)", self)
        random_action.triggered.connect(lambda: self.set_mode("random"))
        mode_menu.addAction(random_action)
        
        # Меню Помощь
        help_menu = menubar.addMenu("Помощь")
        
        about_action = QAction("📌 О программе", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def apply_dark_theme(self):
        """Применяет темную тему через qdarkstyle"""
        try:
            # Пробуем разные варианты для разных версий qdarkstyle
            if hasattr(qdarkstyle, 'load_stylesheet_pyqt6'):
                self.setStyleSheet(qdarkstyle.load_stylesheet_pyqt6())
            elif hasattr(qdarkstyle, 'load_stylesheet'):
                self.setStyleSheet(qdarkstyle.load_stylesheet())
            else:
                # Если ничего не работает, просто игнорируем
                print("⚠️ Не удалось загрузить темную тему")
        except Exception as e:
            print(f"⚠️ Ошибка при загрузке темной темы: {e}")
    
    def set_mode(self, mode):
        """Устанавливает режим работы"""
        if mode == "abs":
            self.abs_radio.setChecked(True)
        else:
            self.random_radio.setChecked(True)
    
    def change_mode(self):
        """Обрабатывает изменение режима"""
        if self.abs_radio.isChecked():
            self.current_mode = "abs"
            self.status_bar.showMessage("Режим: АБС (все игроки)")
            # Показываем поиск и кнопку сброса
            self.search_input.show()
            self.reset_search_btn.show()
        else:
            self.current_mode = "random"
            self.status_bar.showMessage("Режим: Случайные (только вы)")
            # Скрываем поиск и кнопку сброса (в случайном режиме они не нужны)
            self.search_input.hide()
            self.reset_search_btn.hide()
        
        # Если уже есть данные, обновляем таблицу
        if self.current_mode == "abs" and self.abs_analyzer:
            self.display_abs_data()
        elif self.current_mode == "random" and self.random_analyzer:
            self.display_random_data()
    
    def display_abs_data(self):
        """Отображает данные АБС режима"""
        if not self.abs_analyzer:
            return
        
        headers, data, total_battles = self.abs_analyzer.get_table_data()
        self.current_abs_data = data.copy()
        self.total_battles = total_battles
        total_wins = self.abs_analyzer.total_wins
        
        win_percentage = (total_wins / total_battles * 100) if total_battles > 0 else 0
        
        # Подсчитываем статистику по кланам
        clan_stats = {'clan': 0, 'mixed': 0, 'none': 0}
        for battle in self.abs_analyzer.battles:
            clan_info = battle.get('clan_info', {})
            if not clan_info.get('clan') or clan_info.get('clan') == '?':
                clan_stats['none'] += 1
            elif clan_info.get('is_mixed'):
                clan_stats['mixed'] += 1
            else:
                clan_stats['clan'] += 1
        
        # Добавляем информацию о пропущенных боях и кланах
        info_text = (f"🎮 АБС боев: {total_battles}  |  🏆 Побед: {total_wins} ({win_percentage:.1f}%)  |  "
                    f"🏷️ Клановые: {clan_stats['clan']}  |  ⚔️ Сборные: {clan_stats['mixed']}")
        
        if self.abs_analyzer.skipped_battles > 0:
            info_text += f"  |  ⏭️ Пропущено: {self.abs_analyzer.skipped_battles}"
        
        self.info_label.setText(info_text)
        
        # Заполняем таблицу с новыми заголовками
        self.populate_table_abs(headers, data)
        self.reset_search_btn.setEnabled(True)
    
    def display_random_data(self):
        """Отображает данные случайного режима"""
        if not self.random_analyzer:
            return
        
        headers, data, total_battles, total_damage = self.random_analyzer.get_table_data()
        stats = self.random_analyzer.get_summary_stats()
        
        self.info_label.setText(
            f"👤 Игрок: {self.random_analyzer.player_name}  |  "
            f"🎮 Боёв: {total_battles}  |  "
            f"📊 Средний урон: {stats['avg_damage']}  |  "
            f"🏆 Побед: {stats['total_wins']} ({stats['win_rate']}%)"
        )
        
        self.populate_table_random(headers, data)

    def populate_table_random(self, headers, data):
        """Заполняет таблицу для случайного режима с подгонкой под заголовки"""
        self.table.clear()
        self.table.setRowCount(len(data))
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        
        # Отключаем сортировку временно
        self.table.setSortingEnabled(False)
        
        for row, row_data in enumerate(data):
            for col, value in enumerate(row_data):
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(row, col, item)
        
        # Сначала подгоняем все столбцы под содержимое
        self.table.resizeColumnsToContents()
        
        # Теперь настраиваем каждый столбец
        for col in range(len(headers)):
            # Получаем ширину по содержимому
            content_width = self.table.columnWidth(col)
            
            # Получаем ширину заголовка
            header_text = headers[col]
            # Примерная ширина текста (примерно 7 пикселей на символ)
            header_width = len(header_text) * 15
            
            # Берем максимальную ширину из содержимого и заголовка
            final_width = max(content_width, header_width)
            
            # Для последнего столбца (дата и карта) оставляем как есть
            if col == len(headers) - 1:
                # Не ограничиваем последний столбец
                self.table.setColumnWidth(col, final_width)
            else:
                # Для остальных столбцов ограничиваем до 150
                if final_width > 150:
                    self.table.setColumnWidth(col, 150)
                else:
                    self.table.setColumnWidth(col, final_width)
        
        # Включаем сортировку
        self.table.setSortingEnabled(True)        
    
    def populate_table_abs(self, headers, data):
        """Заполняет таблицу для АБС режима с отображением времени, карты, клана и результата"""
        self.table.clear()
        self.table.setRowCount(len(data))
        
        # Создаем новые заголовки (добавляем колонку с процентом выживания)
        new_headers = ['Игрок', 'Ср.урон', 'Боёв', '% Выживания']
        
        for i, battle in enumerate(self.abs_analyzer.battles):
            date_part = battle['date'][:16]
            map_part = battle['map']
            
            # Получаем информацию о клане
            clan_info = battle.get('clan_info', {})
            clan = clan_info.get('clan', '?')
            is_mixed = clan_info.get('is_mixed', False)
            
            # Формируем отображение клана
            if is_mixed:
                clan_display = f"⚔️ {clan}"
            else:
                clan_display = f"🏷️ {clan}"
            
            # Определяем результат боя
            # Нам нужно знать, победил ли владелец в этом бою
            # Для этого нужно найти ID владельца и его команду
            owner_name = None
            owner_team = None
            winner_team = None
            
            # Получаем имя владельца из первого боя (оно одинаковое для всех)
            if hasattr(self.abs_analyzer, 'battles') and len(self.abs_analyzer.battles) > 0:
                # Здесь нужно получить информацию о победителе из данных боя
                # Пока используем заглушку - будем брать из battle если есть
                pass
            
            # Эмодзи для результата
            is_win = battle.get('is_win', False)
            result_emoji = "🏆" if is_win else "💔"
            
            # Создаем заголовок из четырех строк
            header_text = f"{date_part}\n{map_part} - {result_emoji}\n{clan_display}"
            new_headers.append(header_text)
        
        self.table.setColumnCount(len(new_headers))
        self.table.setHorizontalHeaderLabels(new_headers)
        
        # Увеличиваем высоту заголовков для четырех строк
        self.table.horizontalHeader().setDefaultSectionSize(150)
        self.table.horizontalHeader().setMinimumHeight(100)  # Увеличили до 100
        
        # Отключаем сортировку временно
        self.table.setSortingEnabled(False)
        
        # Заполняем данные
        for row, row_data in enumerate(data):
            player_name = row_data[0]  # Имя игрока из первого столбца
            
            # Считаем количество выживаний для игрока
            total_battles = 0
            survived_battles = 0
            
            for battle in self.abs_analyzer.battles:
                battle_id = battle['id']
                if player_name in self.abs_analyzer.battle_data[battle_id]:
                    total_battles += 1
                    if hasattr(self.abs_analyzer, 'battle_health'):
                        health = self.abs_analyzer.battle_health.get(battle_id, {}).get(player_name, 0)
                        if health > 0:
                            survived_battles += 1
            
            # Рассчитываем процент выживания
            survival_rate = (survived_battles / total_battles * 100) if total_battles > 0 else 0
            
            for col, value in enumerate(row_data):
                if col == 0:  # Имя игрока
                    item = QTableWidgetItem(str(value))
                    item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
                    self.table.setItem(row, col, item)
                
                elif col == 1:  # Средний урон
                    item = QTableWidgetItem(str(value))
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.table.setItem(row, col, item)
                
                elif col == 2:  # Количество боев
                    item = QTableWidgetItem(str(value))
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.table.setItem(row, col, item)
                
                else:  # Столбцы с данными по боям (индекс 3 и дальше)
                    # В цикле заполнения данных для col >= 3:
                    # В цикле заполнения данных для col >= 3:
                    battle_index = col - 3
                    if battle_index < len(self.abs_analyzer.battles):
                        battle = self.abs_analyzer.battles[battle_index]
                        battle_id = battle['id']
                        
                        # Получаем здоровье, убийства игрока в этом бою
                        health = 0
                        kills = 0
                        
                        if hasattr(self.abs_analyzer, 'battle_health'):
                            health = self.abs_analyzer.battle_health.get(battle_id, {}).get(player_name, 0)
                        if hasattr(self.abs_analyzer, 'battle_kills'):
                            kills = self.abs_analyzer.battle_kills.get(battle_id, {}).get(player_name, 0)
                        
                        # Проверяем тип value (может быть словарем или строкой '-')
                        if value == '-':
                            display_text = '-'
                        else:
                            # Извлекаем танк и урон из словаря
                            tank = value.get('vehicle', '')
                            damage = value.get('damage', 0)
                            
                            
                            
                            # Первая строка: статус + танк
                            if health > 0:
                                status_emoji = "✅"
                            else:
                                status_emoji = "💀"
                            
                            line1 = f"{status_emoji} {tank}"
                            
                            # Вторая строка: урон и убийства
                            if kills > 0:
                                line2 = f"{damage} 🔪{kills}"
                            else:
                                line2 = str(damage)
                            
                            display_text = f"{line1}\n{line2}"
                        
                        item = QTableWidgetItem(display_text)
                        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                        
                        # Увеличиваем высоту строки для двухстрочного текста
                        current_height = self.table.rowHeight(row)
                        if current_height < 50:
                            self.table.setRowHeight(row, 50)
                        
                        # Добавляем тултип с полной информацией
                        if value != '-':
                            tooltip = f"Техника: {tank}\nУрон: {damage}\nЗдоровье: {health} HP\nУбийств: {kills}"
                            item.setToolTip(tooltip)
                        
                        self.table.setItem(row, col + 1, item)
        
        # Добавляем процент выживания в отдельную колонку (индекс 3)
        for row, row_data in enumerate(data):
            player_name = row_data[0]
            
            # Считаем количество выживаний для игрока
            total_battles = 0
            survived_battles = 0
            
            for battle in self.abs_analyzer.battles:
                battle_id = battle['id']
                if player_name in self.abs_analyzer.battle_data[battle_id]:
                    total_battles += 1
                    if hasattr(self.abs_analyzer, 'battle_health'):
                        health = self.abs_analyzer.battle_health.get(battle_id, {}).get(player_name, 0)
                        if health > 0:
                            survived_battles += 1
            
            # Рассчитываем процент выживания
            survival_rate = (survived_battles / total_battles * 100) if total_battles > 0 else 0
            
            # Форматируем отображение
            survival_text = f"{survival_rate:.1f}%"
            survival_item = QTableWidgetItem(survival_text)
            survival_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            
            # Добавляем цветовую индикацию
            if survival_rate >= 70:
                survival_item.setForeground(QColor("#4CAF50"))  # Зеленый для высокого выживания
            elif survival_rate >= 40:
                survival_item.setForeground(QColor("#FFC107"))  # Желтый для среднего
            else:
                survival_item.setForeground(QColor("#FF6B6B"))  # Красный для низкого
            
            # Добавляем тултип
            survival_item.setToolTip(f"Выжил в {survived_battles} из {total_battles} боев")
            
            self.table.setItem(row, 3, survival_item)
        
        # Подгоняем ширину столбцов
        self.table.resizeColumnsToContents()
        
        # Настраиваем ширину столбцов с данными боев
        for col in range(4, len(new_headers)):  # Начинаем с 4, потому что добавили колонку выживания
            current_width = self.table.columnWidth(col)
            if current_width < 120:
                self.table.setColumnWidth(col, 120)
            elif current_width > 250:
                self.table.setColumnWidth(col, 250)
        
        # Настраиваем первые четыре столбца
        self.table.resizeColumnToContents(0)  # Игрок
        if self.table.columnWidth(0) > 200:
            self.table.setColumnWidth(0, 200)
        
        self.table.setColumnWidth(1, 80)   # Ср.урон
        self.table.setColumnWidth(2, 60)   # Боёв
        self.table.setColumnWidth(3, 110)  # % Выживания
        
        # Включаем сортировку
        self.table.setSortingEnabled(True)
    
    def filter_table(self, text):
        """Фильтрует таблицу по тексту (только для АБС режима)"""
        if self.current_mode != "abs" or not self.abs_analyzer:
            return
        
        # Получаем текущие данные из таблицы (уже отсортированные)
        current_data = []
        for row in range(self.table.rowCount()):
            row_data = []
            for col in range(self.table.columnCount()):
                item = self.table.item(row, col)
                row_data.append(item.text() if item else "")
            current_data.append(row_data)
        
        # Фильтруем по имени игрока (первый столбец)
        for row, row_data in enumerate(current_data):
            if row_data:  # Проверяем, что данные есть
                match = text.lower() in row_data[0].lower()
                self.table.setRowHidden(row, not match)
        
        visible_rows = sum(1 for row in range(self.table.rowCount()) 
                        if not self.table.isRowHidden(row))
        self.filter_stats_label.setText(f"Показано: {visible_rows} из {self.table.rowCount()}")
    
    def reset_search(self):
        """Сбрасывает поиск (только для АБС режима)"""
        if self.current_mode != "abs":
            return
        
        self.search_input.clear()
        
        # Полностью перезаполняем таблицу исходными данными
        if self.current_abs_data is not None:
            # Нужно получить свежие заголовки из анализатора
            headers, _, _ = self.abs_analyzer.get_table_data()
            self.populate_table_abs(headers, self.current_abs_data)
        
        self.filter_stats_label.clear()
        self.status_bar.showMessage("🔄 Поиск сброшен")
    
    def select_files(self):
        """Выбирает файлы для анализа"""
        files = select_files_gui()
        
        if not files:
            return
        
        # Блокируем кнопку выбора во время анализа
        self.select_btn.setEnabled(False)
        self.select_btn.setText("⏳ Анализ...")
        self.status_bar.showMessage(f"Анализ {len(files)} файлов...")
        
        # Обновляем интерфейс, чтобы увидеть изменения
        QApplication.processEvents()
        
        try:
            if self.current_mode == "abs":
                # АБС режим
                self.abs_analyzer = BattleMatrixAnalyzer()
                
                if self.abs_analyzer.process_files(files):
                    # Добавляем информацию о кланах в заголовки
                    self.add_clan_info_to_headers(files)
                    
                    self.display_abs_data()
                    self.save_btn.setEnabled(True)
                    
                    # Показываем детальную статистику обработки
                    processed = self.abs_analyzer.processed_battles
                    skipped = self.abs_analyzer.skipped_battles
                    
                    if skipped > 0:
                        status_text = f"✅ АБС боев: {processed}  |  ⏭️ Пропущено случайных: {skipped}"
                        QMessageBox.information(
                            self, 
                            "Информация", 
                            f"Обработано АБС боев: {processed}\n"
                            f"Пропущено случайных боев (15×15): {skipped}\n\n"
                            f"Всего файлов: {len(files)}"
                        )
                    else:
                        status_text = f"✅ Анализ завершен. Обработано АБС боев: {processed}"
                    
                    self.status_bar.showMessage(status_text)
                else:
                    QMessageBox.warning(
                        self, 
                        "Ошибка", 
                        "Не удалось обработать файлы.\n\n"
                        "Возможные причины:\n"
                        "• Файлы не являются реплеями Мира танков\n"
                        "• Файлы повреждены\n"
                        "• Недостаточно прав для чтения файлов"
                    )
                    self.status_bar.showMessage("❌ Ошибка обработки")
            
            else:
                # Случайный режим
                self.random_analyzer = RandomBattleAnalyzer()
                
                if self.random_analyzer.process_files(files):
                    self.display_random_data()
                    self.save_btn.setEnabled(True)
                    
                    stats = self.random_analyzer.get_summary_stats()
                    status_text = (
                        f"✅ Анализ завершен. Боев: {stats['total_battles']} | "
                        f"Ср.урон: {stats['avg_damage']} | "
                        f"Побед: {stats['total_wins']} ({stats['win_rate']}%)"
                    )
                    self.status_bar.showMessage(status_text)
                else:
                    QMessageBox.warning(
                        self, 
                        "Ошибка", 
                        "Не удалось обработать файлы.\n\n"
                        "Возможные причины:\n"
                        "• Файлы не являются реплеями Мира танков\n"
                        "• Файлы повреждены\n"
                        "• Недостаточно прав для чтения файлов"
                    )
                    self.status_bar.showMessage("❌ Ошибка обработки")
        
        except Exception as e:
            # Обработка неожиданных ошибок
            QMessageBox.critical(
                self,
                "Критическая ошибка",
                f"Произошла непредвиденная ошибка:\n\n{str(e)}\n\n"
                "Пожалуйста, сообщите об этом разработчику."
            )
            self.status_bar.showMessage("❌ Критическая ошибка")
            print(f"❌ Ошибка: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            # В любом случае разблокируем кнопку
            self.select_btn.setEnabled(True)
            self.select_btn.setText("📂 Выбрать файлы")
            QApplication.processEvents()
    
    def add_clan_info_to_headers(self, files):
        """
        Добавляет информацию о кланах и результате в заголовки таблицы
        """
        if not self.abs_analyzer or not self.abs_analyzer.battles:
            return
        
        self.battle_clans = []
        files = sorted(files)       

        # Для каждого боя получаем клан соперника
        for i,battle in enumerate(self.abs_analyzer.battles):
           # print(f"Номер i :{i}")
           # print(f"battle :{battle}")
            if i < len(files):
                try:
                    file_path = files[i]
                    print(f"Обработка файла {i+1}: {os.path.basename(file_path)}")
            
                    clan_info = ClanExtractor.extract_opponent_clan_info(file_path)
                    clan_string = clan_info['clan_string']
                    is_mixed = clan_info.get('is_mixed', False)
                    
                    # Получаем результат боя из battle объекта
                    is_win = battle.get('is_win', False)
                    
                    # Сохраняем информацию о клане и результате
                    battle_info = {
                        'clan': clan_string,
                        'is_mixed': is_mixed,
                        'is_win': is_win,
                        'full_info': clan_info
                    }
                    self.battle_clans.append(battle_info)
                    battle['clan_info'] = battle_info
                    
                    # Выводим в консоль для отладки
                    icon = "⚔️" if is_mixed else "🏷️"
                    result_icon = "🏆" if is_win else "💔"
                    print(f"  {icon} {result_icon} Бой {i+1}: {clan_string}")
                    
                except Exception as e:
                    print(f"Ошибка получения клана для боя {i}: {e}")
                    battle_info = {
                        'clan': '?',
                        'is_mixed': False,
                        'is_win': False,
                        'full_info': {}
                    }
                    self.battle_clans.append(battle_info)
                    battle['clan_info'] = battle_info
    
    def save_csv(self):
        """Сохраняет данные в CSV"""
        analyzer = self.abs_analyzer if self.current_mode == "abs" else self.random_analyzer
        
        if not analyzer:
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Сохранить CSV файл",
            f"battle_{self.current_mode}_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            "CSV files (*.csv);;All files (*.*)"
        )
        
        if file_path:
            if analyzer.export_to_csv(file_path):
                QMessageBox.information(self, "Готово", f"Файл успешно сохранен:\n{file_path}")
                self.status_bar.showMessage(f"✅ Файл сохранен: {file_path}")
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось сохранить файл")
    
    def show_about(self):
        """Показывает окно 'О программе'"""
        QMessageBox.about(
            self,
            "О программе",
            "<h2>🎮 MirTankov ABS Replay Analyzer</h2>"
            "<p><b>Версия:</b> 3.0.0</p>"
            "<p><b>Авторы:</b></p>"
            "<ul>"
            "<li>AleXNocS – Developer</li>"
            "<li>Sk0p1 (aka panda_rez) – Inspiration + Motivation & Tester</li>"
            "</ul>"
            "<p><b>Описание:</b></p>"
            "<p>Инструмент для анализа реплеев Мира танков (.mtreplay)</p>"
            "<p><b>Два режима работы:</b></p>"
            "<ul>"
            "<li><b>АБС:</b> Показывает статистику всех игроков</li>"
            "<li><b>Случайные:</b> Показывает детальную статистику владельца реплеев:<br>"
            "урон, фраги, засвет, выстрелы, попадания, пробития, точность, опыт, заблокировано</li>"
            "</ul>"
            "<p><b>Лицензия:</b> MIT</p>"
        )