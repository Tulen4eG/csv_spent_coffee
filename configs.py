import argparse


def configure_argparse(report_type):
    parser = argparse.ArgumentParser(description='Формирование отчетов')
    parser.add_argument('-f', '--files', nargs='+', help='Названия файлов')
    parser.add_argument(
        '-r', '--report', help='Тип отчета',
        choices=report_type,
    )
    return parser
