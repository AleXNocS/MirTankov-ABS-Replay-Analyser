# 🎮 MirTankov ABS Replay Analyzer

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-windows-lightgrey.svg)](https://www.microsoft.com/windows)
[![Version](https://img.shields.io/badge/version-1.0.0-orange.svg)]()
[![Downloads](https://img.shields.io/github/downloads/AleXNocS/MirTankov-ABS-Replay-Analyzer/total.svg)]()

**Created by / Создано:**
- **AleXNocS** – *Lead Developer*
- **Sk0p1 (aka panda_rez)** – *Co-Developer & Tester*

---

## 📦 Быстрый старт / Quick Start

### 🏃 **Для пользователей / For users**

#### English
1. **Download the ready-to-use executable:**
   - Go to [Releases](https://github.com/AleXNocS/MirTankov-ABS-Replay-Analyser/releases) page
   - Download `MirTankov_ABS_Analyzer.exe`
   - Run it directly – **no Python installation required!**

2. **How to use:**
   - Launch the `.exe` file
   - Click "Выбрать файлы" (Select Files)
   - Choose your `.mtreplay` files
   - View results in the table
   - Click "Сохранить в CSV" (Save to CSV) to export data

#### Русский
1. **Скачайте готовую программу:**
   - Перейдите на страницу [Releases](https://github.com/AleXNocS/MirTankov-ABS-Replay-Analyzer/releases)
   - Скачайте `MirTankov_ABS_Analyzer.exe`
   - Запустите файл – **Python не требуется!**

2. **Как использовать:**
   - Запустите `.exe` файл
   - Нажмите "Выбрать файлы"
   - Укажите ваши `.mtreplay` файлы
   - Просмотрите результаты в таблице
   - Нажмите "Сохранить в CSV" для экспорта данных

---

## 🐍 **Для разработчиков / For developers**

### English
If you want to run from source code or modify the tool:

```bash
# Clone the repository
git clone https://github.com/AleXNocS/MirTankov-ABS-Replay-Analyzer.git
cd MirTankov-ABS-Replay-Analyzer

# Run the script
python replay_analyzer.py

# Create your own executable (optional)
pip install pyinstaller
python -m PyInstaller --onefile --windowed --name "MirTankov_ABS_Analyzer" replay_analyzer.py
