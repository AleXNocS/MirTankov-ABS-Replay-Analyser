# 🎮 MirTankov ABS Replay Analyzer

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Platform](https://img.shields.io/badge/platform-windows-lightgrey.svg)](https://www.microsoft.com/windows)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Version](https://img.shields.io/github/v/release/AleXNocS/MirTankov-ABS-Replay-Analyser)](https://github.com/AleXNocS/MirTankov-ABS-Replay-Analyser/releases/latest)
[![Downloads](https://img.shields.io/github/downloads/AleXNocS/MirTankov-ABS-Replay-Analyser/total.svg)](https://github.com/AleXNocS/MirTankov-ABS-Replay-Analyser/releases)

### 👥 Авторы / Authors
[AleXNocS](https://github.com/AleXNocS) – something like developer  
Sk0p1 (aka panda_rez) – Inspiration+Motivation 😎 & Tester

---
## 🌟 Возможности / Features

### Русский / English
- **Прямой парсинг .mtreplay** – без промежуточных файлов / Direct .mtreplay parsing – no intermediate files needed
- **Выбор нескольких файлов** через стандартный диалог Windows / Multiple file selection via native Windows file dialog
- **Интерактивная таблица** с прокруткой / Interactive data table with scrollable view
- **Матрица статистики игроков** / Player statistics matrix:
  - Средний урон каждого игрока / Average damage per player
  - Общее количество боёв / Total battles count
  - Общий процент побед / Overall win percentage
  - Урон за каждый бой ('-' если игрока не было в бою, '0' если был без урона) / Damage per battle (with '-' for missed battles, '0' for zero damage)
- **Экспорт в CSV** для анализа в Excel / Export to CSV for further analysis in Excel
- **Чистый интерфейс** с понятным управлением / Clean GUI with intuitive controls
- **Модульная архитектура** – легко поддерживать и расширять / Modular architecture – easy to maintain and extend
- **Готовый `.exe` файл** – не требует установки Python / Standalone .exe available – no Python installation required
---
## 📦 Быстрый старт / Quick Start

### 🏃 **Для пользователей / For users**

#### Русский
1. **Скачайте готовую программу:**
   - Перейдите на страницу [Releases](https://github.com/AleXNocS/MirTankov-ABS-Replay-Analyser/releases)
   - Скачайте `MirTankov_ABS_Analyzer.exe`
   - Запустите файл – **Python не требуется!**

2. **Как использовать:**
   - Запустите `.exe` файл
   - Укажите ваши `.mtreplay` файлы
   - Просмотрите результаты в таблице
   - Нажмите "Сохранить в CSV" для экспорта данных

#### English
1. **Download the ready-to-use executable:**
   - Go to [Releases](https://github.com/AleXNocS/MirTankov-ABS-Replay-Analyser/releases) page
   - Download `MirTankov_ABS_Analyzer.exe`
   - Run it directly – **no Python installation required!**

2. **How to use:**
   - Launch the `.exe` file 
   - Choose your `.mtreplay` files
   - View results in the table
   - Click "Сохранить в CSV" (Save to CSV) to export data

---

## 🐍 **Для разработчиков / For developers**

### English

If you want to run from source code or modify the tool:

#### Clone the repository
```bash
git clone https://github.com/AleXNocS/MirTankov-ABS-Replay-Analyser.git
cd MirTankov-ABS-Replay-Analyser
```
### Project Structure OUTDATED
```bash
MirTankov-ABS-Replay-Analyser/
│
├── main.py                 # Entry point
├── models/
│   ├── __init__.py
│   └── analyzer.py         # BattleMatrixAnalyzer class
├── gui/
│   ├── __init__.py
│   └── viewer.py           # TableViewer class
├── utils/
│   ├── __init__.py
│   └── file_dialog.py      # File selection dialog
└── requirements.txt        # Dependencies (empty - uses only standard library)
```
Run from source
```bash
python main.py
```
Create your own executable
```bash
# Install pyinstaller
pip install pyinstaller

# Build executable with icon
python -m PyInstaller --onefile --windowed --icon=icon.ico --name "MirTankov_ABS_Analyzer" main.py

# The .exe file will be in the 'dist' folder
```
Русский
Если вы хотите запустить из исходного кода или модифицировать инструмент:

Клонируйте репозиторий
```bash
git clone https://github.com/AleXNocS/MirTankov-ABS-Replay-Analyser.git
cd MirTankov-ABS-Replay-Analyser
```
Структура проекта
```bash
MirTankov-ABS-Replay-Analyser/
│
├── main.py                 # Точка входа
├── models/
│   ├── __init__.py
│   └── analyzer.py         # Класс BattleMatrixAnalyzer
├── gui/
│   ├── __init__.py
│   └── viewer.py           # Класс TableViewer
├── utils/
│   ├── __init__.py
│   └── file_dialog.py      # Диалог выбора файлов
└── requirements.txt        # Зависимости (пусто - только стандартная библиотека)
```
Запуск из исходного кода
```bash
python main.py
```
Создание исполняемого файла
```bash
# Установите pyinstaller
pip install pyinstaller

# Соберите .exe с иконкой
python -m PyInstaller --onefile --windowed --icon=icon.ico --name "MirTankov_ABS_Analyzer" main.py
# Готовый .exe файл появится в папке 'dist'
```
---

### 📁 Формат вывода / Output format
CSV Structure / Структура CSV
```text
Игрок	Ср.урон	Боёв	19.02.2026 20:55 Жемчужная река	19.02.2026 21:10 Химмельсдорф	...
Player1	2500	10	                2800	                   3200	                  ...
Player2	1800	8	                   -                       1950	                  ...
```
### 🛠️ Требования / Requirements
**For .exe version / Для .exe версии**  
Windows 7/8/10/11  
No Python required – just download and run!  

**For source code / Для исходного кода**  
Python 3.8+  
Windows OS (for .mtreplay files and native file dialog)  
No additional packages needed – all dependencies are in standard library  

---

### 📝 Примечания / Notes

This tool is designed for Lesta Games version of World of Tanks (.mtreplay files)
All processing is done locally – no data is sent anywhere
The .exe version is completely standalone and portable


Инструмент предназначен для версии Lesta Games Мира танков (файлы .mtreplay)
Вся обработка происходит локально – данные никуда не отправляются
.exe версия полностью автономна и портативна



---
## 🤝 Участие в разработке / Contributing
### Contributions are welcome! Feel free to:  
- Report bugs
- Suggest new features
- Submit pull requests  
### Приветствуется любой вклад! Вы можете:  
- Сообщать об ошибках
- Предлагать новые функции
- Отправлять pull request'ы
---
### 📄 Лицензия / License
This project is licensed under the MIT License – see the LICENSE file for details.
Этот проект лицензирован под MIT License – подробности в файле LICENSE.
---
### 🙏 Благодарности / Acknowledgements
Thanks to the World of Tanks/Mir Tankov community  
Inspired by various replay parsing tools  
Спасибо сообществу Мира танков  
Вдохновлено различными инструментами для парсинга реплеев  
**Отдельно спасибо владельцу сайта wn8.pro который вырезал RU регион без указания причины.**
### 🚀 Скачивайте и анализируйте свои бои!
### 🚀 Download now and analyze your battles!
