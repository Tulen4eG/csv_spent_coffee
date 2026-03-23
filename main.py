from csv import reader
from sys import exit

from statistics import median
from tabulate import tabulate

from configs import configure_argparse


HEADERS_MEDIAN_COFFEE = ['student', 'median_coffee']


def read_csv(csv_files):
    """Читает csv файлы и складывает все строки в массив"""

    data = []
    for csv_file in csv_files:
        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                csv_reader = reader(f)
                next(csv_reader)  # пропуск шапки
                for row in csv_reader:
                    data.append(row)
        except FileNotFoundError:
            print(f'Ошибка: файл {csv_file} не существует')
            exit(1)
    return data


def console_output_data(data, headers, colalign=('left', 'right')):
    """Приводит данные к табличному виду и выводит в консоль"""

    print(tabulate(
        data, headers=headers, colalign=colalign,
        tablefmt='grid',
    ))


def median_coffee(csv_files):
    """Формирует отчет по медиане выпитого кофе"""

    students = dict()
    data = read_csv(csv_files)

    for row in data:
        student = row[0]
        coffee_spent = row[2]
        if student in students:
            students[student].append(int(coffee_spent))
        else:
            students[student] = [int(coffee_spent)]
    # преобразование массивов выпитого кофе в их медианы
    for student, values in students.items():
        students[student] = median(values)

    sorted_by_median = sorted(
        students.items(), key=lambda item: item[1], reverse=True
    )
    console_output_data(sorted_by_median, HEADERS_MEDIAN_COFFEE)
    return sorted_by_median


REPORT_TYPE = {
    'median-coffee': median_coffee,
    # Новые виды сортировок отчетов нужно прописать тут
    # 'команда': функция,
}


def main():
    arg_parser = configure_argparse(REPORT_TYPE.keys())
    args = arg_parser.parse_args()
    parser_report = args.report
    if not args.report:
        print('Ошибка: не указан тип отчёта')
        exit(1)
    if args.files:
        REPORT_TYPE[parser_report](args.files)
    else:
        print('Ошибка: не указаны файлы')
        exit(1)


if __name__ == '__main__':
    main()
