# SIC-XE-assembler

## Usage

```
python main.py <option> <source_file>
```

`-i` or `--intermediate` : Assemble from intermediate file. (Just do pass 2)

## Error code

### pass 1

* -1 : 'Invalid operation code or keyword' error
* -2 : 'Not a format 4 instruction' error
* -3 : 'Duplicated symbol' error
* -4 : 'Invalid instruction format' error

### pass 2 (Still in devlopment)

* -1 : 'Invalid operation code or keyword' error
* -2 : Constant type error
* -3 : 'Constant too big' error
* -4 : 'Can't find the symbol' error
* -5 : 'Invalid format of oprand' error
* -6 : 'Not a format 4 instruction' error
* -7 : 'Out of range of both relative addressing mode' error
* -8 : 'Out of range of program counter relative addressing mode' error
* -9 : 'Out of range of the space of memory' error