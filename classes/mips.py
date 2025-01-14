mips = []
actual_method = None
actual_params = None

def sw(op1, op2):
    mips.append(f"sw {op1} (0){op2}")
    mips.append(f"addiu {op2} {op2} -4")

def lw(op1, op2):
    mips.append(f"lw {op1} (4){op2}")

def li(op1, op2):
    mips.append(f"li {op1} {op2}")

def syscall():
    mips.append("li $v0 1") # Imprimir inteiro
    mips.append("syscall")
    mips.append("li $v0 10") # Encerrar programa
    mips.append("syscall\n")

def build_method():
    mips.append("move $fp $sp")
    sw("$ra", "$sp")
    lw("$a0", "$fp")
    sw("$a0", "$sp")

def get_param():
    mips.append("lw $t1 4($sp)")
    mips.append("addiu $sp $sp 4")
    return "$t1"


def if_false(condition, op1, op2, label):
    if "<=" in condition:
        return f"bgt {op1} {op2} {label}"
    if ">=" in condition:
        return f"blt {op1} {op2} {label}"
    if ">" in condition:
        return f"bge {op1} {op2} {label}"
    if "<" in condition:
        return f"ble {op1} {op2} {label}"
    if "!=" in condition:
        return f"beq {op1} {op2} {label}"
    if "==" in condition:
        return f"bne {op1} {op2} {label}"

def op_ari(operando1, operador, operando2):
    if operador == '+':
           

def get_op(op):
    global actual_params
    if op.isnumeric():
        mips.append(f"li $a0 {op}")
        return op
    if op in actual_params:
        return get_param()
    return "$a0"

def iniciar(filename):
    global actual_method
    global actual_params
    f = open(filename, 'r')
    data = f.readlines()
    f.close()
    for i, line in enumerate(data):
        #print(f"{i}: {line}")
        line = line.strip()
        if not line:
            continue
        if line.endswith(":") and "." in line: # Representa um bloco
            label = line[:-1].split('(')[0]
            actual_method = label
            actual_params = line[:-1].split('(')[1].strip(')')
            mips.append(f"{label}:")
            if "main" not in line: # É um método
                build_method()
        elif "param" in line:
            sw("$fp", "$sp")
            value = line.split()[1]
            li("$a0", value)
            sw("$a0", "$sp")
        elif "call" in line:
            label = line.split()[3].strip(',')
            mips.append(f"jal {label}")
        elif "print" in line:
            syscall()
        elif "ifFalse" in line:
            condition = data[i-1].split('=')[1].strip()
            op1 = condition.split()[0]
            op2 = condition.split()[-1]
            label = line.strip().split()[-1]
            mips.append(f"{if_false(condition, get_op(op1), get_op(op2), label)}")
        elif ":=" in line: # Atribuição
            if len(line.strip().split()) == 3: # Atribuição simples
                op = line.strip().split()[-1]
                mips.append(f"li $a0 {op}")
            elif '+' in line or '-' in line or '*' in line: # Atribuição com operação aritmética
                op1 = line.strip().split()[-3]
                operator = line.strip().split()[-2]
                op2 = line.strip().split()[-1]
        elif line.startswith("goto"):
            label = line.strip().split()[-1]
            mips.append(f"b {label}")
        elif line.endswith(":") and line.startswith("else_"):
            mips.append(f"{line}")
        elif "return" in line:
            mips.append(f"jr $ra")
    
    for inst in mips:
        print(inst)

iniciar('./outputs/inter_code.txt')