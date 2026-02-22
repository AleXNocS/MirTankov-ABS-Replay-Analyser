import json
import csv
from pathlib import Path
from collections import defaultdict
from .tank_lib import tank_names

class RandomBattleAnalyzer:
    """
    Анализатор для случайных боев.
    Показывает статистику только владельца реплея.
    Добавляет информацию о выстрелах/попаданиях/пробитиях.
    """
    
    def __init__(self):
        self.player_name = None
        self.player_stats = []  # Статистика по боям для игрока
        self.battles = []       # Информация о боях
        self.total_wins = 0
        self.tank_names = tank_names
        
    def get_vehicle_name(self, vehicle_full):
        """Возвращает игровое название танка"""
        if ':' in vehicle_full:
            vehicle_key = vehicle_full.split(':', 1)[1]
        else:
            vehicle_key = vehicle_full
        
        if vehicle_key in self.tank_names:
            return self.tank_names[vehicle_key]
        
        if ':' in vehicle_full:
            vehicle_full = vehicle_full.split(':', 1)[1]
        vehicle_full = vehicle_full.replace('_', ' ')
        return vehicle_full.strip()
    
    def extract_json_from_replay(self, replay_path):
        """Извлекает metadata и results из .mtreplay файла"""
        try:
            with open(replay_path, 'rb') as f:
                data = f.read()
        except Exception as e:
            print(f"  ❌ Ошибка чтения файла: {e}")
            return None, None
        
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
        """Обрабатывает один реплей и собирает статистику владельца"""
        print(f"\n📁 Обработка: {Path(replay_path).name}")
        
        metadata, results = self.extract_json_from_replay(replay_path)
        
        if not metadata or not results:
            print("  ⚠️ Не удалось извлечь данные, пропускаем")
            return False
        
        # Получаем информацию о бое
        map_name = metadata.get('mapDisplayName', 'Неизвестно')
        date_time = metadata.get('dateTime', 'Неизвестно')
        player_name = metadata.get('playerName', '')
        
        # Сохраняем имя игрока (оно одинаковое для всех реплеев)
        if not self.player_name:
            self.player_name = player_name
        
        # Создаем ID для боя
        battle_id = f"{date_time}_{map_name}"
        
        # Добавляем бой в список
        self.battles.append({
            'id': battle_id,
            'date': date_time,
            'map': map_name,
            'file': Path(replay_path).name
        })
        
        # Находим статистику игрока
        vehicles_meta = metadata.get('vehicles', {})
        vehicles_stats = results.get('vehicles', {})
        
        player_found = False
        player_data = None
        
        for vid, v in vehicles_meta.items():
            if not isinstance(v, dict):
                continue
            
            if v.get('name') == player_name:
                player_found = True
                stats = vehicles_stats.get(vid, [{}])[0]
                
                # Получаем название танка
                vehicle_full = v.get('vehicleType', 'Unknown')
                vehicle = self.get_vehicle_name(vehicle_full)
                
                # Собираем всю статистику
                player_data = {
                    'battle_id': battle_id,
                    'date': date_time,
                    'map': map_name,
                    'vehicle': vehicle,
                    'damage': stats.get('damageDealt', 0),
                    'kills': stats.get('kills', 0),
                    'spotted': stats.get('spotted', 0),
                    'shots': stats.get('shots', 0),
                    'hits': stats.get('directHits', 0),
                    'piercings': stats.get('piercings', 0),
                    'xp': stats.get('xp', 0),
                    'damage_blocked': stats.get('damageBlockedByArmor', 0),
                    'damage_received': stats.get('damageReceived', 0)
                }
                
                # Рассчитываем точность
                if player_data['shots'] > 0:
                    player_data['accuracy'] = (player_data['hits'] / player_data['shots']) * 100
                else:
                    player_data['accuracy'] = 0
                
                # Добавляем в общую статистику
                self.player_stats.append(player_data)
                break
        
        if not player_found:
            print(f"  ⚠️ Не найден игрок {player_name} в реплее")
            return False
        
        # Определяем исход боя
        winner_team = results.get('common', {}).get('winnerTeam', 0)
        player_team = None
        
        for vid, v in vehicles_meta.items():
            if isinstance(v, dict) and v.get('name') == player_name:
                player_team = v.get('team', 0)
                break
        
        if player_team and winner_team == player_team:
            self.total_wins += 1
            outcome = "🏆 ПОБЕДА"
        else:
            outcome = "❌ ПОРАЖЕНИЕ"
        
        print(f"  {outcome} на карте {map_name}")
        print(f"     Урон: {player_data['damage']} | Фраги: {player_data['kills']} | "
              f"Выстрелы: {player_data['shots']} | Попадания: {player_data['hits']} | "
              f"Пробития: {player_data['piercings']} | Блок: {player_data['damage_blocked']}")
        
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
        print(f"👤 Игрок: {self.player_name}")
        print(f"{'='*80}")
        
        return processed > 0
    
    def get_table_data(self):
        """Возвращает данные для таблицы в формате для случайных боев"""
        if not self.player_stats:
            return [], [], 0
        
        # Сортируем бои по дате
        self.player_stats.sort(key=lambda x: x['date'])
        
        # Формируем заголовки
        headers = [
            'Танк', 'Урон', 'Фраги', 'Засвет',
            'Выстрелы', 'Попадания', 'Пробития', 'Точность %',
            'Опыт', 'Заблокировано', 'Дата и карта'
        ]
        
        # Создаем данные
        data = []
        total_damage = 0
        
        for battle in self.player_stats:
            # Форматируем точность
            accuracy = f"{battle['accuracy']:.1f}"
            
            # Форматируем дату и карту
            date_map = f"{battle['date'][:16]} {battle['map']}"
            
            row = [
                battle['vehicle'],
                battle['damage'],
                battle['kills'],
                battle['spotted'],
                battle['shots'],
                battle['hits'],
                battle['piercings'],
                accuracy,
                battle['xp'],
                battle['damage_blocked'],
                date_map
            ]
            data.append(row)
            total_damage += battle['damage']
        
        return headers, data, len(self.player_stats), total_damage
    
    def get_summary_stats(self):
        """Возвращает сводную статистику по всем боям"""
        if not self.player_stats:
            return {}
        
        total_battles = len(self.player_stats)
        total_damage = sum(b['damage'] for b in self.player_stats)
        total_kills = sum(b['kills'] for b in self.player_stats)
        total_spotted = sum(b['spotted'] for b in self.player_stats)
        total_shots = sum(b['shots'] for b in self.player_stats)
        total_hits = sum(b['hits'] for b in self.player_stats)
        total_piercings = sum(b['piercings'] for b in self.player_stats)
        total_blocked = sum(b['damage_blocked'] for b in self.player_stats)
        
        return {
            'total_battles': total_battles,
            'avg_damage': round(total_damage / total_battles, 1),
            'avg_kills': round(total_kills / total_battles, 2),
            'avg_spotted': round(total_spotted / total_battles, 2),
            'avg_shots': round(total_shots / total_battles, 1),
            'avg_hits': round(total_hits / total_battles, 1),
            'avg_piercings': round(total_piercings / total_battles, 1),
            'avg_blocked': round(total_blocked / total_battles, 1),
            'accuracy': round((total_hits / total_shots * 100) if total_shots > 0 else 0, 1),
            'total_wins': self.total_wins,
            'win_rate': round((self.total_wins / total_battles * 100), 1)
        }
    
    def export_to_csv(self, filename):
        """Экспортирует данные в CSV"""
        headers, data, _, total_damage = self.get_table_data()
        
        with open(filename, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(data)
        
        # Добавляем сводную статистику в конец файла
        with open(filename, 'a', encoding='utf-8', newline='') as f:
            f.write("\n")
            f.write("\n=== СВОДНАЯ СТАТИСТИКА ===\n")
            
            stats = self.get_summary_stats()
            f.write(f"Всего боёв: {stats['total_battles']}\n")
            f.write(f"Средний урон: {stats['avg_damage']}\n")
            f.write(f"Средние фраги: {stats['avg_kills']}\n")
            f.write(f"Средний засвет: {stats['avg_spotted']}\n")
            f.write(f"Средние выстрелы: {stats['avg_shots']}\n")
            f.write(f"Средние попадания: {stats['avg_hits']}\n")
            f.write(f"Средние пробития: {stats['avg_piercings']}\n")
            f.write(f"Средний заблокированный урон: {stats['avg_blocked']}\n")
            f.write(f"Общая точность: {stats['accuracy']}%\n")
            f.write(f"Побед: {stats['total_wins']} ({stats['win_rate']}%)\n")
        
        print(f"\n💾 Данные экспортированы в {filename}")
        return True