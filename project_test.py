import argparse
import csv
import sys
from unittest.mock import patch, MagicMock

from pytest import fixture, raises

from configs import configure_argparse
from main import read_csv, median_coffee, main


STUDENT_ONE = [['Ревьювер', '2024-01-01', '3']]
STUDENT_TWO = [['Очень Крутой', '2024-01-02', '5']]
STUDENT_ONE_TWO = [
    ['Ревьювер', '2024-01-01', '3'],
    ['Очень Крутой', '2024-01-02', '5']
]
STUDENTS_BIG = [
    ['Ревьювер', '2024-01-01', '3'],
    ['Ревьювер', '2024-01-02', '4'],
    ['Очень Крутой',   '2024-01-01', '3'],
    ['Очень Крутой',   '2024-01-02', '5'],
    ['Очень Крутой',   '2024-01-03', '10'],
]
STUDENTS_BIG_RESULT = [('Очень Крутой', 5.0), ('Ревьювер', 3.5)]
NONEXISTENT_FILE = 'nonexistent.csv'


@fixture
def csv_file(tmp_path):
    """Создаёт временный CSV-файл с заданным содержимым."""
    def _create(filename, rows, header=True):
        file_path = tmp_path / filename
        with open(file_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            if header:
                writer.writerow(['student', 'date', 'coffee'])
            writer.writerows(rows)
        return file_path
    return _create


# ----- Тесты для read_csv -----
def test_read_csv_single_file(csv_file):
    file_path = csv_file('file1.csv', STUDENT_ONE_TWO)
    data = read_csv([str(file_path)])
    assert data
    assert data == STUDENT_ONE_TWO


def test_read_csv_multiple_files(csv_file):
    file1 = csv_file('file1.csv', STUDENT_ONE)
    file2 = csv_file('file2.csv', STUDENT_TWO)
    data = read_csv([str(file1), str(file2)])
    assert data == STUDENT_ONE_TWO


def test_read_csv_incorrect_file(capsys, monkeypatch):
    monkeypatch.setattr(sys, 'argv', ['script.py', '-f', NONEXISTENT_FILE])
    with raises(SystemExit) as exc_info:
        read_csv([NONEXISTENT_FILE])
    captured = capsys.readouterr()
    assert f'Ошибка: файл {NONEXISTENT_FILE} не существует\n' == captured.out
    assert exc_info.value.code == 1


# ----- Тесты для median_coffee -----
def test_median_coffee_basic(csv_file):
    file_path = csv_file('coffee.csv', STUDENTS_BIG)
    result = median_coffee([str(file_path)])
    expected = STUDENTS_BIG_RESULT
    assert result == expected


def test_median_coffee_empty_data(csv_file):
    file_path = csv_file('empty.csv', [], header=True)
    result = median_coffee([str(file_path)])
    assert result == []


# ----- Тесты для main -----
def test_main_correct_call(csv_file, monkeypatch):
    file_path = csv_file('data.csv', STUDENTS_BIG)
    args = ['main.py', '-f', str(file_path), '-r', 'median-coffee']
    monkeypatch.setattr(sys, 'argv', args)
    mock_median = MagicMock(return_value=STUDENTS_BIG_RESULT)
    with patch.dict('main.REPORT_TYPE', {'median-coffee': mock_median}):
        main()
        mock_median.assert_called_once_with([str(file_path)])


def test_main_no_files(capsys, monkeypatch):
    monkeypatch.setattr(sys, 'argv', ['script.py', '-r', 'median-coffee'])
    with raises(SystemExit) as exc_info:
        main()
    captured = capsys.readouterr()
    assert "Ошибка: не указаны файлы\n" == captured.out
    assert exc_info.value.code == 1


def test_main_no_report(capsys, monkeypatch):
    monkeypatch.setattr(sys, 'argv', ['script.py', '-f', 'data.csv'])
    with raises(SystemExit) as exc_info:
        main()
    captured = capsys.readouterr()
    assert "Ошибка: не указан тип отчёта\n" == captured.out
    assert exc_info.value.code == 1


# ----- Тесты для configure_argparse -----
def test_configure_argparse_choices():
    parser = configure_argparse(['median-coffee'])
    action = parser._option_string_actions['-r']
    assert action.choices == ['median-coffee']
    assert isinstance(parser, argparse.ArgumentParser)


def test_configure_argparse_arguments():
    parser = configure_argparse(['median-coffee'])
    args = parser.parse_args(
        ['-f', 'file1.csv', 'file2.csv', '-r', 'median-coffee']
    )
    assert args.files == ['file1.csv', 'file2.csv']
    assert args.report == 'median-coffee'
