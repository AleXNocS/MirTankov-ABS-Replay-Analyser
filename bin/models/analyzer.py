import json
import csv
from pathlib import Path
from collections import defaultdict
from .tank_lib import tank_names

class BattleMatrixAnalyzer:
    def __init__(self):
        self.players = set()
        self.battles = []
        self.battle_data = defaultdict(dict)      # battle_id -> player_name -> damage
        self.battle_vehicles = defaultdict(dict)  # battle_id -> player_name -> vehicle
        self.player_battles = defaultdict(int)
        self.total_wins = 0
        self.tank_names = tank_names
        self.skipped_battles = 0  # Счетчик пропущенных боев (30 игроков)
        self.processed_battles = 0  # Счетчик обработанных боев (14 игроков)
        
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
        
        # Ищем JSON блоки
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
    
    def count_players_in_battle(self, vehicles_meta):
        """Подсчитывает количество игроков в бою"""
        return len([v for v in vehicles_meta.values() if isinstance(v, dict)])
    
    def process_replay(self, replay_path):
        """Обрабатывает один реплей"""
        print(f"\n📁 Обработка: {Path(replay_path).name}")
        
        metadata, results = self.extract_json_from_replay(replay_path)
        
        if not metadata or not results:
            print("  ⚠️ Не удалось извлечь данные, пропускаем")
            return False
        
        # Получаем информацию о бое
        map_name = metadata.get('mapDisplayName', 'Неизвестно')
        date_time = metadata.get('dateTime', 'Неизвестно')
        
        # Собираем всех игроков
        vehicles_meta = metadata.get('vehicles', {})
        
        # Подсчитываем количество игроков
        players_count = self.count_players_in_battle(vehicles_meta)
        print(f"  👥 Участников в бою: {players_count}")
        
        # Проверяем, что это АБС режим (14 игроков - 7 на 7)
        if players_count == 30:  # Если 30 игроков (15 на 15) - это случайный бой
            self.skipped_battles += 1
            print(f"  ⏭️ Пропущен случайный бой (30 участников)")
            return False
        
        # Создаем ID для боя
        battle_id = f"{date_time}_{map_name}"
        
        # Добавляем бой в список
        self.battles.append({
            'id': battle_id,
            'date': date_time,
            'map': map_name,
            'file': Path(replay_path).name,
            'players_count': players_count
        })
        
        # Получаем статистику
        vehicles_stats = results.get('vehicles', {})
        
        battle_players = set()
        
        for vid, v in vehicles_meta.items():
            if not isinstance(v, dict):
                continue
            
            player_name = v.get('name', 'Unknown')
            vehicle_full = v.get('vehicleType', 'Unknown')
            vehicle = self.get_vehicle_name(vehicle_full)
            
            self.players.add(player_name)
            battle_players.add(player_name)
            
            stats = vehicles_stats.get(vid, [{}])[0]
            damage = stats.get('damageDealt', 0)
            
            self.battle_data[battle_id][player_name] = damage
            self.battle_vehicles[battle_id][player_name] = vehicle
        
        # Увеличиваем счетчик боёв для каждого игрока
        for player in battle_players:
            self.player_battles[player] += 1
        
        # Определяем исход боя
        winner_team = results.get('common', {}).get('winnerTeam', 0)
        player_name = metadata.get('playerName', '')
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
        
        self.processed_battles += 1
        print(f"  {outcome} на карте {map_name}")
        print(f"     Участников: {len(battle_players)}")
        return True
    
    def process_files(self, file_paths):
        """Обрабатывает список файлов"""
        if not file_paths:
            print("❌ Файлы не выбраны")
            return False
        
        print(f"\n{'='*80}")
        print(f"🔍 Выбрано файлов для анализа: {len(file_paths)}")
        print(f"{'='*80}")
        
        self.skipped_battles = 0
        self.processed_battles = 0
        
        for file_path in sorted(file_paths):
            self.process_replay(file_path)
        
        print(f"\n{'='*80}")
        print(f"📊 Статистика обработки:")
        print(f"   ✅ Обработано АБС боев (7×7): {self.processed_battles}")
        print(f"   ⏭️ Пропущено случайных боев (15×15): {self.skipped_battles}")
        print(f"   👥 Уникальных игроков: {len(self.players)}")
        print(f"{'='*80}")
        
        return self.processed_battles > 0
    
    def get_table_data(self):
        """Возвращает данные для таблицы"""
        # Сортируем бои по дате
        self.battles.sort(key=lambda x: x['date'])
        
        # Сортируем игроков по алфавиту
        sorted_players = sorted(self.players)
        
        # ФОРМИРУЕМ ЗАГОЛОВКИ: дата + карта в одной строке
        headers = ['Игрок', 'Ср.урон', 'Боёв']
        for battle in self.battles:
            date_part = battle['date'][:16]
            map_part = battle['map']
            headers.append(f"{date_part} {map_part}")
        
        # Создаем данные с техникой
        data = []
        for player in sorted_players:
            total_damage = 0
            battles_list = []
            
            for battle in self.battles:
                if player in self.battle_data[battle['id']]:
                    damage = self.battle_data[battle['id']][player]
                    vehicle = self.battle_vehicles[battle['id']][player]
                    battles_list.append(f"{vehicle} - {damage}")
                    total_damage += damage
                else:
                    battles_list.append('-')
            
            battles_count = self.player_battles[player]
            avg_damage = round(total_damage / battles_count) if battles_count > 0 else 0
            
            row = [player, avg_damage, battles_count] + battles_list
            data.append(row)
        
        return headers, data, len(self.battles)
    
    def export_to_csv(self, filename):
        """Экспортирует матрицу боев в CSV"""
        headers, data, _ = self.get_table_data()
        
        with open(filename, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(data)
        
        print(f"\n💾 Матрица боев экспортирована в {filename}")
        return True