from PyQt6.QtWidgets import QFileDialog

def select_files_gui():
    """Открывает диалог выбора файлов"""
    file_paths, _ = QFileDialog.getOpenFileNames(
        None,
        "Выберите файлы реплеев (.mtreplay)",
        "",
        "MT Replay files (*.mtreplay);;All files (*.*)"
    )
    return file_paths
