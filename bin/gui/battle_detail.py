import sys
import os
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QTableWidget, QTableWidgetItem, QHeaderView, QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.battle_detail_extractor import BattleDetailExtractor

# Row background colors for each team (dark-theme friendly)
TEAM_COLORS = {
    'owner': QColor('#1a3a5c'),   # dark blue  — owner's team
    'enemy': QColor('#5c1a1a'),   # dark red   — enemy team
}

HEADERS = [
    'Игрок', 'Клан', 'Танк',
    'Урон', 'Засвет', 'Гусля',
    'Потенц.', 'Выстрелы', 'Попадания', 'Точность%',
    'Фраги', 'Выжил', 'Время жизни'
]


def _fmt_time(seconds):
    m, s = divmod(int(seconds), 60)
    return f"{m}:{s:02d}"


class BattleDetailWindow(QDialog):

    def __init__(self, file_path, battle_info, tank_short_names, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"🎮 Детали боя — {battle_info.get('map', '')}  {battle_info.get('date', '')[:16]}")
        self.setMinimumSize(1300, 550)
        self.resize(1500, 600)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)

        # --- Header info bar ---
        layout.addWidget(self._build_header(battle_info))

        # --- Load data ---
        detail = BattleDetailExtractor.extract(file_path, tank_short_names)
        if not detail:
            err = QLabel("❌ Не удалось загрузить детальные данные боя.")
            err.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(err)
            return

        owner_team = battle_info.get('player_team', 0)

        # --- Color legend ---
        layout.addWidget(self._build_legend(owner_team))

        # --- Table ---
        table = self._build_table(detail['players'], owner_team)
        layout.addWidget(table)

    # ------------------------------------------------------------------
    def _build_header(self, battle_info):
        frame = QFrame()
        frame.setFrameShape(QFrame.Shape.StyledPanel)
        hl = QHBoxLayout(frame)
        hl.setContentsMargins(8, 6, 8, 6)

        is_win = battle_info.get('is_win', False)
        result_text = "🏆 ПОБЕДА" if is_win else "💔 ПОРАЖЕНИЕ"
        result_color = "#4CAF50" if is_win else "#FF6B6B"

        clan_info = battle_info.get('clan_info', {})
        clan_str = clan_info.get('clan', '?')
        clan_icon = "⚔️" if clan_info.get('is_mixed') else "🏷️"

        items = [
            ("🗺️ Карта:", battle_info.get('map', '?')),
            ("📅 Дата:", battle_info.get('date', '?')[:16]),
            ("🏁 Результат:", result_text, result_color),
            (f"{clan_icon} Соперник:", clan_str),
        ]

        bold = QFont()
        bold.setBold(True)

        for item in items:
            lbl_key = QLabel(item[0])
            lbl_key.setFont(bold)
            lbl_val = QLabel(item[1])
            if len(item) == 3:
                lbl_val.setStyleSheet(f"color: {item[2]};")
            hl.addWidget(lbl_key)
            hl.addWidget(lbl_val)
            sep = QFrame()
            sep.setFrameShape(QFrame.Shape.VLine)
            sep.setFrameShadow(QFrame.Shadow.Sunken)
            sep.setFixedWidth(1)
            hl.addWidget(sep)

        hl.addStretch()
        return frame

    def _build_legend(self, owner_team):
        hl = QHBoxLayout()
        hl.setContentsMargins(0, 0, 0, 0)

        def swatch(color, text):
            lbl = QLabel(f"  {text}  ")
            lbl.setAutoFillBackground(True)
            p = lbl.palette()
            p.setColor(lbl.backgroundRole(), color)
            lbl.setPalette(p)
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            return lbl

        enemy_team = 1 if owner_team == 2 else 2
        hl.addWidget(swatch(TEAM_COLORS['owner'], f"Команда {owner_team} (ваша)"))
        hl.addSpacing(8)
        hl.addWidget(swatch(TEAM_COLORS['enemy'], f"Команда {enemy_team} (соперник)"))
        hl.addStretch()

        frame = QFrame()
        frame.setLayout(hl)
        return frame

    def _build_table(self, players, owner_team):
        # Sort: owner's team first (by damage desc), then enemy team (by damage desc)
        own = sorted([p for p in players if p['team'] == owner_team], key=lambda x: -x['damage'])
        enemy = sorted([p for p in players if p['team'] != owner_team], key=lambda x: -x['damage'])
        sorted_players = own + enemy

        table = QTableWidget()
        table.setRowCount(len(sorted_players))
        table.setColumnCount(len(HEADERS))
        table.setHorizontalHeaderLabels(HEADERS)
        table.setSortingEnabled(False)
        table.setAlternatingRowColors(False)
        table.setWordWrap(False)
        table.verticalHeader().setDefaultSectionSize(28)

        header = table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        header.setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)

        for row, p in enumerate(sorted_players):
            is_owner_team = (p['team'] == owner_team)
            bg = TEAM_COLORS['owner'] if is_owner_team else TEAM_COLORS['enemy']

            survived = "✅" if p['health'] > 0 else "💀"
            values = [
                p['name'],
                p['clan'],
                p['tank'],
                p['damage'],
                p['assist_radio'],
                p['assist_track'],
                p['potential'],
                p['shots'],
                p['hits'],
                f"{p['accuracy']:.1f}",
                p['kills'],
                survived,
                _fmt_time(p['lifetime']),
            ]

            for col, val in enumerate(values):
                item = QTableWidgetItem(str(val))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                item.setBackground(bg)
                # Left-align name and clan
                if col in (0, 1, 2):
                    item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
                table.setItem(row, col, item)

        # Columns 0-2: fit to content; rest: fit to header text width
        fm = table.horizontalHeader().fontMetrics()
        for col in range(table.columnCount()):
            if col <= 2:
                table.resizeColumnToContents(col)
            else:
                table.setColumnWidth(col, fm.horizontalAdvance(HEADERS[col]) + 30)

        return table
