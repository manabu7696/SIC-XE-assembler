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
                print(f'{asm.lineCounter}\t{format(int(asm.locCounter), 'X').rjust(4,'0')}\t{codeStr.strip('\n')}\t{str(status)}')
                pass1ModifyCode += f'{format(int(asm.locCounter),'X').rjust(4, '0')}\t{codeStr}'
        
            print('\nsymbol info:\n')
            for symbol, content in asm.symbolTable.items():
                    print(f'{symbol}: {content}')
            interFile.write(json.dumps(asm.symbolTable) + '\n')
            interFile.write(pass1ModifyCode)
            print(f'\nprogram length: {hex(asm.programLen)}')

# pass 2 process
def passTwo(intermediateFilePath, isSIC = False):
    asm = assembler.SIC_XE_assembler(isSIC) # initial the assembler
    recordStartingAddr = 0
    objectProgramPath = 'object.txt'
    textRecordBuf = ''
    modRecordBuf = ''
    modLen = 5
    isValPrevious = False
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
                    print(f'{asm.lineCounter - 1}\t{codeStr.strip()}\t\t{asm.objectCode}')
                    if asm.isVariable:
                        if isValPrevious:
                            continue
                        else:
                            objFile.write(f'T{format(recordStartingAddr, 'X').rjust(6, '0')}{format(len(textRecordBuf)//2, 'X').rjust(2, '0')}{textRecordBuf}\n')
                            textRecordBuf = ''
                            recordStartingAddr = 0
                            isValPrevious = True
                    elif len(textRecordBuf + asm.objectCode) > 60 and len(textRecordBuf) < 60:
                        objFile.write(f'T{format(recordStartingAddr, 'X').rjust(6, '0')}{format(len(textRecordBuf)//2, 'X').rjust(2, '0')}{textRecordBuf}\n')
                        textRecordBuf = asm.objectCode
                        recordStartingAddr = asm.locCounter
                    elif len(textRecordBuf + asm.objectCode) == 60 :
                        textRecordBuf += asm.objectCode
                        objFile.write(f'T{format(recordStartingAddr, 'X').rjust(6, '0')}{format(len(textRecordBuf)//2, 'X').rjust(2, '0')}{textRecordBuf}\n')
                        textRecordBuf = ''
                    elif len(textRecordBuf + asm.objectCode) < 60 and len(textRecordBuf) < 60:
                        if textRecordBuf == '':
                            recordStartingAddr = asm.locCounter
                        if isValPrevious:
                            recordStartingAddr = asm.locCounter
                            isValPrevious = False
                        textRecordBuf += asm.objectCode
                                
                    if asm.isNeedReloc:
                        modRecordBuf += f'M{format(asm.locCounter + 1, 'X').rjust(6, '0')}{format(modLen, 'X').rjust(2, '0')}\n'
                elif status == 3:
                    print(f'{asm.lineCounter - 1}\t{codeStr}')
                    objFile.write(f'T{format(recordStartingAddr, 'X').rjust(6, '0')}{format(len(textRecordBuf)//2, 'X').rjust(2, '0')}{textRecordBuf}\n')
                    objFile.write(modRecordBuf)
                    objFile.write(f'E{asm.objectCode}')
                else:
                    print(f'{asm.lineCounter - 1}\t{codeStr.strip()}\t{asm.objectCode}\t{status}')


def main(argvList):
    if argvList[1] == '-i' or argvList[1] == '--intermediate':
        passTwo(argvList[2])
    elif argvList[1] == '-c' or argvList[1] == '--sic':
        passOne(argvList[2])
        passTwo(os.path.join('cache', 'intermediate.txt'), isSIC=True)
    elif argvList[1] == '-s' or argvList[1] == '--symbol':
        passOne(argvList[2])
    else:
        passOne(argvList[1])
        passTwo(os.path.join('cache', 'intermediate.txt'))

main(sys.argv)