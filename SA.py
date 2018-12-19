R0 = 0
R1 = 1
R2 = 2
R3 = 3

DI_AD_MODE = 0
IN_AD_MODE = 1
RI_AD_MODE = 2
PC_AD_MODE = 3

UNKNOWN_SYM = False

def REG(x):
    if x == 'R0':
        return R0 
    if x == 'R1':
        return R1 
    if x == 'R2':
        return R2 
    if x == 'R3':
        return R3
    raise Exception("Invalid reg")

def INT(x):
    return int('0x' + x[:-1], 16)

def HEX(x):
    return ('%2X'%(x)).replace(' ','0')

def MOV(line):
    (RD, RS) = line.split(',')
    (RD, RS) = (REG(RD), REG(RS))
    return hex((0b0100 << 4) + (RS << 2) + RD)[2:]

def ADD(line):
    (RD, RS) = line.split(',')
    (RD, RS) = (REG(RD), REG(RS))
    return '0' + hex((0b0000 << 4) + (RS << 2) + RD)[2:]

def SUB(line):
    (RD, RS) = line.split(',')
    (RD, RS) = (REG(RD), REG(RS))
    return hex((0b1000 << 4) + (RS << 2) + RD)[2:]

def AND(line):
    (RD, RS) = line.split(',')
    (RD, RS) = (REG(RD), REG(RS))
    return hex((0b0001 << 4) + (RS << 2) + RD)[2:]

def OR(line):
    (RD, RS) = line.split(',')
    (RD, RS) = (REG(RD), REG(RS))
    return hex((0b1001 << 4) + (RS << 2) + RD)[2:]

def RR(line):
    (RD, RS) = line.split(',')
    (RD, RS) = (REG(RD), REG(RS))
    return hex((0b1010 << 4) + (RS << 2) + RD)[2:]

def INC(line):
    RD = REG(line)
    return hex((0b0111 << 4) + (0 << 2) + RD)[2:]

def HLT():
    return hex((0b0101 << 4) + (0 << 2) + 0)[2:]

def LAD(line):
    line = line.split(',')
    if len(line) == 2:
        if line[1][0] == '[' and line[1][-1] == ']':
            MODE = IN_AD_MODE
            AD = INT(line[1][1:-1])
        else:
            MODE = DI_AD_MODE
            AD = INT(line[1])
        RD = REG(line[0])
    else:
        MODE = RI_AD_MODE
        (RD, AD) = (REG(line[0]), INT(line[2]))
    return [hex((0b1100 << 4) + (MODE << 2) + RD)[2:], HEX(AD)]

def STA(line):
    line = line.split(',')
    if len(line) == 2:
        if line[0][0] == '[' and line[0][-1] == ']':
            MODE = IN_AD_MODE
            AD = INT(line[0][1:-1])
        else:
            MODE = DI_AD_MODE
            AD = INT(line[0])
        RD = REG(line[1])
    else:
        MODE = RI_AD_MODE
        (RD, AD) = (REG(line[1]), INT(line[2]))
    return [hex((0b1101 << 4) + (MODE << 2) + RD)[2:], HEX(AD)]

def JMP(line):
    line = line.split(',')
    if len(line) == 1:
        if line[0][0] == '[' and line[0][-1] == ']':
            MODE = IN_AD_MODE
            AD = INT(line[0][1:-1])
        else:
            MODE = DI_AD_MODE
            AD = INT(line[0])
    else:
        MODE = RI_AD_MODE 
        AD = INT(line[1])
    return [hex((0b1110 << 4) + (MODE << 2) + 0)[2:], HEX(AD)]

def BZC(line):
    line = line.split(',')
    if len(line) == 1:
        if line[0][0] == '[' and line[0][-1] == ']':
            MODE = IN_AD_MODE
            AD = INT(line[0][1:-1])
        else:
            MODE = DI_AD_MODE
            AD = INT(line[0])
    else:
        MODE = RI_AD_MODE 
        AD = INT(line[1])
    return [hex((0b1111 << 4) + (MODE << 2) + 0)[2:], HEX(AD)]

def IN(line):
    (RD, AD) = line.split(',')
    (RD, AD) = (REG(RD), INT(AD))
    return [hex((0b0010 << 4) + (0 << 2) + RD)[2:], HEX(AD)]

def OUT(line):
    (AD, RS) = line.split(',')
    (AD, RS) = (INT(AD), REG(RS))
    return [hex((0b0011 << 4) + (RS << 2) + 0)[2:], HEX(AD)]

def LDI(line):
    (RD, A) = line.split(',')
    (RD, A) = (REG(RD), INT(A))
    return [hex((0b0110 << 4) + (0 << 2) + RD)[2:], HEX(A)]

builtin_syms = {'MOV' : 1,
                'ADD' : 1,
                'SUB' : 1,
                'AND' : 1,
                'OR' : 1,
                'RR' : 1,
                'INC' : 1,
                'HLT' : 1,
                'LAD' : 2,
                'STA' : 2,
                'JMP' : 2,
                'BZC' : 2,
                'IN' : 2,
                'OUT' : 2, 
                'LDI' : 2}

dispatch = {'MOV' : 1,
            'ADD' : ADD,
            'SUB' : SUB,
            'AND' : AND,
            'OR' : OR,
            'RR' : RR,
            'INC' : INC,
            'HLT' : HLT,
            'LAD' : LAD,
            'STA' : STA,
            'JMP' : JMP,
            'BZC' : BZC,
            'IN' : IN,
            'OUT' : OUT, 
            'LDI' : LDI}

def dispatcher(line):
    try:
        return dispatch[line.split(' ')[0]](line.split(' ')[1])
    except IndexError:
        #For HLT
        return dispatch[line.split(' ')[0]]()

def trans(pesudo):
    pesudo = list(filter(lambda x: len(x) > 0, pesudo.split('\n')))
    internal = list()
    syms = {'RI' : 'R2'}
    index = 0

    for x in pesudo:
        #Generate syms_table
        sym = x.split(' ')[0]
        if sym not in builtin_syms.keys():
            syms[sym[:-1]] = HEX(index) + 'H'
            x = x[len(sym)+1:]
            sym = x.split(' ')[0]
        index += builtin_syms[sym]
        internal.append(x)
    internal = '\n'.join(internal)

    for x in internal:
        #Resolve address of syms in syms_table
        for x in syms:
            internal = internal.replace(x,syms[x])
    internal = internal.split('\n')

    result = list()
    index = 0
    for (asm, comment) in zip(internal, pesudo):
        #Really do the transformation
        r = dispatcher(asm)
        if isinstance(r, list):
            result.append(HEX(index) + " " + r[0].upper() + " ; " + comment)
            index += 1
            result.append(HEX(index) + " " + r[1])
        else:
            result.append(HEX(index) + " " + r.upper() + " ; " + comment)
        index += 1

    return "\n".join(result)

if __name__ == "__main__":
    code = ""
    while True:
        try:
            code += input() + '\n'
        except EOFError:
            print(trans(code))
            break
