import json
from pathlib import Path
from models.analyzer import BattleMatrixAnalyzer

analyzer = BattleMatrixAnalyzer()
replay_path = "20260305_2128_china-Ch22_113_44_north_america.mtreplay"

print(f"\n📁 Анализ файла: {replay_path}")
print("="*60)

metadata, results = analyzer.extract_json_from_replay(replay_path)

if not metadata or not results:
    print("❌ Не удалось извлечь данные")
else:
    # Получаем vehicles из metadata
    vehicles_meta = metadata.get('vehicles', {})
    
    # Получаем статистику из results
    vehicles_stats = results.get('vehicles', {})
    
    print("\n📊 Реальное состояние игроков (по health):")
    print("-" * 60)
    
    for vid, v in vehicles_meta.items():
        if not isinstance(v, dict):
            continue
        
        player_name = v.get('name', 'Unknown')
        team = v.get('team', '?')
        
        # Получаем здоровье из results
        stats = vehicles_stats.get(vid, [{}])[0]
        health = stats.get('health', 0)
        
        # Определяем статус по здоровью
        status = "💀 ПОГИБ" if health <= 0 else f"✅ ВЫЖИЛ ({health} HP)"
        
        print(f"  {player_name:<20} | Команда {team} | {status}")
    
    print("-" * 60)
    
    # Подсчет статистики
    total = 0
    dead = 0
    alive = 0
    
    for vid, v in vehicles_meta.items():
        if not isinstance(v, dict):
            continue
        
        total += 1
        stats = vehicles_stats.get(vid, [{}])[0]
        health = stats.get('health', 0)
        
        if health <= 0:
            dead += 1
        else:
            alive += 1
    
    print(f"\n📈 Статистика по результатам боя:")
    print(f"  Всего игроков: {total}")
    print(f"  Выжило: {alive}")
    print(f"  Погибло: {dead}")