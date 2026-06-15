# Dir View - просмотр дерева файловой системы (PyQt5)

![CI](https://github.com/Malleou/astra-dirview/actions/workflows/ci.yml/badge.svg)

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

## Архитектура

Логика, не зависящая от GUI (подсчёт размеров, форматирование, обход
директорий), вынесена в отдельный модуль `core.py`. Это позволяет
покрывать её юнит-тестами без запуска графического интерфейса и PyQt5.

- `core.py` — чистая логика (тестируемая, без GUI).
- `dirview.py` — графический интерфейс на PyQt5, использует `core`.

### Зависимости
- Python 3
- PyQt5

```bash
sudo apt install python3 python3-pyqt5
```

**Для разработки и тестов:**
```bash
pip install pytest flake8
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

## Тесты и проверка качества

Логика из `core.py` покрыта юнит-тестами (pytest), стиль кода
проверяется линтером flake8.

```bash
# Запустить тесты
pytest tests/ -v

# Проверить стиль кода
flake8 core.py dirview.py tests/
```

Настройки линтера (длина строки, исключения) — в `setup.cfg`.

### CI/CD

При каждом `push` и `pull request` GitHub Actions автоматически
запускает flake8 и pytest на чистой машине.
Конфигурация: `.github/workflows/ci.yml`.

---

## Структура проекта

```
astra-dirview/
├── core.py                 # чистая логика (без GUI, тестируемая)
├── dirview.py              # приложение (GUI на PyQt5)
├── original_dirview.py     # исходный пример PyQt5 — точка отсчёта для патча
├── setup.py
├── setup.cfg               # настройки flake8
├── conftest.py             # конфигурация pytest
├── README.md
├── tests/                  # юнит-тесты для core.py
│   └── test_dirview.py
├── .github/
│   └── workflows/
│       └── ci.yml          # пайплайн CI (flake8 + pytest)
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
|Настроить CI/CD в проекте|✅ Ready|

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

## Тесты и автоматизация (CI/CD)
1. Вынес логику, не зависящую от GUI, в отдельный модуль `core.py`,
   чтобы её можно было тестировать без запуска PyQt5.
2. Написал юнит-тесты в `tests/` (pytest), настроил `conftest.py`.
3. Подключил линтер flake8, настройки вынес в `setup.cfg`.
4. Добавил `core` в `setup.py`, чтобы пакет собирался корректно.
5. Настроил CI на GitHub Actions (`.github/workflows/ci.yml`):
   при каждом push автоматически запускаются flake8 и pytest
   на чистой машине.
