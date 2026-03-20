from wotreplay import ReplayData
from collections import Counter
import os

class ClanExtractor:
    """
    Отдельный класс для извлечения информации о клане соперника
    Использует wotreplay и не влияет на основной анализатор
    """
    
    @staticmethod
    def extract_opponent_clan_info(replay_path):
        """
        Извлекает информацию о клане соперника из реплея
        
        Args:
            replay_path: путь к файлу реплея
            
        Returns:
            dict: информация о клане {
                'clan_string': '4BD' или '4BD/MUCOP',
                'clans_list': ['4BD', 'MUCOP'],
                'is_mixed': True/False,
                'clan_stats': {'4BD': 7, 'MUCOP': 7},
                'success': True/False
            }
        """
        result = {
            'clan_string': 'Без клана',
            'primary_clan': 'Без клана',
            'clans_list': [],
            'is_mixed': False,
            'clan_stats': {},
            'success': False
        }
        
        try:
            # Загружаем реплей через wotreplay
            replay = ReplayData(file_path=str(replay_path))
            
            # Получаем сырые данные
            battle_data = replay.replay.battle_data
            
            # Данные об игроках находятся в battle_data[1]
            players_data = battle_data[1]
            
            # Находим владельца реплея и его команду
            owner_name = None
            owner_team = None
            
            # Получаем имя владельца из metadata
            if hasattr(replay, 'battle_metadata') and replay.battle_metadata:
                owner_name = replay.battle_metadata[0].get('player_name')
            
            # Находим команду владельца
            for player_id, player_info in players_data.items():
                if player_info.get('name') == owner_name:
                    owner_team = player_info.get('team')
                    break
            
            if owner_team is None:
                return result
            
            # Собираем кланы противников
            clan_counter = Counter()
            
            for player_id, player_info in players_data.items():
                player_name = player_info.get('name', '')
                team = player_info.get('team')
                clan = player_info.get('clanAbbrev', '').strip()
                
                # Пропускаем владельца
                if player_name == owner_name:
                    continue
                
                if team != owner_team and clan:  # Это противник с кланом
                    clan_counter[clan] += 1
            
            # Формируем результат
            clans_list = sorted(clan_counter.keys())
            result['clans_list'] = clans_list
            result['clan_stats'] = dict(clan_counter)
            result['is_mixed'] = len(clans_list) > 1
            result['success'] = True

            if not clans_list:
                result['clan_string'] = 'Без клана'
            elif len(clans_list) == 1:
                result['clan_string'] = clans_list[0]
            else:
                result['clan_string'] = '/'.join(clans_list)

            # Определяем организующий клан соперника через fortClanDBIDs
            bd0 = battle_data[0]
            db_to_abbrev = {
                p['clanDBID']: p['clanAbbrev']
                for p in bd0.get('players', {}).values()
                if p.get('clanDBID') and p.get('clanAbbrev')
            }
            fort_clan_ids = bd0.get('personal', {}).get('avatar', {}).get('fortClanDBIDs', [])

            if fort_clan_ids and len(fort_clan_ids) >= 2:
                for clan_db_id in fort_clan_ids:
                    # Используем bd0['players'] — там есть и team, и clanDBID
                    for p_info in bd0.get('players', {}).values():
                        if p_info.get('team') != owner_team and p_info.get('clanDBID') == clan_db_id:
                            result['primary_clan'] = db_to_abbrev.get(clan_db_id, 'Без клана')
                            break
                    if result['primary_clan'] != 'Без клана':
                        break

            # Fallback: если fortClanDBIDs недоступен — берём клан с большинством игроков
            if result['primary_clan'] == 'Без клана' and clan_counter:
                result['primary_clan'] = max(clan_counter, key=clan_counter.get)
                
        except Exception as e:
            print(f"⚠️ Ошибка при извлечении клана: {e}")
            result['success'] = False
        
        return result
    
    @staticmethod
    def extract_clan_string(replay_path):
        """
        Быстрый метод для получения только строки клана
        """
        info = ClanExtractor.extract_opponent_clan_info(replay_path)
        return info['clan_string']