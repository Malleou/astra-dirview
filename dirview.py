#!/usr/bin/env python


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


import sys
from pathlib import Path

from PyQt5.QtCore import QDir, Qt, QSortFilterProxyModel, QTimer
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


class FileFilterProxyModel(QSortFilterProxyModel):
    """Фильтрация по имени с сохранением родительских папок для совпадений."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._filter_text = ""

    def setFilterText(self, text):
        new_text = text.strip().lower()
        if new_text == self._filter_text:
            return
        self._filter_text = new_text
        self.invalidateFilter()

    def filterAcceptsRow(self, source_row, source_parent):
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

        # Папка остается видимой, если внутри есть совпадение.
        if model.isDir(index):
            for row in range(model.rowCount(index)):
                if self.filterAcceptsRow(row, index):
                    return True

        return False


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.home_path = str(Path.home())
        self.setWindowTitle(f"Dir View - {self.home_path}")

        # Модель файловой системы: файлы, папки и скрытые элементы.
        self.model = QFileSystemModel(self)
        self.model.setRootPath(self.home_path)
        self.model.setFilter(QDir.AllEntries | QDir.Hidden | QDir.NoDotAndDotDot)

        # Прокси-модель для фильтрации по имени.
        self.proxy = FileFilterProxyModel(self)
        self.proxy.setSourceModel(self.model)
        self.proxy.setDynamicSortFilter(True)

        # Дерево.
        self.tree = QTreeView()
        self.tree.setModel(self.proxy)
        self.tree.setAnimated(True)
        self.tree.setIndentation(20)
        self.tree.setSortingEnabled(True)
        self.tree.setColumnWidth(0, 300)
        self.tree.sortByColumn(0, Qt.AscendingOrder)

        # Стартовая директория — домашняя директория пользователя.
        root_source_index = self.model.index(self.home_path)
        self.tree.setRootIndex(self.proxy.mapFromSource(root_source_index))

        # Поле фильтрации.
        self.filter_edit = QLineEdit()
        self.filter_edit.setPlaceholderText("Фильтр по имени файла или папки...")
        self.filter_edit.setClearButtonEnabled(True)

        # Небольшая задержка, чтобы не фильтровать на каждую букву.
        self.filter_timer = QTimer(self)
        self.filter_timer.setSingleShot(True)
        self.filter_timer.setInterval(FILTER_DELAY_MS)

        self.filter_edit.textChanged.connect(self.on_filter_text_changed)
        self.filter_timer.timeout.connect(self.apply_filter)

        # Компоновка.
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        layout.addWidget(self.filter_edit)
        layout.addWidget(self.tree)
        self.setCentralWidget(central_widget)

        self.resize(900, 600)

    def on_filter_text_changed(self, _text):
        self.filter_timer.start()

    def apply_filter(self):
        self.proxy.setFilterText(self.filter_edit.text())


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()