import dataModel, json

def twosComplement(n):
    return 2 ** 12 + n

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
        valueList = []
        for char in constant:
            valueList.append(format(ord(char), 'X'))
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
        return format(value, 'X').rjust(6, '0')

    
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
        self.isSIC = False
        self.base = None
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
                    value = self.symbolTable['reg'].get(symbol, -4)
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
                    value = int(self.symbolTable.get(symbol, '-4'), 16)
                    if value == -4:
                        value = 0
                        self.errFlag = -4
                    oprandValue.append(value)
        return oprandValue

    def assemble(self, mnemonic, oprand = []):
        if self.isSIC:
            indirect = 0
            immediate = 0
            index = 0
            relativeBase = 0
            relativePC = 0
            extend = 0
        else:
            indirect = 1
            immediate = 1
            index = 0
            relativeBase = 0
            relativePC = 0
            extend = 0
            needRelative = True
            if mnemonic.startswith('+'):
                addr = 0
                mnemonic = mnemonic.strip('+')
                if dataModel.getInstructionFormat(mnemonic) == '3/4':
                    extend = 1
                    needRelative = False
                    if len(oprand) == 1:
                        if oprand[0].startswith('@'):
                            immediate = 0
                            oprand[0] = oprand[0].strip('@')
                            oprandTemp = self.oprandProcess('3/4', oprand)
                            if self.errFlag == -4:
                                addr = int(oprand[0])
                                self.errFlag = 0
                            else:
                                addr = oprandTemp[0]
                        elif oprand[0].startswith('#'):
                            indirect = 0
                            oprand[0] = oprand[0].strip('#')
                            oprandTemp = self.oprandProcess('3/4', oprand)
                            if self.errFlag == -4:
                                addr = int(oprand[0])
                                self.errFlag = 0
                            else:
                                addr = oprandTemp[0]
                        else:
                            oprandTemp = self.oprandProcess('3/4', oprand)
                            if self.errFlag == -4:
                                addr = int(oprand[0])
                                self.errFlag = 0
                            else:
                                addr = oprandTemp[0]
                    elif len(oprand) == 2 and oprand[1] == 'X':
                        index = 1
                        oprandTemp = self.oprandProcess('3/4', [oprand[0]])
                        if self.errFlag == -4:
                            addr = int(oprand[0])
                            self.errFlag = 0
                        else:
                            addr = oprandTemp[0]
                    else:
                        return -5
                    if addr >= 2 ** 20:
                        return -9
                    return format(dataModel.getOpCode(mnemonic) * 2 ** 24 + indirect * 2 ** 25 + immediate * 2 ** 24 + index * 2 ** 23 + relativeBase * 2 ** 22 + relativePC * 2 ** 21 + extend * 2 ** 20 + addr, 'X').rjust(8, '0')
                else:
                    return -6
            else:
                if dataModel.getInstructionInfo(mnemonic) == -1:
                    if mnemonic == 'BYTE':
                        return byteConvert(oprand[0])
                    elif mnemonic == 'WORD':
                        return wordConvert(oprand[0])
                    else:
                        return -1
                else:
                    if dataModel.getInstructionFormat(mnemonic) == '1':
                        if len(oprand) == dataModel.getArgumentAmount(mnemonic):
                            return format(dataModel.getOpCode(mnemonic), 'X')
                        else:
                            return -5
                    elif dataModel.getInstructionFormat(mnemonic) == '2':
                        if len(oprand) == dataModel.getArgumentAmount(mnemonic):
                            oprand = self.oprandProcess('2', oprand)
                            return format(dataModel.getOpCode(mnemonic) * 0x100 + oprand[0] * 0x10 + oprand[1], 'X')
                        else:
                            return -5
                    elif dataModel.getInstructionFormat(mnemonic) == '3/4':
                        if len(oprand) == 1:
                            if oprand[0].startswith('@'):
                                immediate = 0
                                oprand[0] = oprand[0].strip('@')
                                oprandTemp = self.oprandProcess('3/4', oprand)
                                if self.errFlag == -4:
                                    offset = int(oprand[0])
                                    self.errFlag = 0
                                    needRelative = False
                                else:
                                    oprand = oprandTemp[0]
                            elif oprand[0].startswith('#'):
                                indirect = 0
                                oprand[0] = oprand[0].strip('#')
                                oprandTemp = self.oprandProcess('3/4', oprand)
                                if self.errFlag == -4:
                                    offset = int(oprand[0])
                                    self.errFlag = 0
                                    needRelative = False
                                else:
                                    oprand = oprandTemp[0]
                            else:
                                oprandTemp = self.oprandProcess('3/4', oprand)
                                if self.errFlag == -4:
                                    offset = int(oprand[0])
                                    self.errFlag = 0
                                    needRelative = False
                                else:
                                    oprand = oprandTemp[0]
                        elif len(oprand) == 2 and oprand[1] == 'X':
                            index = 1
                            oprandTemp = self.oprandProcess('3/4', [oprand[0]])
                            if self.errFlag == -4:
                                offset = int(oprand[0])
                                self.errFlag = 0
                                needRelative = False
                            else:
                                oprand = oprandTemp[0]
                        else:
                            needRelative = False
                            offset = 0
                        if needRelative:
                            self.nextLocCounter = self.locCounter + instructionLen(mnemonic)
                            PCoffset = oprand - self.nextLocCounter
                            if -2048 <= PCoffset < 2048:
                                relativePC = 1
                                if PCoffset < 0:
                                    PCoffset = twosComplement(PCoffset)
                                offset = PCoffset
                            elif type(self.base) == int:
                                baseOffset = oprand - self.base
                                if 0 <= baseOffset < 4096:
                                    relativeBase = 1
                                    offset = baseOffset
                                else:
                                    return -7
                            else:
                                return -8
                        return format(dataModel.getOpCode(mnemonic) * 2 ** 16 + indirect * 2 ** 17 + immediate * 2 ** 16 + index * 2 ** 15 + relativeBase * 2 ** 14 + relativePC * 2 ** 13 + extend * 2 ** 12 + offset, 'X').rjust(6, '0')
                    
    def passTwoParser(self, codeStr):
        self.objectCode = ''
        self.lineCounter += 1
        if self.lineCounter == 1 and codeStr.startswith('{'):
            self.symbolTable = json.loads(codeStr)
            return 0
        else:
            self.codeList = codeStr.split()
            self.locCounter = int(self.codeList[0], 16)
            if self.lineCounter == 2 and len(self.codeList) == 4 and self.codeList[2] == 'START':
                self.objectCode = f'{self.codeList[1].ljust(6)}{self.codeList[3].rjust(6, '0')}{self.symbolTable['programLen'].strip('0x').rjust(6, '0')}'
                return 1
            elif self.codeList[1] == 'END':
                self.objectCode = f'{self.symbolTable[self.codeList[2]].strip('0x').rjust(6, '0')}'
                return 3
            else:
                if '.' not in self.codeList: # not a comment
                    if len(self.codeList) == 4:
                        if self.codeList[2] == 'RESW' or self.codeList[2] == 'RESB':
                            self.objectCode = ''
                        else:
                            oprand = self.codeList[3].split(',')
                            result = self.assemble(self.codeList[2], oprand)
                            if isinstance(result, int):
                                return result
                            else:
                                self.objectCode = result
                    elif len(self.codeList) == 3:
                        oprand = self.codeList[2].split(',')
                        if self.codeList[1] == 'BASE':
                            self.base = self.oprandProcess('3/4', oprand)[0]
                        else:
                            result = self.assemble(self.codeList[1], oprand)
                            if isinstance(result, int):
                                return result
                            else:
                                self.objectCode = result
                    elif len(self.codeList) == 2:
                        result = self.assemble(self.codeList[1])
                        if isinstance(result, int):
                            return result
                        else:
                            self.objectCode = self.assemble(self.codeList[1])
                return 2