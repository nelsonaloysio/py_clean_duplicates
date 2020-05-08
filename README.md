py_clean_duplicates
---

Cleans duplicate lines from file by appending line
or field value to a set() and comparing its length.

```
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
  --output-ignored      lines with IndexError to another file
```