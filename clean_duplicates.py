#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Cleans duplicate lines from file by appending line
or field value to a set() and comparing its length.

usage: clean_duplicates [-h] [-o OUTPUT] [-c COLUMN] [-d DELIMITER]
                        [-q {0,1,2,3}] [-e ENCODING] [--index-ignore]
                        input

positional arguments:
  input                 input file name

optional arguments:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        output file name
  -c COLUMN, --column COLUMN
                        column index or title to find duplicate values
  -d DELIMITER, --delimiter DELIMITER
                        column field delimiter
  -q {0,1,2,3}, --quoting {0,1,2,3}
                        text quoting {0: 'minimal', 1: 'all',
                        2: 'non-numeric', 3: 'none'}
  -e ENCODING, --encoding ENCODING
                        file encoding (default: utf-8)
  --index-ignore        bypass IndexError exceptions
'''

from argparse import ArgumentParser
from csv import reader, writer
from os.path import basename, splitext
from sys import stderr

ENCODING = 'utf-8'

QUOTING = {0: 'minimal',
           1: 'all',
           2: 'non-numeric',
           3: 'none'}

def clean_duplicates(input_name, output_name=None,
    column=None, delimiter=None, quoting=0,
    encoding=ENCODING, index_ignore=False):
    '''
    Perform line duplicate removal.
    '''
    set_values = set()

    quotechar = '"'

    if quoting == 3:
        quotechar = ''

    if str(column) == '0':
        print('Error: invalid column (0), must be >= 1.', file=stderr)
        raise SystemExit

    if not output_name:
        name, ext = splitext(basename(input_name))
        output_name = name + '_CLEANED' + ext

    if not delimiter:
        delimiter = get_file_delimiter(input_name, encoding)

    with open(input_name, 'rt', encoding=encoding) as input_file:
        file_reader = reader(input_file, delimiter=delimiter, quoting=quoting)
        header = next(file_reader)

        if isinstance(column, str):

            try: # as index number
                column = int(column)
                if column > len(header):
                    print("Error: invalid column (%s), header has %s columns." % (column, len(header)), file=stderr)
                    raise SystemExit
                column = (column - 1)

            except ValueError: # as title
                if column not in header:
                    print("Error: invalid column ('%s'), not in header: %s." % (column, header), file=stderr)
                    raise SystemExit
                column = header.index(column)

        with open(output_name, 'w', newline='', encoding=encoding) as output_file:
            file_writer = writer(output_file, delimiter=delimiter, quoting=quoting, quotechar=quotechar)
            file_writer.writerow(header)

            for line in file_reader:
                index = file_reader.line_num
                print('Read %s lines.' % index, end='\r')\
                if (index/10000).is_integer() else None

                if line != header:
                    len_set_values = len(set_values)

                    try: # check if duplicate
                        set_values.add(line[column] if column != None else tuple(line))

                        if len(set_values) != len_set_values:
                            file_writer.writerow(line)

                    except IndexError:
                        if index_ignore:
                            continue
                        raise

    int_lines_total = file_reader.line_num
    int_lines_fixed = int_lines_total - len(set_values) - 1
    int_lines_valid = len(set_values) + 1 # header

    print('Read', str(int_lines_total), 'total lines.\n'+\
          str(int_lines_fixed), 'removed lines.\n'+\
          str(int_lines_valid), 'lines after cleaning.')

def get_file_delimiter(input_name, encoding=ENCODING):
    '''
    Returns character delimiter from file.
    '''
    with open(input_name, 'rt', encoding=encoding) as input_file:
        file_reader = reader(input_file)
        header = str(next(file_reader))

    for i in ['|', '\\t', ';', ',']:
        if i in header: # \\t != \t
            return i.replace('\\t', '\t')

    return '\n'

if __name__ == "__main__":

    parser = ArgumentParser()

    parser.add_argument('input', action='store', help='input file name')
    parser.add_argument('-o', '--output', action='store', help='output file name')
    parser.add_argument('-c', '--column', action='store', help='column index or title to find duplicate values')
    parser.add_argument('-d', '--delimiter', action='store', help='column field delimiter')
    parser.add_argument('-q', '--quoting', action='store', type=int, choices=QUOTING.keys(), default=0, help='text quoting %s' % QUOTING)
    parser.add_argument('-e', '--encoding', action='store', help='file encoding (default: %s)' % ENCODING)
    parser.add_argument('--index-ignore', action='store_true', help='bypass IndexError exceptions')

    args = parser.parse_args()

    clean_duplicates(args.input,
                     args.output,
                     args.column,
                     args.delimiter,
                     args.quoting,
                     args.encoding,
                     args.index_ignore)