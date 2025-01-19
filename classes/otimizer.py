import math

dict_methods = {}
new_code = []

def get_params(block):
    """
    Otimização global.
    Precisa de alguns ajustes.
    Talvez não seja utilizada.
    """
    global dict_methods
    params_list = []
    class_name = ""
    if len(block) > 0 and 'call' not in block[-1]: # Não há chamada de método
        return
    for line in block:
        if '.' in line:
            for iten in line.split():
                if '.' in iten:
                    class_name = iten.strip(',')
                    break
        if line.startswith('param'):
            params_list.append(line.split()[1].strip())
    params_list.reverse()
    dict_methods[class_name] = params_list
    print(dict_methods)

def expoente_2(n):
    try:
        n = int(n)
    except ValueError:
        return False
    return n > 0 and (n & (n - 1)) == 0

def otimizacao_algebrica(block):
    new_block = []
    new_line = ""
    for line in block:
        if '** 2' in line:
            operando = line.split()[2]
            new_line = line.replace('** 2', f'* {operando}')
        elif '*' in line:
            num = line.split()[-1].strip()
            if expoente_2(num):
                new_line = line.replace(f"* {num}", f"<< {int(math.log2(int(num)))}")
            else:
                new_line = line
        elif '* 0' in line or ' 0 *' in line:
            var = line.split()[0]
            new_line = f"{var} := 0"
        elif ('+ 0' in line or ' 0 +' in line) or ('* 1\n' in line or ' 1 *' in line) or ('- 0' in line or ' 0 -' in line):
            new_line = ""
        else:
            new_line = line.strip()
        new_block.append(new_line.strip())
    return new_block

def propagacao_copia(block):
    one_value = []
    for i, line in enumerate(block):
        itens = line.split()
        if len(itens) == 3:
            one_value.append([itens[0],itens[2]])
            block.pop(i)
    for i, line in enumerate(block):
        for iten in one_value:
            if iten[0] in line.split():
                block[i] = block[i].replace(iten[0], iten[1])
    return block


def atrib_simples(block):
    left = []
    for line in block:
        if len(line) > 1:
            left.append(line.split()[0])
    for i, iten in enumerate(left):
        if left.count(iten) > 1:
            left[i] = f"new_{iten}"
            block[i] = block[i].replace(iten, f"new_{iten}")
            for j in range(i+1, len(block)):
                block[j] = block[j].replace(iten, f"new_{iten}")
                if block[j].split()[0] == f"new_{iten}": # Nova atribuição
                    block[j] = block[j].replace(f"new_{iten}", iten, 1)
                    break
    return block

def are_numbers(x, y):
    try:
        int(x)
        int(y)
    except ValueError:
        return False
    return True

def desdobramento_constante(block):
    for i, line in enumerate(block):
        itens = line.split()
        if len(itens) > 4 and are_numbers(itens[2],itens[4]):
            exp = f"{itens[2]} {itens[3]} {itens[4]}"
            block[i] = block[i].replace(exp, str(eval(exp)))
    return block

def remover_mortos(block):
    left = []
    right = []
    for line in block:
        if ':=' in line:
            left.append(line.split()[0])
            right.append(line.split()[1:])
        else:
            left.append("nada")
            right.append(["nada"])
    #for i in range(len(block)):
    #    print(left[i], right[i], block[i])
    for i, iten in enumerate(left):
        count = 0
        for r in right:
            if iten in r:
                count += 1
                break
        if count == 0:
            print(i)
            print(block)
            block.pop(i)
    return block

def save_in_file():
    with open('./outputs/otimized_inter_code.txt', 'w') as f:
        for line in new_code:
            f.write(line+'\n')

def local_otimizer(block):
    for _ in range(3):
        block = otimizacao_algebrica(block)
        block = atrib_simples(block)
        block = propagacao_copia(block)
        block = desdobramento_constante(block)
        #block = remover_mortos(block)
    for line in block:
        new_code.append(line)

def read_file(filename):
    f = open(filename, 'r')
    data = f.readlines()
    block = []
    for line in data:
        if line.strip().endswith(':'):
            #get_params(block)
            local_otimizer(block)
            block = []
        block.append(line)
        if 'call' in line:
            #get_params(block)
            local_otimizer(block)
            block = []
    local_otimizer(block)

read_file('./outputs/inter_code.txt')
save_in_file()
