import assembler, os, sys, json

# pass 1 process
def passOne(sourceFilePath):
    asm = assembler.SIC_XE_assembler() # initial the assembler

    cacheFolderPath = 'cache'
    intermediateFilePath = os.path.join(cacheFolderPath, 'intermediate.txt')
    os.makedirs(cacheFolderPath, exist_ok=True)
    pass1ModifyCode = ''

    with open(sourceFilePath,'r') as f:
        with open(intermediateFilePath, 'w') as interFile:
            print('Pass 1')
            print('line\tloc\tsource code\toperand\t\terror code\n')

            # pass 1 
            while True:
                codeStr = f.readline()
                if codeStr == '':
                    break
                status = asm.passOneParser(codeStr)
                if status == None:
                    status = ''
                print(f'{asm.lineCounter}\t{hex(int(asm.locCounter))}\t{codeStr.strip('\n')}\t{str(status)}')
                pass1ModifyCode += f'{hex(int(asm.locCounter))}\t{codeStr}'
        
            print('\nsymbol info:\n')
            for symbol, content in asm.symbolTable.items():
                    print(f'{symbol}: {content}')
            interFile.write(json.dumps(asm.symbolTable) + '\n')
            interFile.write(pass1ModifyCode)
            print(f'\nprogram length: {hex(asm.programLen)}')

# pass 2 process
def passTwo(intermediateFilePath):
    asm = assembler.SIC_XE_assembler() # initial the assembler

    objectProgramPath = 'object.txt'

    with open(intermediateFilePath, 'r') as f:
        with open(objectProgramPath, 'w') as objFile:
            print('Pass 2')
            print('line\tloc\tsource code\toperand\t\tobject code')

            # pass 2
            while True:
                codeStr = f.readline()
                if codeStr == '':
                    break
                status = asm.passTwoParser(codeStr)
                if status == 0:
                    continue
                elif status == 1:
                    print(f'{asm.lineCounter - 1}\t{codeStr.strip()}')
                    objFile.write(f'H{asm.objectCode}\n')
                elif status == 2:
                    print(f'{asm.lineCounter - 1}\t{codeStr.strip('\n')}{asm.objectCode}')
                elif status == 3:
                    print(f'{asm.lineCounter - 1}\t{codeStr}')
                    objFile.write(f'E{asm.objectCode}')
                else:
                    print(f'{asm.lineCounter - 1}\t{codeStr.strip()}\t{asm.objectCode}\t{status}')


def main(argvList):
    if argvList[1] == '-i' or argvList[1] == '--intermediate':
        passTwo(argvList[2])
    else:
        passOne(argvList[1])
        passTwo(os.path.join('cache', 'intermediate.txt'))

main(sys.argv)