#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Cleans duplicate lines from file by appending line
or field value to a set() and comparing its length.

usage: clean_duplicates.py [-h] [-o OUTPUT] [-c COLUMN] input

positional arguments:
  input                 input file name

optional arguments:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        output file name
  -c COLUMN, --column COLUMN
                        column index or title
'''

from argparse import ArgumentParser
from csv import reader, writer, QUOTE_MINIMAL
from os.path import basename, splitext

def clean_duplicates(input_name, output_name=None,
    column=None, quoting=QUOTE_MINIMAL):
    '''
    Perform line duplicate removal.
    '''
    print('Cleaning duplicate lines...')

    if not output_name:
        name, ext = splitext(basename(input_name))
        output_name = name + '_CLEANED' + ext

    delimiter = get_file_delimiter(input_name)

    set_values = set()

    with open(input_name, 'rt', encoding='utf8', errors='ignore') as input_file:
        file_reader = reader(input_file, delimiter=delimiter, quoting=quoting)
        header = next(file_reader)

        if isinstance(column, str):
            column = header.index(column)

        elif isinstance(column, int):
            column = header[column]

        with open(output_name, 'w', newline='', encoding='utf8', errors='ignore') as output_file:
            file_writer = writer(output_file, delimiter=delimiter, quoting=quoting)
            file_writer.writerow(header)

            for line in file_reader:
                len_set_values = len(set_values)
                set_values.add(line[column] if column else tuple(line))

                if len(set_values) != len_set_values:
                    file_writer.writerow(line)

    int_lines_total = file_reader.line_num
    int_lines_fixed = int_lines_total - len(set_values) - 1
    int_lines_valid = len(set_values) + 1 # header

    print('Read', str(int_lines_total), 'total lines.\n'+\
          str(int_lines_fixed), 'duplicate lines.\n'+\
          str(int_lines_valid), 'lines after cleaning.')

def get_file_delimiter(input_name):
    '''
    Returns character delimiter from file.
    '''
    with open(input_name, 'rt', encoding='utf8') as input_file:
        file_reader = reader(input_file)
        header = str(next(file_reader))

    for i in ['|', '\\t', ';', ',']:
        if i in header: # \\t != \t
            print('Delimiter set as "' + i + '".')
            return i.replace('\\t', '\t')

    return '\n'

if __name__ == "__main__":

    parser = ArgumentParser()

    parser.add_argument('input', action='store', help='input file name')
    parser.add_argument('-o', '--output', action='store', help='output file name')
    parser.add_argument('-c', '--column', action='store', help='column index or title')

    args = parser.parse_args()

    clean_duplicates(args.input,
                     args.output,
                     args.column)