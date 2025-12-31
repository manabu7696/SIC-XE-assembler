# opcodeTable，格式如下：<mnemonic>: [<instruction_format>, <argument_amount>, <object_code>]
OPCODE_TABLE = {'ADD': ['3/4', 1, 0x18],
                'ADDF': ['3/4', 1, 0x58],
                'ADDR': ['2', 2, 0x90],
                'AND': ['3/4', 1, 0x40],
                'CLEAR': ['2', 1, 0xb4],
                'COMP': ['3/4', 1, 0x28],
                'COMPF': ['3/4', 1, 0x88],
                'COMPR': ['2', 2, 0xa0],
                'DIV': ['3/4', 1, 0x24],
                'DIVF': ['3/4', 1, 0x64],
                'DIVR': ['2', 2, 0x9c],
                'FIX': ['1', 0, 0xc4],
                'FLOAT': ['1', 0, 0xc0],
                'HIO': ['1', 0, 0xf4],
                'J': ['3/4', 1, 0x3c],
                'JEQ': ['3/4', 1, 0x30],
                'JGT': ['3/4', 1, 0x34],
                'JLT': ['3/4', 1, 0x38],
                'JSUB': ['3/4', 1, 0x48],
                'LDA': ['3/4', 1, 0x00],
                'LDB': ['3/4', 1, 0x68],
                'LDCH': ['3/4', 1, 0x50],
                'LDF': ['3/4', 1, 0x70],
                'LDL': ['3/4', 1, 0x08],
                'LDS': ['3/4', 1, 0x6c],
                'LDT': ['3/4', 1, 0x74],
                'LDX': ['3/4', 1, 0x04],
                'LPS': ['3/4', 1, 0xd0],
                'MUL': ['3/4', 1, 0x20],
                'MULF': ['3/4', 1, 0x60],
                'MULR': ['2', 2, 0x98],
                'NORM': ['1', 0, 0xc8],
                'OR': ['3/4', 1, 0x44],
                'RD': ['3/4', 1, 0xd8],
                'RMO': ['2', 2, 0xac],
                'RSUB': ['3/4', 0, 0x4c],
                'SHIFTL': ['2', 2, 0xa4],
                'SHIFTR': ['2', 2, 0xa8],
                'SIO': ['1', 0, 0xf0],
                'SSK': ['3/4', 1, 0xec],
                'STA': ['3/4', 1, 0x0c],
                'STB': ['3/4', 1, 0x78],
                'STCH': ['3/4', 1, 0x54],
                'STF': ['3/4', 1, 0x80],
                'STI': ['3/4', 1, 0xd4],
                'STL': ['3/4', 1, 0x14],
                'STS': ['3/4', 1, 0x7c],
                'STSW': ['3/4', 1, 0xe8],
                'STT': ['3/4', 1, 0x84],
                'STX': ['3/4', 1, 0x10],
                'SUB': ['3/4', 1, 0x1c],
                'SUBF': ['3/4', 1, 0x5c],
                'SUBR': ['2', 2, 0x94],
                'SVC': ['2', 1, 0xb0],
                'TD': ['3/4', 1, 0xe0],
                'TIO': ['1', 0, 0xf8],
                'TIX': ['3/4', 1, 0x2c],
                'TIXR': ['2', 1, 0xb8],
                'WD': ['3/4', 1, 0xdc]}

# 定義取得instruction資訊的函數
def getInstructionInfo(mnemonic):
    if mnemonic not in OPCODE_TABLE:
        return -1 # not in opcode table error
    return {'instruction_format': OPCODE_TABLE[mnemonic][0], 'argument_amount': OPCODE_TABLE[mnemonic][1], 'object_code': OPCODE_TABLE[mnemonic][2]}

def getInstructionFormat(mnemonic):
    if mnemonic not in OPCODE_TABLE:
        return -1 # not in opcode table
    return OPCODE_TABLE[mnemonic][0]

def getArgumentAmount(mnemonic):
    if mnemonic not in OPCODE_TABLE:
        return -1 # not in opcode table 
    return OPCODE_TABLE[mnemonic][1]

def getOpCode(mnemonic):
    if mnemonic not in OPCODE_TABLE:
        return -1 # not in opcode table 
    return OPCODE_TABLE[mnemonic][2]

# 定義每個register助憶詞對應數字
REGISTER_SYMBOL_TABLE = {'A': 0, 'X': 1, 'L': 2, 'B': 3, 'S': 4, 'T': 5, 'F': 6, 'PC': 8, 'SW': 9}
