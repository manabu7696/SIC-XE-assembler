import dataModel, json

def instructionLen(opcode):
    # deal the format 4 instruction
    if opcode.startswith('+'):
        opcode = opcode.strip('+')
        if dataModel.getInstructionFormat(opcode) == '3/4':
            return 4
        else:
            return -2 # 'not a format 4 instruction' error
    else:
        # format 1
        if dataModel.getInstructionFormat(opcode) == '1':
            return 1
        
        # format 2
        elif dataModel.getInstructionFormat(opcode) == '2':
            return 2
        
        # format 3
        elif dataModel.getInstructionFormat(opcode) == '3/4':
            return 3
        
        # deal the 'not in opcode table' case
        elif dataModel.getInstructionFormat(opcode) == -1:
            return -1 # not a valid instruction 

def constantLen(constant):
    # deal 'char' type constant
    if constant.startswith('C'):
        constant = constant.strip("C''")
        return int(len(constant))
    # deal 'hex' type constant
    elif constant.startswith('X'):
        constant = constant.strip("X''")
        return int(len(constant)/2)
    
def byteConvert(constant):
    # deal 'char' type constant
    if constant.startswith('C'):
        constant = constant.strip("C''")
        constantList = constant.split('')
        valueList = []
        for char in constantList:
            valueList.append(hex(ord(char)))
        value = ''.join(valueList)
        return value
    # deal 'hex' type constant
    elif constant.startswith('X'):
        constant = constant.strip("X''")
        return constant
    else:
        return -2 # constant type error
    
def wordConvert(constant):
    value = int(constant)
    if value > 0xffffff:
        return -3 # constant too big error
    else:
        return hex(value).strip('0x').rjust(6, '0')

    
def dataLen(keyword, oprand):
    if keyword == 'WORD':
        return 3
    elif keyword == 'RESW':
        return 3 * int(oprand)
    elif keyword == 'RESB':
        return int(oprand)
    elif keyword == 'BYTE':
        return constantLen(oprand)
    else:
        return -1 # not a valid keyword

def lenCalc(keyword, oprand = ''):
    if oprand == '':
            return instructionLen(keyword)
    else:
        if instructionLen(keyword) == -1:
            return dataLen(keyword, oprand)
        else:
            return instructionLen(keyword)

class SIC_XE_assembler:
    def __init__(self):
        self.symbolTable = {}
        self.symbolTable['reg'] = dataModel.REGISTER_SYMBOL_TABLE
        self.lineCounter = 0
        self.nextLocCounter = 0 # set the default nextLoc
        self.objectCode = ''
        self.errFlag = 0
    
    def passOneParser(self, codeStr):
        self.lineCounter += 1
        self.codeList = codeStr.split() # split the source code

        # if line 1 is under specific format(XXXX START <start_address>), do the corresponding process
        if self.lineCounter == 1 and len(self.codeList) == 3 and self.codeList[1] == 'START':
            self.symbolTable['start'] = hex(int(self.codeList[2])) # save the start address
            self.locCounter = int(self.symbolTable['start'], 16)
            self.nextLocCounter = self.locCounter # initial the loc and nextLoc
        
        # other cases
        else:
            self.locCounter = self.nextLocCounter # update the locCounter 

            # if it is the end line, caculate the programLen
            if self.codeList[0] == 'END':
                self.programLen = self.locCounter - int(self.symbolTable['start'], 16)
                self.symbolTable['programLen'] = hex(self.programLen)
            
            else:
                if '.' not in self.codeList: # not a comment
                    if len(self.codeList) == 3:
                        if self.codeList[0] in self.symbolTable:
                            return -3 # duplicate symbol
                        else:
                            self.symbolTable[self.codeList[0]] = hex(self.locCounter)
                        if lenCalc(self.codeList[1], self.codeList[2]) < 0:
                            return lenCalc(self.codeList[1], self.codeList[2])
                        else:
                            self.nextLocCounter = self.locCounter + lenCalc(self.codeList[1], self.codeList[2])
                    elif len(self.codeList) == 2:
                        if lenCalc(self.codeList[0], self.codeList[1]) < 0:
                            return lenCalc(self.codeList[0], self.codeList[1])
                        else:
                            self.nextLocCounter = self.locCounter + lenCalc(self.codeList[0], self.codeList[1])
                    elif len(self.codeList) == 1:
                        if lenCalc(self.codeList[0]) < 0:
                            return lenCalc(self.codeList[0])
                        else:
                            self.nextLocCounter = self.locCounter + lenCalc(self.codeList[0])
                    else:
                        return -4 # invalid instruction format
    
    def oprandProcess(self, format, oprand = []):
        oprandValue = []
        if format == '2':
            if oprand == []:
                oprandValue = [0]
            else:
                for symbol in oprand:
                    value = int(self.symbolTable['reg'].get(symbol, '-4'), 16)
                    if value == -4:
                        value = 0
                        self.errFlag = -4
                    oprandValue.append(value)
                if len(oprandValue) == 1:
                    oprandValue.append(0)
        elif format == '3/4':
            if oprand == []:
                oprandValue = [0]
            else:
                for symbol in oprand:
                    value = int(self.symbolTable.get(symbol, -4), 16)
                    if value == -4:
                        value = 0
                        self.errFlag = -4
                    oprandValue.append(value)
        return oprandValue

    def assemble(self, mnemonic, oprand = []):
        if mnemonic.startswith('+'):
            mnemonic = mnemonic.strip('+')
            if dataModel.getInstructionFormat(mnemonic) == '3/4':
                if len(oprand) == dataModel.getArgumentAmount(mnemonic):
                    oprand = self.oprandProcess('3/4', oprand)
                    
                else:
                    return -5
            else:
                return -6
        else:
            if dataModel.getInstructionInfo(mnemonic) == -1:
                if mnemonic == 'BYTE':
                    return byteConvert(oprand)
                elif mnemonic == 'WORD':
                    return wordConvert(oprand)
                else:
                    return -1
            else:
                if len(oprand) == dataModel.getArgumentAmount(mnemonic):
                    if dataModel.getInstructionFormat(mnemonic) == '1':
                        return hex(dataModel.getOpCode(mnemonic)).strip('0x')
                    elif dataModel.getInstructionFormat(mnemonic) == '2':
                        oprand = self.oprandProcess('2', oprand)
                        return hex(dataModel.getOpCode(mnemonic) * 0x100 + oprand[0] * 0x10 + oprand[1]).strip('0x')
                    elif dataModel.getInstructionFormat(mnemonic) == '3/4':
                        if
                    
                else:
                    return -5

    def passTwoParser(self, codeStr):
        self.lineCounter += 1
        if self.lineCounter == 1 and codeStr.startswith('{'):
            self.symbolTable = json.loads(codeStr)
        else:
            self.codeList = codeStr.split()
            if self.lineCounter == 2 and len(self.codeList) == 4 and self.codeList[2] == 'START':
                self.objectCode = f'{self.codeList[1].ljust(6)}{self.codeList[3].rjust(6, '0')}{self.symbolTable['programLen'].strip('0x').rjust(6, '0')}'
                return 1
            elif self.codeList[1] == 'END':
                self.objectCode = f'{self.symbolTable[self.codeList[2]].strip('0x').rjust(6, '0')}'
                return 3
            else:
                if '.' not in self.codeList: # not a comment
                    if len(self.codeList) == 4:
                        