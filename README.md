# Dir View - просмотр дерева файловой системы (PyQt5)

Графическое приложение на Python/PyQt5: отображает дерево файловой
системы начиная с домашней директории пользователя, позволяет
фильтровать элементы по имени и считать размеры папок.

Выполнено в рамках тестового задания для стажёра Python.
За основу взят пример `itemviews/dirview` из PyQt5.

## Возможности

- Дерево файловой системы со стартом в домашней директории текущего пользователя.
- Отображение файлов и папок, включая скрытые.
- Фильтрация по имени файлов и папок (поле поиска).
- Подсчёт размера папки по двойному клику в колонке «Размер»
  (с отображением прогресса и сортировкой по размеру).
- Подсчёт выполняется в фоновом потоке — интерфейс не зависает.

### Зависимости
- Python 3
- PyQt5

```bash
sudo apt install python3 python3-pyqt5
```

## Установка и запуск

### Запуск из исходников
Из папки с программой, в bash:
```bash
python3 dirview.py
```
или
```bash
./dirview.py
```

### Сборка и установка .deb-пакета
```bash
# Установить инструменты сборки
sudo apt install devscripts debhelper dh-python -y

# Собрать пакет (из корня проекта)
dpkg-buildpackage -us -uc -b

# Установить полученный пакет (лежит на уровень выше)
sudo dpkg -i ../astra-dirview_*.deb

# Запустить
astra-dirview
```

---

## Структура проекта

```
astra-dirview/
├── dirview.py              # приложение (рабочая версия)
├── original_dirview.py     # исходный пример PyQt5 — точка отсчёта для патча
├── setup.py
├── README.md
└── debian/
    ├── patches/
    │   ├── series                          # список патчей
    │   └── 0001-dirview-improvements.patch # изменения относительно оригинала (DEP-3)
    ├── control
    ├── rules
    ├── changelog
    ├── copyright
    ├── astra-dirview.1            # man-страница
    ├── astra-dirview.manpages
    └── source/format
```

---

## Изменения относительно исходного кода

За основу взят `itemviews/dirview.py` (сохранён как `original_dirview.py`).

Все изменения относительно оригинала оформлены отдельным патчем в формате
**Debian quilt** с заголовком **DEP-3**:

```
debian/patches/0001-dirview-improvements.patch
```

Патч накладывается на оригинальный код автоматически при сборке пакета.

### Как посмотреть/применить патч

```bash
# просмотреть содержимое патча
cat debian/patches/0001-dirview-improvements.patch

# работа с патчем через quilt
export QUILT_PATCHES=debian/patches
quilt push -a   # применить патч поверх оригинала
quilt pop -a    # откатить к оригиналу
```

---

## Статус задач

|Задание|Статус|
|---|---|
|Установить Astra Linux 1.7/1.8 на виртуалку|✅ Ready|
|Обновиться до последней версии|✅ Ready|
|Установить из нашего репозитория QtCreator|✅ Ready|
|Взять за основу проект dirview|✅ Ready|
|Сделать стартовой директорией домашнюю директорию текущего пользователя|✅ Ready|
|Отображать файлы, папки, в том числе и скрытые|✅ Ready|
|Добавить QLineEdit виджет для фильтрации по имёнам файлов и папок|✅ Ready|
|Добавить столбец «Размер папки»|✅ Ready|
|Дебианизировать готовое решение|✅ Ready|
|Описать изменения относительно исходного кода|✅ Ready|
|Настроить CI/CD в проекте|🔄 at Work|

# Дневник работы

## Linux
1. Скачал установочный файл.
2. Скачал и установил VirtualBox.
3. Поставил виртуалку Astra Linux (почему-то графическая установка не сработала).
4. Проверил сетевые репозитории командой `cat /etc/apt/sources.list`.
5. `sudo nano /etc/apt/sources.list` и раскомментировал источники для обновления.
6. Обновил командой `sudo apt update && sudo apt dist-upgrade -y`.
7. `sudo apt install qtcreator -y`
8. `sudo apt install python3 python3-pyqt5 qtcreator git -y`
9. `sudo apt install python3-pip python3-venv build-essential -y`

   Занятно, что когда заходил в GitHub через konsole, программа запросила
   пароль, потом поставила мой пароль в значение логина и снова попросила
   пароль :)

## Код
За основу приложения взял пример `itemviews/dirview.py` из публичного
репозитория https://github.com/baoboa/pyqt5/tree/master/examples/itemviews
Оригинал сохранён в файле `original_dirview.py`.

## Дебианизация
1. Создал директорию `debian/` со служебными файлами:
   `control`, `rules`, `changelog`, `copyright`, `source/format`.
2. Указал лицензию **BSD-3-Clause** в `debian/copyright` — она унаследована
   от исходного примера PyQt (Nokia / Riverbank), нельзя менять на другую.
3. Добавил man-страницу `astra-dirview.1` и файл `astra-dirview.manpages`.
4. Настроил `.gitignore`, чтобы артефакты сборки
   (`.debhelper`, `*.substvars`, `debian/astra-dirview/`) не попадали в репозиторий.
5. Собрал пакет командой `dpkg-buildpackage -us -uc -b` и проверил установку.
