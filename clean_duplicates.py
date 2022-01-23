#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Cleans duplicate lines from file by appending line
or field value to a set() and comparing its length.

usage: clean_duplicates [-h] [-o OUTPUT_NAME] [-c COLUMN] [-d DELIMITER]
                        [-q {0,1,2,3}] [-e ENCODING] [-v]
                        [--consider-index-errors]
                        [--dump-index-errors OUTPUT_ERRORS_NAME]
                        [--max-field-size]
                        input_name

positional arguments:
  input_name            input file name

optional arguments:
  -h, --help            show this help message and exit
  -o OUTPUT_NAME, --output-name OUTPUT_NAME
                        output file name
  -c COLUMN, --column COLUMN
                        column index or title to find duplicate values
  -d DELIMITER, --delimiter DELIMITER
                        column field delimiter
  -q {0,1,2,3}, --quoting {0,1,2,3}
                        text quoting {0: 'minimal', 1: 'all', 2: 'non-
                        numeric', 3: 'none'}
  -e ENCODING, --encoding ENCODING
                        file encoding (default: utf-8)
  -v, --invert          invert matches to return duplicates only
  --consider-index-errors
                        write lines with IndexError to output file
  --dump-index-errors OUTPUT_ERRORS_NAME
                        write lines with IndexError to another file
  --max-field-size      extend field size limit to maximum allowed
'''

from argparse import ArgumentParser
from csv import field_size_limit, reader, writer
from os.path import basename,splitext
from sys import maxsize, stderr

ENCODING = 'utf-8'

QUOTING = {0: 'minimal',
           1: 'all',
           2: 'non-numeric',
           3: 'none'}

def clean_duplicates(
    input_name,
    column=None,
    consider_index_errors=False,
    delimiter=None,
    encoding=ENCODING,
    header=True,
    invert=False,
    max_field_size=False,
    output_errors_name=None,
    output_name=None,
    quoting=0,
) -> None:
    '''
    Perform line duplicate removal.
    '''
    int_errors = 0
    set_values = set()
    quotechar = '"'

    if quoting == 3:
        quotechar = ''

    if str(column) == '0':
        print('Error: invalid column (0), must be >= 1.', file=stderr)
        raise SystemExit

    if max_field_size:
        max_field_size_limit()

    if not delimiter:
        delimiter = get_file_delimiter(input_name, encoding)

    if not output_name:
        name, ext = splitext(basename(input_name))
        output_name = name + '_CLEANED' + ext
    output_errors_name = output_errors_name or output_name

    with open(input_name, 'rt', encoding=encoding) as input_file:
        file_reader = reader(input_file, delimiter=delimiter, quoting=quoting, quotechar=quotechar)
        header = next(file_reader)
        column = get_header_index(header, column)

        with open(output_name, 'w', newline='', encoding=encoding) as output_file:
            file_writer = writer(output_file, delimiter=delimiter, quoting=quoting, quotechar=quotechar)
            file_writer.writerow(header)

            with open(output_errors_name, 'w', newline='', encoding=encoding) as errors_file:
                error_writer = writer(errors_file, delimiter=delimiter, quoting=quoting, quotechar=quotechar)

                for line in file_reader:
                    print(f'Read {file_reader.line_num} lines.', end='\r')\
                    if (file_reader.line_num/10000).is_integer() else None

                    if line != header:
                        len_set_values = len(set_values)

                        try: # check if duplicate
                            set_values.add(line[column] if column != None else tuple(line))

                            if (len(set_values) == len_set_values and invert)\
                            or (len(set_values) != len_set_values and not invert):
                                file_writer.writerow(line)

                        except IndexError as e:
                            print(f'Warning: IndexError on line {file_reader.line_num}.', file=stderr)
                            int_errors += 1

                            if consider_index_errors:
                                file_writer.writerow(line)

                            if output_errors_name != output_name:
                                error_writer.writerow(header) if int_errors == 1 else None
                                error_writer.writerow(line)

    print(f'Read {file_reader.line_num} total lines.' +
          f'\n{file_reader.line_num - len(set_values) - (int_errors if consider_index_errors else 0) - 1} invalid lines.' +
          f'\n{len(set_values) + (int_errors if consider_index_errors else 0) + 1} lines after cleaning.')

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

def get_header_index(header, column=None):
    '''
    Returns index number from column in header if string.
    '''
    if column:
        try: # as index number
            column = int(column)
            if column > len(header):
                print(f"Error: invalid column ('{column}'), header has {len(header)} columns.", file=stderr)
                raise SystemExit
            column = (column - 1)

        except ValueError: # as title
            if column not in header:
                print(f"Error: invalid column ('{column}'), not in header: {header}.", file=stderr)
                raise SystemExit
            column = header.index(column)

    return column

def max_field_size_limit(d=10):
    '''
    Extend the maximum allowed field size to
    work around field limit errors reading files.
    '''
    max_size = int(maxsize)

    while True:
        max_size = int(max_size/d)
        try:
            field_size_limit(max_size)
        except OverflowError:
            pass
        else:
            return

if __name__ == "__main__":

    parser = ArgumentParser()

    parser.add_argument('input_name', action='store', help='input file name')
    parser.add_argument('-o', '--output-name', action='store', help='output file name')
    parser.add_argument('-c', '--column', action='store', help='column index or title to find duplicate values')
    parser.add_argument('-d', '--delimiter', action='store', help='column field delimiter')
    parser.add_argument('-q', '--quoting', action='store', type=int, choices=QUOTING.keys(), default=0, help='text quoting %s' % QUOTING)
    parser.add_argument('-e', '--encoding', action='store', help='file encoding (default: %s)' % ENCODING)
    parser.add_argument('-v', '--invert', action='store_true', help='invert matches to return duplicates only')
    parser.add_argument('--consider-index-errors', action='store_true', help='write lines with IndexError to output file')
    parser.add_argument('--dump-index-errors', action='store', dest='output_errors_name', help='write lines with IndexError to another file')
    parser.add_argument('--max-field-size', action='store_true', help='extend field size limit to maximum allowed')

    args = parser.parse_args()

    clean_duplicates(**vars(args))