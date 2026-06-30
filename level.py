# level.py
# Definição das FASES do jogo: plataformas, moedas, inimigos, bandeira
# e background de cada fase.
#
# COMO CRIAR UMA FASE NOVA (ex: Fase 3):
#   1. Copie uma das funções construir_fase_N() abaixo (ex: a da Fase 2)
#   2. Cole após ela, renomeie para construir_fase_3()
#   3. Ajuste largura_fase, segmentos_chao, plataformas_flutuantes,
#      posicoes_moedas, posicoes_inimigos e nome="Fase 3" como quiser
#   4. Defina imagem_background="background_fase3.png" (ou outro nome)
#      e coloque esse arquivo em assets/images/
#   5. Adicione construir_fase_3 na lista FASES, no final deste arquivo
#
# Pronto - o jogo passa a ter 3 fases automaticamente, na ordem da lista.
# Ao tocar a bandeira da última fase da lista, o jogo declara vitória;
# nas fases intermediárias, ele avança para a próxima automaticamente.

import pygame
from settings import ALTURA, IMG_BANDEIRA
from sprites.platform import Plataforma, PlataformaMovel, PlataformaCaindo, PlataformaQuebradica
from sprites.coin import Moeda
from sprites.enemy import Inimigo, MonstroVoador, MonstroAtirador
from sprites.spike import Espinho
from utils import carregar_imagem

CHAO_Y = ALTURA - 40  # altura do chão principal (igual em todas as fases)


class Bandeira(pygame.sprite.Sprite):
    """Objetivo final da fase: tocar nela avança para a próxima fase
    (ou vence o jogo, se for a última)."""
    def __init__(self, x, y):
        super().__init__()
        self.image = carregar_imagem(IMG_BANDEIRA, tamanho=(40, 80), cor_fallback=(60, 180, 75))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def desenhar(self, tela, deslocamento_camera):
        pos = (self.rect.x - deslocamento_camera, self.rect.y)
        tela.blit(self.image, pos)


def _montar_fase(largura_fase, segmentos_chao, plataformas_flutuantes,
                  posicoes_moedas, posicoes_inimigos, nome="Fase",
                  imagem_background=None,
                  plataformas_moveis=None, plataformas_caindo=None,
                  plataformas_quebradicas=None, posicoes_espinhos=None,
                  posicoes_monstros_voadores=None, posicoes_monstros_atiradores=None):
    """
    Função auxiliar interna: monta os grupos de sprites a partir de
    listas simples de coordenadas. Usada por todas as construir_fase_N().

    Parâmetros novos (todos opcionais - omita os que não for usar):

    plataformas_moveis: lista de tuplas
        (x, y, largura, altura, ponto_final, eixo)
        eixo é "horizontal" ou "vertical". ponto_final é a posição
        (x se horizontal, y se vertical) até onde ela vai e volta.
        Ex: (300, 400, 120, 24, 600, "horizontal")
            -> anda entre x=300 e x=600, na altura y=400.

    plataformas_caindo: lista de tuplas (x, y, largura, altura)
        Plataforma normal até o herói pisar; depois treme e cai.

    plataformas_quebradicas: lista de tuplas (x, y, largura, altura)
        ou (x, y, largura, altura, pisadas_para_quebrar) para
        personalizar quantas pisadas ela resiste.

    posicoes_espinhos: lista de tuplas (x, y) ou (x, y, largura, altura)
        Obstáculo fixo que causa dano ao toque.

    posicoes_monstros_voadores: lista de tuplas
        (x, y, distancia_patrulha, amplitude_vertical)
        Monstro que voa livremente, sem precisar de chão.

    posicoes_monstros_atiradores: lista de tuplas
        (x, y, direcao_inicial, distancia_patrulha)
        direcao_inicial: 1 (atira para a direita) ou -1 (para a esquerda).
        distancia_patrulha=0 -> fica parado disparando do mesmo lugar.

    imagem_background: nome do arquivo de fundo desta fase específica
    (ex: "background_fase1.png"). Se None, a tela de jogo usa o
    background padrão (IMG_BACKGROUND) definido em settings.py.
    """
    plataformas = pygame.sprite.Group()
    moedas = pygame.sprite.Group()
    inimigos = pygame.sprite.Group()
    espinhos = pygame.sprite.Group()

    for inicio, fim in segmentos_chao:
        plataformas.add(Plataforma(inicio, CHAO_Y, fim - inicio, 40))

    for x, y, larg, alt in plataformas_flutuantes:
        plataformas.add(Plataforma(x, y, larg, alt))

    for x, y, larg, alt, ponto_final, eixo in (plataformas_moveis or []):
        plataformas.add(PlataformaMovel(x, y, larg, alt, ponto_final, eixo=eixo))

    for x, y, larg, alt in (plataformas_caindo or []):
        plataformas.add(PlataformaCaindo(x, y, larg, alt))

    for item in (plataformas_quebradicas or []):
        if len(item) == 4:
            x, y, larg, alt = item
            plataformas.add(PlataformaQuebradica(x, y, larg, alt))
        else:
            x, y, larg, alt, pisadas = item
            plataformas.add(PlataformaQuebradica(x, y, larg, alt, pisadas_para_quebrar=pisadas))

    for item in (posicoes_espinhos or []):
        if len(item) == 2:
            x, y = item
            espinhos.add(Espinho(x, y))
        else:
            x, y, larg, alt = item
            espinhos.add(Espinho(x, y, largura=larg, altura=alt))

    for x, y in posicoes_moedas:
        moedas.add(Moeda(x, y))

    for x, y, dist in posicoes_inimigos:
        inimigos.add(Inimigo(x, y, dist))

    for item in (posicoes_monstros_voadores or []):
        if len(item) == 2:
            x, y = item
            inimigos.add(MonstroVoador(x, y))
        elif len(item) == 3:
            x, y, dist = item
            inimigos.add(MonstroVoador(x, y, distancia_patrulha=dist))
        else:
            x, y, dist, amplitude = item
            inimigos.add(MonstroVoador(x, y, distancia_patrulha=dist, amplitude_vertical=amplitude))

    for item in (posicoes_monstros_atiradores or []):
        if len(item) == 2:
            x, y = item
            inimigos.add(MonstroAtirador(x, y))
        elif len(item) == 3:
            x, y, direcao = item
            inimigos.add(MonstroAtirador(x, y, direcao_inicial=direcao))
        else:
            x, y, direcao, dist = item
            inimigos.add(MonstroAtirador(x, y, direcao_inicial=direcao, distancia_patrulha=dist))

    bandeira = Bandeira(largura_fase - 120, CHAO_Y - 80)

    return {
        "nome": nome,
        "plataformas": plataformas,
        "moedas": moedas,
        "inimigos": inimigos,
        "espinhos": espinhos,
        "bandeira": bandeira,
        "largura_fase": largura_fase,
        "imagem_background": imagem_background,
    }


# =========================================================================
# FASE 1
# =========================================================================
def construir_fase_1():
    largura_fase = 3200

    segmentos_chao = [
        (0, 700),
        (780, 1300),
        (1380, 2000),
        (2100, 3200),
    ]

    plataformas_flutuantes = [
        (300, 380, 120, 24),
        (520, 300, 120, 24),
        (900, 420, 100, 24),
        (1050, 320, 100, 24),
        (1450, 400, 140, 24),
        (1650, 280, 100, 24),
        (1900, 360, 100, 24),
        (2250, 420, 120, 24),
        (2450, 320, 100, 24),
        (2700, 400, 140, 24),
    ]

    posicoes_moedas = [
        (340, 340), (560, 260), (920, 380), (1070, 280),
        (1470, 360), (1670, 240), (1920, 320), (2270, 380),
        (2470, 280), (2720, 360),
        (150, CHAO_Y - 40), (450, CHAO_Y - 40), (1700, CHAO_Y - 40),
        (2900, CHAO_Y - 40), (3000, CHAO_Y - 40),
    ]

    # (x, y, distancia_de_patrulha)
    posicoes_inimigos = [
        (500, CHAO_Y - 48, 100),
        (1000, CHAO_Y - 48, 120),
        (1600, CHAO_Y - 48, 100),
        (1950, 312, 80),
        (2300, CHAO_Y - 48, 150),
        (2900, CHAO_Y - 48, 100),
    ]

    return _montar_fase(
        largura_fase, segmentos_chao, plataformas_flutuantes,
        posicoes_moedas, posicoes_inimigos, nome="Fase 1",
        imagem_background="background_fase1.png"
    )


# =========================================================================
# FASE 2
# (mais longa e com mais inimigos / buracos maiores - ajuste como quiser)
# =========================================================================
def construir_fase_2():
    largura_fase = 4000

    segmentos_chao = [
        (0, 600),
        (700, 1100),
        (1220, 1700),
        (1820, 2200),
        (2340, 2750),
        (2750, 3150),
        (3250, 4000),
    ]

    plataformas_flutuantes = [
        (250, 360, 110, 24),
        (480, 280, 110, 24),
        (650, 420, 90, 24),
        (800, 300, 110, 36),
        (1130, 340, 100, 24),
        (1350, 260, 130, 40),
        (1750, 380, 120, 24),
        (1950, 300, 100, 24),
        (2250, 420, 100, 24),
        (2480, 320, 100, 24),
        (2700, 360, 120, 24),
        (3100, 280, 100, 24),
        (3350, 400, 40, 24),
        (3600, 320, 100, 24),
    ]

    posicoes_moedas = [
        (290, 320), (520, 240), (690, 380),
        (1190, 300), (1390, 220), (1790, 340),
        (1990, 260), (2290, 380), (2520, 280),
        (2840, 320), (3140, 240), (3390, 360), (3640, 280),
        (150, CHAO_Y - 40), (950, CHAO_Y - 40), (2050, CHAO_Y - 40),
        (2600, CHAO_Y - 40), (3800, CHAO_Y - 40), (3900, CHAO_Y - 40),
    ]

    posicoes_inimigos = [
        (450, CHAO_Y - 48, 100),
        (900, CHAO_Y - 48, 120),
        (1300, 220, 80),
        (1650, CHAO_Y - 48, 100),
        (2000, CHAO_Y - 48, 130),
        (2400, 380, 80),
        (2700, CHAO_Y - 48, 100),
        (3200, CHAO_Y - 48, 150),
        (3700, CHAO_Y - 48, 120),
    ]

    # ---- Exemplos de plataformas especiais (Fase 2 em diante) ----

    # Plataforma móvel horizontal: anda de x=1450 até x=1650, na altura y=300
    plataformas_moveis = [
        (1450, 300, 100, 24, 1650, "horizontal"),
        # Plataforma móvel vertical: sobe e desce entre y=200 e y=420
        (2950, 420, 100, 24, 200, "vertical"),
    ]

    # Plataforma que cai pouco depois do herói pisar
    plataformas_caindo = [
        (3450, 380, 110, 24),
    ]

    # Plataforma quebradiça: quebra após 3 pisadas (padrão)
    plataformas_quebradicas = [
        (3850, 340, 100, 24),
    ]

    # Espinhos no chão: cuidado para não cair em cima
    posicoes_espinhos = [
        (1040, CHAO_Y - 40),
        (2900, CHAO_Y - 40),
    ]

    # Monstro voador: sobrevoa o trecho entre x=2050 e x=2200
    posicoes_monstros_voadores = [
        (2050, 280, 150, 35),
    ]

    # Monstro atirador: fica perto de x=3000, disparando para a esquerda
    posicoes_monstros_atiradores = [
        (3000, CHAO_Y - 48, -1, 0),  # direcao=-1 (esquerda), patrulha=0 (fica parado)
    ]

    return _montar_fase(
        largura_fase, segmentos_chao, plataformas_flutuantes,
        posicoes_moedas, posicoes_inimigos, nome="Fase 2",
        imagem_background="background_fase2.png",
        plataformas_moveis=plataformas_moveis,
        plataformas_caindo=plataformas_caindo,
        plataformas_quebradicas=plataformas_quebradicas,
        posicoes_espinhos=posicoes_espinhos,
        posicoes_monstros_voadores=posicoes_monstros_voadores,
        posicoes_monstros_atiradores=posicoes_monstros_atiradores,
    )


# =========================================================================
# LISTA DE FASES
# =========================================================================
# A ordem da lista é a ordem em que as fases acontecem no jogo.
# Para adicionar a Fase 3: escreva uma função construir_fase_3() acima,
# seguindo o mesmo modelo, e adicione ela aqui na lista.
FASES = [
    construir_fase_1,
    construir_fase_2,
]

TOTAL_FASES = len(FASES)


def construir_fase(numero_fase):
    """
    Constrói e retorna os dados da fase pelo número (1, 2, 3, ...).
    Lança IndexError se o número não existir em FASES.
    """
    indice = numero_fase - 1
    if indice < 0 or indice >= len(FASES):
        raise IndexError(f"Fase {numero_fase} não existe (total de fases: {TOTAL_FASES})")
    return FASES[indice]()
