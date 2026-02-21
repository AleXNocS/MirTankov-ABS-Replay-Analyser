import json
import csv
from pathlib import Path
from collections import defaultdict
from .tank_lib import tank_names  # Импортируем словарь с названиями танков

class BattleMatrixAnalyzer:
    def __init__(self):
        self.players = set()
        self.battles = []
        self.battle_data = defaultdict(dict)      # battle_id -> player_name -> damage
        self.battle_vehicles = defaultdict(dict)  # battle_id -> player_name -> vehicle
        self.player_battles = defaultdict(int)
        self.total_wins = 0
        self.tank_names = tank_names  # Сохраняем словарь
        
    def get_vehicle_name(self, vehicle_full):
        """
        Возвращает игровое название танка по точному совпадению
        Если точного совпадения нет, возвращает техническое название
        """
        # Извлекаем ключ из полного названия
        # Например из "ussr:R231_Object_278" нужно получить "R231_Object_278"
        if ':' in vehicle_full:
            vehicle_key = vehicle_full.split(':', 1)[1]
        else:
            vehicle_key = vehicle_full
        
        # Ищем точное совпадение в словаре
        if vehicle_key in self.tank_names:
            return self.tank_names[vehicle_key]
        
        # Если точного совпадения нет, возвращаем очищенное техническое название
        # Убираем префикс страны
        if ':' in vehicle_full:
            vehicle_full = vehicle_full.split(':', 1)[1]
        
        # Заменяем подчеркивания на пробелы
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
        
        # Создаем ID для боя
        battle_id = f"{date_time}_{map_name}"
        
        # Добавляем бой в список
        self.battles.append({
            'id': battle_id,
            'date': date_time,
            'map': map_name,
            'file': Path(replay_path).name
        })
        
        # Собираем всех игроков
        vehicles_meta = metadata.get('vehicles', {})
        vehicles_stats = results.get('vehicles', {})
        
        battle_players = set()
        
        for vid, v in vehicles_meta.items():
            if not isinstance(v, dict):
                continue
            
            player_name = v.get('name', 'Unknown')
            vehicle_full = v.get('vehicleType', 'Unknown')
            # Получаем название танка используя точное совпадение
            vehicle = self.get_vehicle_name(vehicle_full)
            
            # Добавляем игрока в общий список
            self.players.add(player_name)
            battle_players.add(player_name)
            
            # Получаем урон
            stats = vehicles_stats.get(vid, [{}])[0]
            damage = stats.get('damageDealt', 0)
            
            # Сохраняем урон и технику для этого боя
            self.battle_data[battle_id][player_name] = damage
            self.battle_vehicles[battle_id][player_name] = vehicle
        
        # Увеличиваем счетчик боёв для каждого игрока в этом бою
        for player in battle_players:
            self.player_battles[player] += 1
        
        # Определяем исход боя для подсчета побед
        winner_team = results.get('common', {}).get('winnerTeam', 0)
        player_name = metadata.get('playerName', '')
        player_team = None
        
        # Находим команду игрока
        for vid, v in vehicles_meta.items():
            if isinstance(v, dict) and v.get('name') == player_name:
                player_team = v.get('team', 0)
                break
        
        # Если бой выигран, увеличиваем счетчик побед
        if player_team and winner_team == player_team:
            self.total_wins += 1
            outcome = "🏆 ПОБЕДА"
        else:
            outcome = "❌ ПОРАЖЕНИЕ"
        
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
        
        processed = 0
        for file_path in sorted(file_paths):
            if self.process_replay(file_path):
                processed += 1
        
        print(f"\n{'='*80}")
        print(f"✅ Успешно обработано файлов: {processed}/{len(file_paths)}")
        print(f"👥 Уникальных игроков: {len(self.players)}")
        print(f"{'='*80}")
        
        return processed > 0
    
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
                    # Форматируем ячейку как "Танк - урон"
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