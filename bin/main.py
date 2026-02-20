import sys
from models.analyzer import BattleMatrixAnalyzer
from gui.viewer import TableViewer
from utils.file_dialog import select_files_gui

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
        
        # Показываем таблицу с процентом побед
        print("\n📊 Открывается окно с таблицей результатов...")
        viewer = TableViewer(headers, data, total_battles, analyzer.total_wins)
        viewer.run()
        
        print("\n✅ Работа завершена")
    else:
        print("\n❌ Не удалось обработать файлы")
    
   # input("\nНажмите Enter для выхода...")

if __name__ == "__main__":
    main()