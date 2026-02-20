# import polib
# import os

# def extract_vehicle_names_from_mo(mo_file_path):
#     """
#     Извлекает названия танков из .mo файла локализации
#     """
#     mo = polib.mofile(mo_file_path)
#     vehicles = {}
    
#     for entry in mo:
#         # В .mo файлах ключи и значения хранятся в специальном формате
#         msgid = entry.msgid
#         msgstr = entry.msgstr
        
#         # Фильтруем только записи, относящиеся к танкам
#         if 'vehicle' in msgid.lower() or 'tank' in msgid.lower():
#             vehicles[msgid] = msgstr
    
#     return vehicles

# # Пример использования для разных наций
# nations = ['ru', 'en', 'de', 'fr']  # и т.д.
# all_vehicles = {}

# mo_path = "N:\wot\Tanki\res\text\ru\lc_messages\nations.mo"
# nations_mo = polib.mofile(mo_path)
# print(nations_mo)
# # for nation in nations:
# #     mo_path = f"path/to/World_of_Tanks/res/text/LC_MESSAGES/vehicles.{nation}.mo"
# #     if os.path.exists(mo_path):
# #         vehicles = extract_vehicle_names_from_mo(mo_path)
# #         all_vehicles[nation] = vehicles
# #         print(f"Найдено {len(vehicles)} записей для {nation}")

# import polib
# import os

# def extract_nations_from_mo(mo_file_path):
#     """
#     Извлекает названия наций из .mo файла локализации
#     """
#     try:
#         # Загружаем .mo файл
#         mo = polib.mofile(mo_file_path)
#     except Exception as e:
#         print(f"Ошибка при загрузке {mo_file_path}: {e}")
#         return {}
    
#     nations = {}
    
#     for entry in mo:
#         msgid = entry.msgid
#         msgstr = entry.msgstr
        
#         # В nations.mo ключи обычно выглядят как названия наций
#         # Например: "ussr", "germany", "usa" и т.д.
#         if msgid and msgstr and not msgid.startswith('#'):
#             nations[msgid] = msgstr
    
#     return nations

# # Путь к файлу nations.mo
# mo_path = r"N:\wot\Tanki\res\text\ru\lc_messages\nations.mo"

# # Проверяем существование файла
# if os.path.exists(mo_path):
#     print(f"Файл найден: {mo_path}")
    
#     # Извлекаем названия наций
#     nations = extract_nations_from_mo(mo_path)
    
#     # Выводим результаты
#     print(f"\nНайдено наций: {len(nations)}")
#     print("\nНазвания наций:")
#     for key, value in nations.items():
#         print(f"  {key} -> {value}")
        
#     # Покажем также первые несколько записей для понимания структуры
#     print("\nПервые 10 записей в файле:")
#     mo = polib.mofile(mo_path)
#     for i, entry in enumerate(mo[:10]):
#         print(f"{i+1}. msgid: {entry.msgid}")
#         print(f"   msgstr: {entry.msgstr}")
#         print(f"   комментарий: {entry.comment}")
#         print("-" * 40)
        
# else:
#     print(f"Файл не найден по пути: {mo_path}")
    
#     # Попробуем найти файл в других возможных местах
#     print("\nПоиск nations.mo в других директориях:")
#     base_path = r"N:\wot\Tanki\res\text"
    
#     for root, dirs, files in os.walk(base_path):
#         if "nations.mo" in files:
#             found_path = os.path.join(root, "nations.mo")
#             print(f"Найден: {found_path}")
            
#             # Загружаем найденный файл
#             nations = extract_nations_from_mo(found_path)
#             print(f"\nНайдено наций: {len(nations)}")
#             for key, value in list(nations.items())[:5]:  # Покажем первые 5
#                 print(f"  {key} -> {value}")
#             break


#   china -> Китай
#   czech -> Чехословакия
#   france -> Франция
#   germany -> Германия
#   intunion -> Сборная наций
#   italy -> Италия
#   japan -> Япония
#   poland -> Польша
#   sweden -> Швеция
#   uk -> Великобритания
#   usa -> США
#   ussr -> СССР

import polib
import os
from collections import defaultdict

# Словарь наций (как в вашем списке)
nations = {
  #  'china': 'Китай',
  #  'czech': 'Чехословакия',
  #  'france': 'Франция',
  #  'germany': 'Германия',
  #  'intunion': 'Сборная наций',
  #  'italy': 'Италия',
  #  'japan': 'Япония',
  #  'poland': 'Польша',
  #  'sweden': 'Швеция',
    'gb': 'Великобритания',
  #  'usa': 'США',
  #  'ussr': 'СССР'
}

def extract_vehicles_from_mo(mo_file_path, nation_name):
    """
    Извлекает названия танков из .mo файла локализации для конкретной нации
    """
    try:
        mo = polib.mofile(mo_file_path)
    except Exception as e:
        print(f"  Ошибка при загрузке {mo_file_path}: {e}")
        return {}
    
    vehicles = {}
    
    for entry in mo:
        msgid = entry.msgid
        msgstr = entry.msgstr
        
        # Пропускаем пустые записи
        if not msgid or not msgstr:
            continue
        
        # Сохраняем все записи, но фильтруем только те, которые похожи на названия танков
        # Обычно в таких файлах ключи содержат идентификаторы танков, а значения - их названия
        vehicles[msgid] = msgstr
    
    return vehicles

def find_nation_vehicle_files(base_path):
    """
    Ищет файлы вида {нация}_vehicles.mo для всех наций
    """
    nation_files = {}
    
    for nation_code in nations.keys():
        # Ищем файл с названием {нация}_vehicles.mo
        target_file = f"{nation_code}_vehicles.mo"
        
        for root, dirs, files in os.walk(base_path):
            if target_file in files:
                file_path = os.path.join(root, target_file)
                nation_files[nation_code] = file_path
                print(f"  Найден файл для {nations[nation_code]}: {file_path}")
                break
    
    return nation_files

def analyze_vehicle_names(vehicles_dict):
    """
    Анализирует структуру названий танков
    """
    if not vehicles_dict:
        return
    
    print(f"\n  Всего записей: {len(vehicles_dict)}")
    
    # Покажем несколько примеров
    print("  Примеры записей:")
    for i, (key, value) in enumerate(list(vehicles_dict.items())[:10]):
        print(f"    {i+1}. {key} -> {value}")
    
    # Анализ структуры ключей
    key_patterns = defaultdict(int)
    for key in vehicles_dict.keys():
        if ':' in key:
            parts = key.split(':')
            if len(parts) > 1:
                pattern = f"{parts[0]}:..."
                key_patterns[pattern] += 1
        elif '/' in key:
            parts = key.split('/')
            if len(parts) > 1:
                pattern = f"{parts[0]}/..."
                key_patterns[pattern] += 1
        else:
            key_patterns['other'] += 1
    
    print("  Структура ключей:")
    for pattern, count in key_patterns.items():
        print(f"    {pattern}: {count} записей")

# Основной путь к файлам локализации
base_path = r"N:\wot\Tanki\res\text"

# Словарь для хранения всех танков по нациям
all_vehicles_by_nation = {}

print("Поиск файлов с названиями танков...")
print("-" * 50)

# Ищем файлы для каждой нации
nation_files = find_nation_vehicle_files(base_path)

print("\n" + "="*50)
print("Анализ файлов с названиями танков:")
print("="*50)

# Обрабатываем каждый найденный файл
for nation_code, file_path in nation_files.items():
    nation_name = nations.get(nation_code, nation_code)
    print(f"\n--- {nation_name} ({nation_code}) ---")
    
    vehicles = extract_vehicles_from_mo(file_path, nation_name)
    all_vehicles_by_nation[nation_code] = vehicles
    
    analyze_vehicle_names(vehicles)

# Если файлы не найдены, попробуем другой подход - поиск всех .mo файлов,
# которые могут содержать названия танков
if not nation_files:
    print("\nФайлы вида {нация}_vehicles.mo не найдены.")
    print("Поиск альтернативных файлов с названиями танков...")
    
    all_mo_files = []
    for root, dirs, files in os.walk(base_path):
        for file in files:
            if file.endswith('.mo') and 'vehicle' in file.lower():
                all_mo_files.append(os.path.join(root, file))
    
    if all_mo_files:
        print(f"\nНайдено {len(all_mo_files)} .mo файлов, содержащих 'vehicle' в названии:")
        for mo_file in all_mo_files[:20]:  # Покажем первые 20
            print(f"  {mo_file}")
            
            # Попробуем определить, к какой нации относится файл
            for nation_code in nations.keys():
                if nation_code in mo_file.lower():
                    print(f"    → Возможно, относится к нации {nations[nation_code]}")
                    break
    else:
        print(".mo файлы с 'vehicle' в названии не найдены")
        
        # Поиск всех .mo файлов в директории lc_messages
        print("\nПоиск всех .mo файлов в директориях lc_messages:")
        for root, dirs, files in os.walk(base_path):
            if 'lc_messages' in root:
                for file in files:
                    if file.endswith('.mo'):
                        print(f"  {os.path.join(root, file)}")

# Сохраняем результаты в файл для дальнейшего использования
if all_vehicles_by_nation:
    output_file = "wot_vehicles_list.txt"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("Список танков World of Tanks по нациям\n")
        f.write("="*50 + "\n\n")
        
        for nation_code, vehicles in all_vehicles_by_nation.items():
            nation_name = nations.get(nation_code, nation_code)
            f.write(f"\n{nation_name} ({nation_code}):\n")
            f.write("-" * 30 + "\n")
            
            for key, value in vehicles.items():
                f.write(f"  {key}: {value}\n")
    
    print(f"\nРезультаты сохранены в файл: {output_file}")

# Вывод статистики
print("\n" + "="*50)
print("СТАТИСТИКА:")
print("="*50)
total_vehicles = 0
for nation_code, vehicles in all_vehicles_by_nation.items():
    nation_name = nations.get(nation_code, nation_code)
    count = len(vehicles)
    total_vehicles += count
    print(f"{nation_name}: {count} записей")

print(f"\nВСЕГО: {total_vehicles} записей")
