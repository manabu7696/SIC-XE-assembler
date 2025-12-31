import assembler, sys
i = 0

with open(sys.argv[1],'r') as f:

    asm = assembler.SIC_XE_assembler() # initial the assembler

    print('loc\tsource code\toperand\t\t\t\t\terror code\n')

    # pass 1 
    while True:
        codeStr = f.readline()
        if codeStr == '':
            break
        i += 1
        status = asm.passOneParser(codeStr, i)
        if status == None:
            status = ''
        print(str(hex(int(asm.locCounter))) + '\t' + codeStr.strip('\n') + '\t\t\t' + str(status))
    
    print('\nsymbol info:\n')

    for symbol, content in asm.symbolTable.items():
        if type(content) == type({}):
            print(f'{symbol}: {content}')
        else:
            print(f'{symbol}: {hex(content)}')
    
    print(f'\nprogram length: {hex(asm.programLen)}')