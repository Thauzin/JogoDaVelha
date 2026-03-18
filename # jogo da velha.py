# jogo da velha
import math

# Tabuleiro vazio
tabuleiro = [" " for _ in range(9)]

# Mostrar tabuleiro
def mostrar_tabuleiro():
    print()
    print(tabuleiro[0], "|", tabuleiro[1], "|", tabuleiro[2])
    print("--+---+--")
    print(tabuleiro[3], "|", tabuleiro[4], "|", tabuleiro[5])
    print("--+---+--")
    print(tabuleiro[6], "|", tabuleiro[7], "|", tabuleiro[8])
    print()


# Verificar vencedor
def verificar_vencedor(tab, jogador):
    combinacoes = [
        [0,1,2],[3,4,5],[6,7,8],
        [0,3,6],[1,4,7],[2,5,8],
        [0,4,8],[2,4,6]
    ]

    for c in combinacoes:
        if tab[c[0]] == tab[c[1]] == tab[c[2]] == jogador:
            return True
    return False


# Verificar empate
def empate(tab):
    return " " not in tab


# 🧠 Função de avaliação (AGORA FUNCIONAL)
def avaliar_estado(tabuleiro):
    peso_vitoria = 2
    peso_quase = 10
    bias = 0

    score = 0

    combinacoes = [
        [0,1,2],[3,4,5],[6,7,8],
        [0,3,6],[1,4,7],[2,5,8],
        [0,4,8],[2,4,6]
    ]

    for c in combinacoes:
        linha = [tabuleiro[i] for i in c]

        # Vitória
        if linha.count("X") == 3:
            score += peso_vitoria
        elif linha.count("O") == 3:
            score -= peso_vitoria

        # Quase vitória
        elif linha.count("X") == 2 and linha.count(" ") == 1:
            score += peso_quase
        elif linha.count("O") == 2 and linha.count(" ") == 1:
            score -= peso_quase

    return score + bias


# 🤖 Minimax com profundidade limitada + avaliação
def minimax(tab, profundidade, maximizando):

    # Estados finais
    if verificar_vencedor(tab, "X"):
        return 100
    if verificar_vencedor(tab, "O"):
        return -100
    if empate(tab):
        return 0

    # 🔥 Limite de profundidade (usa avaliação)
    if profundidade == 3:
        return avaliar_estado(tab)

    if maximizando:
        melhor = -math.inf

        for i in range(9):
            if tab[i] == " ":
                tab[i] = "X"
                valor = minimax(tab, profundidade + 1, False)
                tab[i] = " "
                melhor = max(melhor, valor)

        return melhor

    else:
        melhor = math.inf

        for i in range(9):
            if tab[i] == " ":
                tab[i] = "O"
                valor = minimax(tab, profundidade + 1, True)
                tab[i] = " "
                melhor = min(melhor, valor)

        return melhor


# IA escolhe a melhor jogada
def melhor_jogada():
    melhor_valor = -math.inf
    jogada = None

    for i in range(9):
        if tabuleiro[i] == " ":
            tabuleiro[i] = "X"
            valor = minimax(tabuleiro, 0, False)
            tabuleiro[i] = " "

            if valor > melhor_valor:
                melhor_valor = valor
                jogada = i

    return jogada


# Loop do jogo
while True:

    mostrar_tabuleiro()

    pos = int(input("Escolha posição (0-8): "))

    if tabuleiro[pos] != " ":
        print("Posição ocupada!")
        continue

    tabuleiro[pos] = "O"

    if verificar_vencedor(tabuleiro, "O"):
        mostrar_tabuleiro()
        print("Você venceu!")
        break

    if empate(tabuleiro):
        mostrar_tabuleiro()
        print("Empate!")
        break

    # IA joga
    ia = melhor_jogada()
    tabuleiro[ia] = "X"

    if verificar_vencedor(tabuleiro, "X"):
        mostrar_tabuleiro()
        print("IA venceu!")
        break

    if empate(tabuleiro):
        mostrar_tabuleiro()
        print("Empate!")
        break