Jogo da Velha com Monte Carlo Tree Search (MCTS)

import math
import random


# ---------------------------------------------------------------------------
# Tabuleiro
# ---------------------------------------------------------------------------

tabuleiro = [" " for _ in range(9)]


def mostrar_tabuleiro():
    print()
    print(tabuleiro[0], "|", tabuleiro[1], "|", tabuleiro[2])
    print("--+---+--")
    print(tabuleiro[3], "|", tabuleiro[4], "|", tabuleiro[5])
    print("--+---+--")
    print(tabuleiro[6], "|", tabuleiro[7], "|", tabuleiro[8])
    print()


# ---------------------------------------------------------------------------
# Regras do jogo
# ---------------------------------------------------------------------------

def verificar_vencedor(tab, jogador):
    combinacoes = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8],
        [0, 3, 6], [1, 4, 7], [2, 5, 8],
        [0, 4, 8], [2, 4, 6]
    ]
    for c in combinacoes:
        if tab[c[0]] == tab[c[1]] == tab[c[2]] == jogador:
            return True
    return False


def empate(tab):
    return " " not in tab


def jogo_encerrado(tab):
    return verificar_vencedor(tab, "X") or verificar_vencedor(tab, "O") or empate(tab)


def jogadas_possiveis(tab):
    return [i for i, v in enumerate(tab) if v == " "]


# ---------------------------------------------------------------------------
# Nó da árvore MCTS
# ---------------------------------------------------------------------------

class No:
    """Representa um estado do tabuleiro na árvore de busca."""

    def __init__(self, tab, jogador, jogada=None, pai=None):
        self.tab = tab[:]          # cópia do tabuleiro neste estado
        self.jogador = jogador     # jogador que VAI jogar a partir deste nó
        self.jogada = jogada       # jogada que gerou este nó (índice 0-8)
        self.pai = pai             # nó pai

        self.filhos = []
        self.vitorias = 0          # vitórias acumuladas nas simulações
        self.visitas = 0           # total de visitas

        # Jogadas ainda não expandidas a partir deste estado
        self.nao_expandidas = jogadas_possiveis(self.tab)

    # ------------------------------------------------------------------
    # UCB1 — Upper Confidence Bound aplicado a árvores
    # ------------------------------------------------------------------
    def ucb1(self, c=math.sqrt(2)):
        """Calcula o valor UCB1 para seleção do nó mais promissor."""
        if self.visitas == 0:
            return float("inf")
        return (self.vitorias / self.visitas) + c * math.sqrt(
            math.log(self.pai.visitas) / self.visitas
        )

    def totalmente_expandido(self):
        return len(self.nao_expandidas) == 0

    def eh_terminal(self):
        return jogo_encerrado(self.tab)


# ---------------------------------------------------------------------------
# As quatro fases do MCTS
# ---------------------------------------------------------------------------

def selecionar(no):
    """Desce na árvore escolhendo o filho com maior UCB1 até encontrar
    um nó não totalmente expandido ou terminal."""
    while not no.eh_terminal() and no.totalmente_expandido():
        no = max(no.filhos, key=lambda f: f.ucb1())
    return no


def expandir(no):
    """Cria um novo filho a partir de uma jogada ainda não explorada."""
    jogada = no.nao_expandidas.pop(random.randrange(len(no.nao_expandidas)))
    novo_tab = no.tab[:]
    novo_tab[jogada] = no.jogador
    proximo = "O" if no.jogador == "X" else "X"
    filho = No(novo_tab, proximo, jogada=jogada, pai=no)
    no.filhos.append(filho)
    return filho


def simular(no):
    """Simulação aleatória (rollout) a partir do estado do nó até o fim do jogo.
    Retorna +1 se X vencer, -1 se O vencer, 0 em caso de empate."""
    tab = no.tab[:]
    jogador = no.jogador

    while not jogo_encerrado(tab):
        possiveis = jogadas_possiveis(tab)
        escolha = random.choice(possiveis)
        tab[escolha] = jogador
        jogador = "O" if jogador == "X" else "X"

    if verificar_vencedor(tab, "X"):
        return 1
    if verificar_vencedor(tab, "O"):
        return -1
    return 0


def retropropagar(no, resultado):
    """Propaga o resultado da simulação de volta até a raiz,
    invertendo o sinal a cada nível (perspectiva do jogador)."""
    while no is not None:
        no.visitas += 1
        # X maximiza (+1), O minimiza (-1); invertemos ao subir
        if no.jogador == "O":          # nó pertence ao turno de O → X acabou de jogar
            no.vitorias += resultado
        else:                          # nó pertence ao turno de X → O acabou de jogar
            no.vitorias -= resultado
        no = no.pai


# ---------------------------------------------------------------------------
# Interface principal do MCTS
# ---------------------------------------------------------------------------

def _jogada_imediata(tab, jogador_ia):
    """Retorna uma jogada que vence ou bloqueia imediatamente, se existir."""
    adversario = "O" if jogador_ia == "X" else "X"
    possiveis = jogadas_possiveis(tab)

    # 1. Verificar vitória imediata
    for pos in possiveis:
        copia = tab[:]
        copia[pos] = jogador_ia
        if verificar_vencedor(copia, jogador_ia):
            return pos

    # 2. Bloquear vitória imediata do adversário
    for pos in possiveis:
        copia = tab[:]
        copia[pos] = adversario
        if verificar_vencedor(copia, adversario):
            return pos

    return None


def mcts(tab, jogador_ia="X", iteracoes=50):
    """Executa o MCTS e retorna o índice da melhor jogada para a IA."""
    # Atalho: vitória ou bloqueio imediato (evita erros com poucas iterações)
    jogada_rapida = _jogada_imediata(tab, jogador_ia)
    if jogada_rapida is not None:
        return jogada_rapida

    raiz = No(tab, jogador_ia)

    for _ in range(iteracoes):
        # 1. Seleção
        no = selecionar(raiz)

        # 2. Expansão (se não for terminal)
        if not no.eh_terminal():
            no = expandir(no)

        # 3. Simulação
        resultado = simular(no)

        # 4. Retropropagação
        retropropagar(no, resultado)

    # Escolhe o filho com mais visitas (decisão mais robusta)
    melhor = max(raiz.filhos, key=lambda f: f.visitas)
    return melhor.jogada


# ---------------------------------------------------------------------------
# Loop principal do jogo
# ---------------------------------------------------------------------------

ITERACOES_MCTS = 50   # aumente para uma IA mais forte (e mais lenta)

if __name__ == "__main__":
    while True:
        mostrar_tabuleiro()

        # --- Jogada do jogador (O) ---
        try:
            pos = int(input("Escolha posição (0-8): "))
        except ValueError:
            print("Entrada inválida! Digite um número de 0 a 8.")
            continue

        if not (0 <= pos <= 8):
            print("Posição fora do intervalo! Escolha entre 0 e 8.")
            continue

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

        # --- Jogada da IA (X) via MCTS ---
        print("IA pensando...")
        ia = mcts(tabuleiro, jogador_ia="X", iteracoes=ITERACOES_MCTS)
        tabuleiro[ia] = "X"
        print(f"IA jogou na posição {ia}.")

        if verificar_vencedor(tabuleiro, "X"):
            mostrar_tabuleiro()
            print("IA venceu!")
            break

        if empate(tabuleiro):
            mostrar_tabuleiro()
            print("Empate!")
            break

