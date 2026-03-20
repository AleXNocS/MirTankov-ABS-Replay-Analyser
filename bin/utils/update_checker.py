import json
import ssl
import urllib.request
import urllib.error
from packaging.version import Version
from PyQt6.QtCore import QThread, pyqtSignal


class UpdateCheckerThread(QThread):
    update_available = pyqtSignal(str, str)  # (latest_version, release_url)
    up_to_date = pyqtSignal()
    check_failed = pyqtSignal()

    def __init__(self, current_version: str, api_url: str):
        super().__init__()
        self._current = current_version
        self._api_url = api_url

    def run(self):
        try:
            req = urllib.request.Request(
                self._api_url,
                headers={"User-Agent": "MirTankov-ABS-Replay-Analyser"}
            )
            ctx = ssl.create_default_context()
            with urllib.request.urlopen(req, timeout=10, context=ctx) as resp:
                data = json.loads(resp.read().decode())

            tag = data.get("tag_name", "").lstrip("v.")
            html_url = data.get("html_url", "")

            if not tag:
                self.check_failed.emit()
                return

            if Version(tag) > Version(self._current):
                self.update_available.emit(tag, html_url)
            else:
                self.up_to_date.emit()

        except Exception as e:
            print(f"⚠️ Ошибка проверки обновлений: {e}")
            self.check_failed.emit()
