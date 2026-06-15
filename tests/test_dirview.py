"""Юнит-тесты для функций dirview (без GUI)"""

from core import human_readable_size, iter_folder_size


def test_bytes_no_decimals():
    """Байты без дробей"""
    assert human_readable_size(0) == "0 Б"
    assert human_readable_size(500) == "500 Б"
    assert human_readable_size(1023) == "1023 Б"


def test_kilobytes():
    assert human_readable_size(1024) == "1.0 КБ"
    assert human_readable_size(1536) == "1.5 КБ"


def test_megabytes():
    assert human_readable_size(1024 * 1024) == "1.0 МБ"


def test_gigabytes():
    assert human_readable_size(1024 ** 3) == "1.0 ГБ"


def test_large_values_use_terabytes():
    result = human_readable_size(1024 ** 4)
    assert result.endswith("ТБ")


def test_empty_folder(tmp_path):
    """Пустая папка - размер 0, файлов 0"""
    events = list(iter_folder_size(str(tmp_path)))
    status, count, total = events[-1]
    assert status == "done"
    assert count == 0
    assert total == 0


def test_single_file_size(tmp_path):
    """Учитывается ли размер файла"""
    f = tmp_path / "hello.txt"
    f.write_bytes(b"x" * 100)

    events = list(iter_folder_size(str(tmp_path)))
    status, count, total = events[-1]
    assert status == "done"
    assert count == 1
    assert total == 100


def test_nested_folders(tmp_path):
    """Файлы во вложенных папках тоже считаются"""
    (tmp_path / "a").mkdir()
    (tmp_path / "a" / "b").mkdir()
    (tmp_path / "file1.txt").write_bytes(b"x" * 10)
    (tmp_path / "a" / "file2.txt").write_bytes(b"x" * 20)
    (tmp_path / "a" / "b" / "file3.txt").write_bytes(b"x" * 30)

    events = list(iter_folder_size(str(tmp_path)))
    status, count, total = events[-1]
    assert status == "done"
    assert count == 3
    assert total == 60


def test_last_event_is_done(tmp_path):
    """Последнее событие всегда done"""
    (tmp_path / "f.txt").write_bytes(b"data")
    events = list(iter_folder_size(str(tmp_path)))
    assert events[-1][0] == "done"


def test_nonexistent_path_does_not_crash():
    """Несуществующий путь не роняет функцию, отдаёт done с нулями"""
    events = list(iter_folder_size("/no/such/path/12345"))
    status, count, total = events[-1]
    assert status == "done"
    assert count == 0
    assert total == 0
