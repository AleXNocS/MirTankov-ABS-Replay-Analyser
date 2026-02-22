import sys
import os
import ctypes
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from gui.main_window import MainWindow

def setup_taskbar_icon():
    """Критически важно: вызывать ДО создания QApplication"""
    if sys.platform == "win32":
        try:
            # Уникальный идентификатор для вашего приложения
            # Формат: Компания.Продукт.Версия
            myappid = 'AleXNocS.MirTankovABSReplayAnalyzer.2.0.0'
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
            print(f"✅ AppUserModelID установлен: {myappid}")
        except Exception as e:
            print(f"❌ Ошибка установки AppUserModelID: {e}")

def get_icon_path():
    """Возвращает путь к иконке"""
    if getattr(sys, 'frozen', False):
        application_path = sys._MEIPASS
        print(f"📦 Запущено из .exe, путь: {application_path}")
    else:
        application_path = os.path.dirname(os.path.abspath(__file__))
        print(f"🐍 Запущено из скрипта, путь: {application_path}")
    
    icon_path = os.path.join(application_path, 'icon.ico')
    if os.path.exists(icon_path):
        print(f"✅ Иконка найдена: {icon_path}")
    else:
        print(f"❌ Иконка НЕ найдена: {icon_path}")
    
    return icon_path if os.path.exists(icon_path) else None

def main():
    # 1. СНАЧАЛА устанавливаем AppUserModelID (это критически важно!)
    setup_taskbar_icon()
    
    # 2. ПОТОМ создаем QApplication
    app = QApplication(sys.argv)
    app.setApplicationName("MirTankov ABS Replay Analyzer")
    app.setApplicationVersion("2.0.0")
    
    # 3. Устанавливаем иконку для приложения
    icon_path = get_icon_path()
    if icon_path:
        app_icon = QIcon(icon_path)
        app.setWindowIcon(app_icon)
        print("✅ Иконка установлена для приложения")
    
    # 4. Создаем и показываем окно
    window = MainWindow()
    
    # 5. ДОПОЛНИТЕЛЬНО устанавливаем иконку для окна
    if icon_path:
        window.setWindowIcon(QIcon(icon_path))
        print("✅ Иконка установлена для окна")
    
    window.show()
    print("✅ Приложение запущено")
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()