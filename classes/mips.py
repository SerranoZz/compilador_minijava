import re

mips = []
actual_method = []
actual_params = []
t_count = 0
temps = {}

def new_temp():
    global t_count
    t_count += 1
    return t_count

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
    t_var = f"$t{new_temp()}"
    mips.append(f"lw {t_var} 4($sp)")
    mips.append("addiu $sp $sp 4")
    return t_var


def if_false(condition, op1, op2, label):
    if "<=" in condition:
        return f"bgt {op1} {op2} {label}"
    if ">=" in condition:
        return f"blt {op1} {op2} {label}"
    if "<" in condition:
        return f"bge {op1} {op2} {label}"
    if ">" in condition:
        return f"ble {op1} {op2} {label}"
    if "!=" in condition:
        return f"beq {op1} {op2} {label}"
    if "==" in condition:
        return f"bne {op1} {op2} {label}"

def cgen(op):
    if is_numeric(op):
        mips.append(f"li $a0 {op}")
    elif op in actual_params:
        i = actual_params.index(op) + 1
        mips.append(f"lw $a0 {str(4*i)}($fp)")


def operation(op):
    global t_count
    t_var = f"$t{t_count}"
    if op == '+':
        mips.append(f"add $a0 {t_var} $a0")
    elif op == '-':
        mips.append(f"sub $a0 {t_var} $a0")
    elif op == '*':
        mips.append(f"mul $a0 {t_var} $a0")
    else:
        t_count -= 1

def assign(line):
    if len(line.split()) == 3: # Atribuição simples
        cgen(line.split()[-1])
    elif '+' in line or '-' in line or '*' in line: # Atribuição com operação aritmética
        op1 = line.strip().split()[-3]
        operator = line.strip().split()[-2]
        op2 = line.strip().split()[-1]
        cgen(op1)
        mips.append("sw $a0 0($sp)")
        mips.append("addiu $sp $sp -4")
        cgen(op2)
        t_var = f"$t{new_temp()}"
        mips.append(f"lw {t_var} 4($sp)")
        mips.append("addiu $sp $sp 4")
        operation(operator)
    elif '>' in line or '<' in line:
        op1 = line.strip().split()[-3]
        operator = line.strip().split()[-2]
        op2 = line.strip().split()[-1]
        cgen(op1)
        mips.append("sw $a0 0($sp)")
        mips.append("addiu $sp $sp -4")
        cgen(op2)
        t_var = f"$t{new_temp()}"
        mips.append(f"lw {t_var} 4($sp)")
        mips.append("addiu $sp $sp 4")

def is_numeric(n):
    try:
        int(n)
    except ValueError:
        return False
    return True

def get_op(op):
    global actual_params
    if is_numeric(op):
        print(f"op: {op}")
        mips.append(f"li $a0 {op}")
        return op
    if op in actual_params:
        return get_param()
    return "$a0"

def call_method(idx, data):
    global actual_params
    actual_params = []
    start = idx - 1
    sw("$fp", "$sp")
    while "param" in data[start]:
        start -= 1
    for j in range(start+1, idx):
        value = data[j].split()[1]
        cgen(value)
        sw("$a0", "$sp")
        actual_params.append(value)
    actual_params.reverse()
    label = data[idx].split()[3].strip(',')
    mips.append(f"jal {label}")

def end_method():
    mips.append("lw $ra 4($sp)")
    z = 8 + 4 * len(actual_params)
    print(actual_params)
    mips.append(f"addiu $sp $sp {z}")
    mips.append("lw $fp 0($sp)")
    mips.append("jr $ra")

def iniciar(filename):
    global actual_method
    global actual_params
    f = open(filename, 'r')
    data = f.readlines()
    f.close()
    for i, line in enumerate(data):
        line = line.strip()
        if not line:
            continue
        if line.endswith(":") and "." in line: # Representa um bloco
            actual_method = []
            label = line[:-1].split('(')[0]
            actual_method.append(label)
            params = re.search(r'\((.*?)\)', line)
            params = params.group(1).split(',')
            for param in params:
                actual_method.append(param.strip())
            mips.append(f"{label}:")
            build_method()
        elif "call" in line:
            call_method(i, data)
        elif "print" in line:
            syscall()
        elif "ifFalse" in line:
            condition = data[i-1].split('=')[1].strip()
            op1 = condition.split()[0]
            op2 = condition.split()[-1]
            label = line.strip().split()[-1]
            t_var = f"$t{t_count}"
            mips.append(f"{if_false(condition, '$a0', t_var, label)}")
        elif ":=" in line: # Atribuição
            assign(line)
        elif line.startswith("goto"):
            label = line.strip().split()[-1]
            mips.append(f"b {label}")
        elif line.endswith(":") and (line.startswith("else_") or line.startswith("true_") or line.startswith("end_")):
            mips.append(f"{line}")
        elif "return" in line:
            end_method()
    
    for inst in mips:
        print(inst)

iniciar('./outputs/otimized_inter_code.txt')