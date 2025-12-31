import dataModel

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

def dataLocCounter(keyword, oprand, loc):
    if dataLen(keyword, oprand) == -1:
        return -1 # not a valid keyword
    else:
        return loc + dataLen(keyword, oprand)



class SIC_XE_assembler:
    def __init__(self):
        self.symbolTable = {}
        self.symbolTable['reg'] = dataModel.REGISTER_SYMBOL_TABLE
        self.nextLocCounter = 0 # set the default nextLoc 
    def passOneParser(self, codeStr, i):
        self.codeList = codeStr.split() # split the source code

        # if line 1 is under specific format(XXXX START <start_address>), do the corresponding process
        if i == 1 and len(self.codeList) == 3 and self.codeList[1] == 'START':
            self.symbolTable['start'] = int(self.codeList[2],16) # save the start address
            self.locCounter = self.symbolTable['start']
            self.nextLocCounter = self.locCounter # initial the loc and nextLoc
        
        # other cases
        else:
            self.locCounter = self.nextLocCounter 

            # if it is the end line, caculate the programLen
            if self.codeList[0] == 'END':
                self.programLen = self.locCounter - self.symbolTable['start']
            
            else:
                if '.' not in self.codeList: # not a comment
                    if len(self.codeList) == 3:
                        if self.codeList[0] in self.symbolTable:
                            return -3 # duplicate symbol
                        else:
                            self.symbolTable[self.codeList[0]] = self.locCounter
                        if instructionLen(self.codeList[1]) == -1:
                            if dataLocCounter(self.codeList[1], self.codeList[2], self.locCounter) == -1:
                                return -1 # not a valid keyword 
                            else:
                                self.nextLocCounter = dataLocCounter(self.codeList[1], self.codeList[2], self.locCounter)
                        elif instructionLen(self.codeList[1]) == -2:
                            return -2
                        else:
                            self.nextLocCounter = self.locCounter + instructionLen(self.codeList[1])
                    elif len(self.codeList) == 2:
                        if instructionLen(self.codeList[0]) == -1:
                            if dataLocCounter(self.codeList[0], self.codeList[1], self.locCounter) == -1:
                                return -1 # not a valid keyword 
                            else:
                                self.nextLocCounter = dataLocCounter(self.codeList[0], self.codeList[1], self.locCounter)
                        elif instructionLen(self.codeList[0]) == -2:
                            return -2 # not a format 4 instruction
                        else:
                            self.nextLocCounter = self.locCounter + instructionLen(self.codeList[0])
                    elif len(self.codeList) == 1:
                        if instructionLen(self.codeList[0]) == -1:
                            return -1 # invalid operation code
                        elif instructionLen(self.codeList[0]) == -2:
                            return -2 # not a format 4 instruction
                        else:
                            self.nextLocCounter = self.locCounter + instructionLen(self.codeList[0])
                    else:
                        return -4 # invalid instruction format
