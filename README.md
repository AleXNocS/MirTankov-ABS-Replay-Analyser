# 🎮 MirTankov ABS Replay Analyzer

**Created by / Создано:**
- **AleXNocS** – *Developer*
- **Sk0p1 (aka panda_rez)** – *Inspiration + Motivation & Tester*

---

## 📦 Быстрый старт / Quick Start

### 🏃 **Для пользователей / For users**

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
---

## 🐍 **Для разработчиков / For developers**

### English
If you want to run from source code or modify the tool:

```bash
# Clone the repository
git clone https://github.com/AleXNocS/MirTankov-ABS-Replay-Analyzer.git
cd MirTankov-ABS-Replay-Analyzer

# Run the script
python gui_0_2_replay_analyze.py

# Create your own executable (optional)
pip install pyinstaller
python -m PyInstaller --onefile --windowed --name "MirTankov_ABS_Analyzer" gui_0_2_replay_analyze.py
