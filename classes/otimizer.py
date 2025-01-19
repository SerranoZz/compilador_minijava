import math
import re

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
        if len(itens) == 3 and itens[1] == ':=':
            one_value.append([itens[0],itens[2]])
            #block.pop(i)
    for i, line in enumerate(block):
        for itens in one_value:
            if itens[0] in line.split()[1:]:
                new_line = line.split()[1:]
                new_line[new_line.index(itens[0])] = itens[1]
                block[i] = f"{line.split()[0]} {' '.join(new_line)}"
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
                if f"{iten}" in block[j].split()[1:]:
                    new_line = block[j].split()[1:]
                    new_line[new_line.index(iten)] = f"new_{iten}"
                    block[j] = f"{block[j].split()[0]} {' '.join(new_line)}"
                if block[j].split()[0] == iten: # Nova atribuição
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

def remover_mortos(new_code, final_code):
    left = []
    right = []
    for i, line in enumerate(new_code):
        if 'ifFalse' in line:
            itens = line.split()
            if itens[1] == 'False':
                idx = final_code.index(line)
                final_code[idx] = f"goto {itens[-1]}"
                #for j in range(idx+1, len(final_code)):
                #   if final_code[j] == f"{itens[-1]}:":
                #        break
                #    final_code.pop(j)
            elif itens[1] == 'True':
                idx = final_code.index(line)
                final_code.pop(idx+1) # Remove o indicador do label de True
                final_code.pop(idx) # Remove o IF
        elif ':=' in line and re.match(r'^t\d+$', line.split()[0]): # Atribuição de temporário
            t_var = line.split()[0]
            count = 0
            for final_line in final_code:
                if t_var in final_line.split()[1:]:
                    count += 1
                    break
            if count == 0:
                final_code.pop(final_code.index(line))
    return final_code

def save_in_file(code):
    with open('./outputs/otimized_inter_code.txt', 'w') as f:
        for line in code:
            f.write(line+'\n')

def global_otimizer():
    final_code = []
    for line in new_code:
        final_code.append(line)
    return remover_mortos(new_code, final_code)

def local_otimizer(block):
    for _ in range(3):
        #get_params(block)
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
    return global_otimizer()

code = read_file('./outputs/inter_code.txt')
save_in_file(code)
