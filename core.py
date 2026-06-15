"""Чистая логика без зависимостей от GUI/Qt.
Эти функции не используют PyQt5 и легко тестируются.
"""

import os
from typing import Iterator, Tuple


def human_readable_size(num_bytes: int) -> str:
    """Переводит байты в читаемый вид"""
    units = ["Б", "КБ", "МБ", "ГБ", "ТБ"]
    size = float(num_bytes)
    for unit in units:
        if size < 1024.0 or unit == units[-1]:
            if unit == "Б":
                return f"{int(size)} {unit}"
            return f"{size:.1f} {unit}"
        size /= 1024.0


def iter_folder_size(path: str) -> Iterator[Tuple[str, int, int]]:
    """
    Считает суммарный размер папки через os.scandir.
    Периодически отдаёт промежуточный результат.
    """
    total = 0
    count = 0
    stack = [path]
    display_files_count = 53
    while stack:
        current = stack.pop()
        try:
            with os.scandir(current) as it:
                for entry in it:
                    try:
                        if entry.is_symlink():
                            continue
                        if entry.is_dir(follow_symlinks=False):
                            stack.append(entry.path)
                        elif entry.is_file(follow_symlinks=False):
                            total += entry.stat(follow_symlinks=False).st_size
                            count += 1
                            if count % display_files_count == 0:
                                yield ("progress", count, total)
                    except OSError:
                        pass
        except OSError:
            pass
    yield ("done", count, total)
