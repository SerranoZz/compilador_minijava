def agrupar_expressoes(vetor):
    if not any(op in vetor for op in ['+', '-', '*']):  # Verifica se o vetor contém algum operador
        return vetor
    expressoes = []
    expressao_atual = []
    print(vetor)
    for i in range(len(vetor)):
        if i + 1 < len(vetor):  # Verifica se há um operador após o item atual
            if vetor[i + 1] in ['+', '-', '*']:
                expressao_atual.append(vetor[i])
            elif vetor[i] in ['+', '-', '*']:
                expressao_atual.append(vetor[i])
            else:
                expressao_atual.append(vetor[i])
                expressoes.append(expressao_atual)
                expressao_atual = []
        else:
            expressao_atual.append(vetor[i])

    if expressao_atual:  # Adiciona a última expressão, se houver
        expressoes.append(expressao_atual)

    return expressoes

# Exemplo de uso:
entrada = ['2', '3','5']
saida = agrupar_expressoes(entrada)
print(saida)
