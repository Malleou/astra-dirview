#!/usr/bin/env python3


#############################################################################
##
## Copyright (C) 2017 Riverbank Computing Limited.
## Copyright (C) 2017 Hans-Peter Jansen <hpj@urpla.net>
## Copyright (C) 2010 Nokia Corporation and/or its subsidiary(-ies).
## All rights reserved.
##
## This file is part of the examples of PyQt.
##
## $QT_BEGIN_LICENSE:BSD$
## You may use this file under the terms of the BSD license as follows:
##
## "Redistribution and use in source and binary forms, with or without
## modification, are permitted provided that the following conditions are
## met:
##   * Redistributions of source code must retain the above copyright
##     notice, this list of conditions and the following disclaimer.
##   * Redistributions in binary form must reproduce the above copyright
##     notice, this list of conditions and the following disclaimer in
##     the documentation and/or other materials provided with the
##     distribution.
##   * Neither the name of Nokia Corporation and its Subsidiary(-ies) nor
##     the names of its contributors may be used to endorse or promote
##     products derived from this software without specific prior written
##     permission.
##
## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
## "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
## LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
## A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
## OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
## SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
## LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
## DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
## THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
## (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
## OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE."
## $QT_END_LICENSE$
##
#############################################################################

import os
import sys
from pathlib import Path

from PyQt5.QtCore import (
    QDir,
    Qt,
    QSortFilterProxyModel,
    QTimer,
    QObject,
    QThread,
    pyqtSignal,
)
from PyQt5.QtWidgets import (
    QApplication,
    QFileSystemModel,
    QLineEdit,
    QMainWindow,
    QTreeView,
    QVBoxLayout,
    QWidget,
)

FILTER_DELAY_MS = 250
SIZE_COLUMN = 1  # Колонка "Размер" в QFileSystemModel.


def human_readable_size(num_bytes):
    """Переводит байты в читаемый вид"""

    units = ["Б", "КБ", "МБ", "ГБ", "ТБ"]
    size = float(num_bytes)
    for unit in units:
        if size < 1024.0 or unit == units[-1]:
            if unit == "Б":
                return f"{int(size)} {unit}"
            return f"{size:.1f} {unit}"
        size /= 1024.0


def iter_folder_size(path):
    """
    Считает суммарный размер папки через os.scandir
    Периодически отдает промежуточный результат
    """

    total = 0
    count = 0
    stack = [path]
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
                            if count % 53 == 0:
                                yield ("progress", count, total)
                    except OSError:
                        pass
        except OSError:
            pass
    yield ("done", count, total)


class FolderSizeWorker(QObject):
    """
    Рлдсчёт размера папки в отдельном потоке

    Работает с QThread (через moveToThread)
    Пока считает, возвращает progress
    finished по завершении
    stop() позволяет прервать подсчет досрочно.
    """

    progress = pyqtSignal(str, int)  # path, files_count
    finished = pyqtSignal(str, int)  # path, size

    def __init__(self, path):
        super().__init__()
        self._path = path
        self._stop = False

    def stop(self):
        self._stop = True

    def run(self):
        for item in iter_folder_size(self._path):
            if self._stop:
                return
            if item[0] == "progress":
                self.progress.emit(self._path, item[1])
            else:
                self.finished.emit(self._path, item[2])


class FileSystemSizeModel(QFileSystemModel):
    """
    Модель файловой системы с поддержкой размеров папок.

    Хранит кэш посчитанных размеров и состояние подсчета,
    а в колонке размера для папок отображает:
      - "Двойной клик" если размер еще не считали,
      - "Подсчет... (N файлов)" во время подсчета,
      - читаемый размер после завершения.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.folder_sizes = {}   # path -> int (готовый размер)
        self.progress_info = {}  # path -> int (файлов обработано, пока считается)

    def set_progress(self, path, count):
        """Обновляет прогресс подсчета для папки"""
        self.progress_info[path] = count
        self._emit_size_changed(path)

    def set_folder_size(self, path, size):
        """Сохраняет итоговый размер папки"""
        self.progress_info.pop(path, None)
        self.folder_sizes[path] = size
        self._emit_size_changed(path)

    def _emit_size_changed(self, path):
        """Сообщает, что ячейка размера изменилась."""
        idx = self.index(path)
        if idx.isValid():
            size_idx = idx.sibling(idx.row(), SIZE_COLUMN)
            self.dataChanged.emit(size_idx, size_idx, [Qt.DisplayRole])
            
    
    def data(self, index, role=Qt.DisplayRole):
        """Текст размера папки в число"""
        if index.isValid() and index.column() == SIZE_COLUMN and self.isDir(index):
            path = self.filePath(index.sibling(index.row(), 0))

            if role == Qt.UserRole:
                return self.folder_sizes.get(path, -1)

            if role == Qt.DisplayRole:
                if path in self.progress_info:
                    return f"Подсчет... ({self.progress_info[path]} файлов)"
                if path in self.folder_sizes:
                    return human_readable_size(self.folder_sizes[path])
                return "Двойной клик"

        return super().data(index, role)


class FileFilterProxyModel(QSortFilterProxyModel):
    """Фильтрация по имени"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._filter_text = ""

    def setFilterText(self, text):
        """Устанавливает текст фильтра и перезапускает фильтрацию при изменении."""
        new_text = text.strip().lower()
        if new_text == self._filter_text:
            return
        self._filter_text = new_text
        self.invalidateFilter()

    def filterAcceptsRow(self, source_row, source_parent):
        """Решает, показывать ли строку: по совпадению имени или содержимого папки."""
        if not self._filter_text:
            return True
        model = self.sourceModel()
        if model is None:
            return False
        index = model.index(source_row, 0, source_parent)
        if not index.isValid():
            return False
        if self._filter_text in model.fileName(index).lower():
            return True
        if model.isDir(index):
            for row in range(model.rowCount(index)):
                if self.filterAcceptsRow(row, index):
                    return True
        return False
    
    def lessThan(self, left, right):
        """Особая сортировка для колонки размера"""
        model = self.sourceModel()

        if left.column() == SIZE_COLUMN and right.column() == SIZE_COLUMN:
            left_dir = model.isDir(left)
            right_dir = model.isDir(right)

            if left_dir:
                left_size = model.data(left, Qt.UserRole)
            else:
                left_size = model.size(left)

            if right_dir:
                right_size = model.data(right, Qt.UserRole)
            else:
                right_size = model.size(right)

            return left_size < right_size

        return super().lessThan(left, right)


class MainWindow(QMainWindow):
    """Главное окно приложения"""

    def __init__(self):
        super().__init__()

        self.home_path = str(Path.home())
        self.setWindowTitle(f"Dir View - {self.home_path}")

        self.model = FileSystemSizeModel(self)
        self.model.setRootPath(self.home_path)
        self.model.setFilter(QDir.AllEntries | QDir.Hidden | QDir.NoDotAndDotDot)

        self.proxy = FileFilterProxyModel(self)
        self.proxy.setSourceModel(self.model)
        self.proxy.setDynamicSortFilter(True)

        self.tree = QTreeView()
        self.tree.setModel(self.proxy)
        self.tree.setAnimated(True)
        self.tree.setIndentation(20)
        self.tree.setSortingEnabled(True)
        self.tree.setColumnWidth(0, 300)
        self.tree.sortByColumn(0, Qt.AscendingOrder)
        self.tree.doubleClicked.connect(self.on_tree_double_clicked)

        root_source_index = self.model.index(self.home_path)
        self.tree.setRootIndex(self.proxy.mapFromSource(root_source_index))

        self.filter_edit = QLineEdit()
        self.filter_edit.setPlaceholderText("Фильтр по имени файла или папки...")
        self.filter_edit.setClearButtonEnabled(True)

        self.filter_timer = QTimer(self)
        self.filter_timer.setSingleShot(True)
        self.filter_timer.setInterval(FILTER_DELAY_MS)

        self.filter_edit.textChanged.connect(self.on_filter_text_changed)
        self.filter_timer.timeout.connect(self.apply_filter)

        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        layout.addWidget(self.filter_edit)
        layout.addWidget(self.tree)
        self.setCentralWidget(central_widget)

        self.resize(900, 600)

        self._threads = {}
        self._workers = {}


    def on_filter_text_changed(self, _text):
        """Перезапуск таймера"""
        self.filter_timer.start()

    def apply_filter(self):
        self.proxy.setFilterText(self.filter_edit.text())


    def on_tree_double_clicked(self, proxy_index):
        """Подсчёт размера папок по двойному клику"""
        if not proxy_index.isValid():
            return
        src_index = self.proxy.mapToSource(proxy_index)
        if not self.model.isDir(src_index):
            return
        if proxy_index.column() != SIZE_COLUMN:
            return
        path = self.model.filePath(src_index.sibling(src_index.row(), 0))
        self.start_size_calc(path)

    def start_size_calc(self, path):
        if path in self._threads:
            return

        self.model.set_progress(path, 0)

        thread = QThread(self)
        worker = FolderSizeWorker(path)
        worker.moveToThread(thread)

        thread.started.connect(worker.run)
        worker.progress.connect(self.model.set_progress)
        worker.finished.connect(self.on_size_ready)
        worker.finished.connect(thread.quit)
        worker.finished.connect(worker.deleteLater)
        thread.finished.connect(thread.deleteLater)
        thread.finished.connect(lambda p=path: self._cleanup(p))

        self._threads[path] = thread
        self._workers[path] = worker
        thread.start()

    def on_size_ready(self, path, size):
        """Сохраняет посчитанный размер"""
        self.model.set_folder_size(path, size)

    def _cleanup(self, path):
        """Убирает завершившийся поток и воркер из хранилищ"""
        self._threads.pop(path, None)
        self._workers.pop(path, None)


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
