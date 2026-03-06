import re
import json
from pathlib import Path

def parse_all_short_names(po_files_dir):
    """
    Парсит все .po файлы в директории и собирает короткие названия танков
    Ищет строки вида:
    msgid "R45_IS-7_short"
    msgstr "ИС-7"
    """
    all_short_names = {}
    po_files = Path(po_files_dir).glob("*.po")
    
    for po_file in po_files:
        print(f"Обработка {po_file.name}...")
        
        with open(po_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Регулярное выражение для поиска пар msgid/msgstr с _short
        # Учитываем, что msgstr может быть многострочным
        pattern = r'msgid "([A-Za-z0-9_]+_short)"\nmsgstr "([^"]*)"'
        matches = re.findall(pattern, content)
        
        count = 0
        for msgid, short_name in matches:
            # Извлекаем идентификатор танка (убираем _short)
            tank_id = msgid.replace('_short', '')
            if short_name and short_name != "?empty?":
                all_short_names[tank_id] = short_name
                count += 1
        
        print(f"  Найдено {count} коротких названий")
    
    return all_short_names

# Укажите путь к папке с .po файлами
po_dir = Path("vehicles")
short_names = parse_all_short_names(po_dir)

print(f"\n✅ Всего найдено коротких названий: {len(short_names)}")

# Сохраняем в JSON для использования в проекте
with open('tank_short_names.json', 'w', encoding='utf-8') as f:
    json.dump(short_names, f, ensure_ascii=False, indent=2)

print(f"\n✅ Сохранено в tank_short_names.json")

# Покажем несколько примеров
print("\n📋 Примеры:")
examples = [
    "R45_IS-7",
    "F108_Panhard_EBR_105",
    "GB98_T95_FV4201_Chieftain",
    "R231_Object_278",
    "Ch22_113"
]

for tank_id in examples:
    short = short_names.get(tank_id, "НЕ НАЙДЕНО")
    print(f"  {tank_id} -> {short}")