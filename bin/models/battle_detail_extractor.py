import json
from pathlib import Path
from wotreplay import ReplayData

BACKSLASH, QUOTE, OPEN, CLOSE = 92, 34, 123, 125


class BattleDetailExtractor:

    @staticmethod
    def _parse_json_blocks(data):
        metadata = None
        results = None
        pos = 0
        while pos < len(data) and (not metadata or not results):
            if data[pos] == OPEN:
                end, depth, in_str, esc = pos, 0, False, False
                while end < len(data):
                    b = data[end]
                    if not in_str:
                        if b == OPEN:
                            depth += 1
                        elif b == CLOSE:
                            depth -= 1
                            if depth == 0:
                                break
                        elif b == QUOTE:
                            in_str = True
                    else:
                        if b == QUOTE and not esc:
                            in_str = False
                    esc = (b == BACKSLASH and not esc)
                    end += 1
                if depth == 0 and end - pos > 100:
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

    @staticmethod
    def _get_short_name(vehicle_full, tank_short_names):
        if not vehicle_full:
            return '?'
        key = vehicle_full.split(':', 1)[1] if ':' in vehicle_full else vehicle_full
        if key in tank_short_names:
            return tank_short_names[key]
        return key.replace('_', ' ') if '_' in key else key

    @staticmethod
    def extract(file_path, tank_short_names):
        """
        Extracts detailed stats for all 14 players in a battle.
        Returns dict with 'players', 'duration', 'winner_team', or None on failure.
        """
        try:
            with open(file_path, 'rb') as f:
                data = f.read()
        except Exception as e:
            print(f"  ❌ Cannot read file: {e}")
            return None

        metadata, results = BattleDetailExtractor._parse_json_blocks(data)
        if not metadata or not results:
            print("  ❌ Could not parse replay JSON blocks")
            return None

        # Get names + clans for all 14 players via wotreplay
        wot_players = {}
        try:
            replay = ReplayData(file_path=str(file_path))
            wot_players = replay.replay.battle_data[1]
        except Exception as e:
            print(f"  ⚠️ wotreplay error: {e}")

        # Build vid -> vehicleType from metadata (owner's team only)
        vid_to_vehicle = {
            vid: v.get('vehicleType', '')
            for vid, v in metadata.get('vehicles', {}).items()
            if isinstance(v, dict)
        }

        common = results.get('common', {})
        players = []

        for vid, vlist in results['vehicles'].items():
            stats = vlist[0] if isinstance(vlist, list) else vlist

            # Resolve name and clan — try wotreplay first, fall back to metadata
            wot_info = wot_players.get(int(vid), wot_players.get(str(vid), {}))
            meta_info = metadata.get('vehicles', {}).get(vid, {})
            name = wot_info.get('name') or meta_info.get('name', '?')
            clan = wot_info.get('clanAbbrev', meta_info.get('clanAbbrev', '')) or ''

            # Resolve tank name
            vehicle_full = vid_to_vehicle.get(vid, '')
            tank = BattleDetailExtractor._get_short_name(vehicle_full, tank_short_names)

            shots = stats.get('shots', 0)
            hits = stats.get('directHits', 0)
            accuracy = round(hits / shots * 100, 1) if shots > 0 else 0.0

            players.append({
                'name': name,
                'clan': clan,
                'team': stats.get('team', 0),
                'tank': tank,
                'damage': stats.get('damageDealt', 0),
                'assist_radio': stats.get('damageAssistedRadio', 0),
                'assist_track': stats.get('damageAssistedTrack', 0),
                'potential': stats.get('potentialDamageReceived', 0),
                'shots': shots,
                'hits': hits,
                'accuracy': accuracy,
                'kills': stats.get('kills', 0),
                'health': stats.get('health', 0),
                'max_health': stats.get('maxHealth', 0),
                'lifetime': stats.get('lifeTime', 0),
            })

        return {
            'players': players,
            'duration': common.get('duration', 0),
            'winner_team': common.get('winnerTeam', 0),
        }
