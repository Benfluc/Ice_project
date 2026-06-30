# utils.py
# Funções utilitárias: carregamento de imagens/sons com "placeholder" automático
# caso o arquivo de asset ainda não exista (assim o jogo roda mesmo sem os
# arquivos finais de arte/audio).

import os
import pygame

from settings import IMAGES_DIR, SOUNDS_DIR, FONTS_DIR


def desenhar_coracao(superficie, centro_x, centro_y, tamanho, cor):
    """
    Desenha um coração simples (vetorial) numa Surface, usado como
    fallback do HUD de vida quando não há um coracao.png customizado.
    """
    r = tamanho // 2
    # Dois círculos no topo (os "lóbulos" do coração)
    pygame.draw.circle(superficie, cor, (centro_x - r // 2, centro_y - r // 3), r // 2)
    pygame.draw.circle(superficie, cor, (centro_x + r // 2, centro_y - r // 3), r // 2)
    # Triângulo na base (a "ponta" do coração)
    pontos = [
        (centro_x - r, centro_y - r // 4),
        (centro_x + r, centro_y - r // 4),
        (centro_x, centro_y + r),
    ]
    pygame.draw.polygon(superficie, cor, pontos)


def carregar_sequencia_animacao(prefixo, tamanho=None, cor_fallback=(255, 0, 255), max_frames=30):
    """
    Carrega uma sequência de imagens numeradas a partir de um prefixo,
    por exemplo: prefixo="heroi_idle" carrega heroi_idle_1.png,
    heroi_idle_2.png, heroi_idle_3.png... até não encontrar mais nenhum
    arquivo (ou atingir max_frames).

    Retorna uma lista de Surfaces (sempre com pelo menos 1 elemento).
    Se nenhum arquivo "prefixo_N.png" existir, retorna uma lista com um
    único placeholder colorido, para o jogo não quebrar.
    """
    frames = []
    numero = 1
    while numero <= max_frames:
        nome_arquivo = f"{prefixo}_{numero}.png"
        caminho = os.path.join(IMAGES_DIR, nome_arquivo)
        if not os.path.isfile(caminho):
            break
        try:
            img = pygame.image.load(caminho).convert_alpha()
            if tamanho:
                img = pygame.transform.scale(img, tamanho)
            frames.append(img)
        except pygame.error:
            break
        numero += 1

    if not frames:
        # Nenhum frame encontrado -> 1 placeholder colorido (igual ao
        # comportamento de carregar_imagem para imagens estáticas)
        tamanho_placeholder = tamanho if tamanho else (64, 64)
        surf = pygame.Surface(tamanho_placeholder, pygame.SRCALPHA)
        surf.fill(cor_fallback)
        pygame.draw.rect(surf, (0, 0, 0), surf.get_rect(), 2)
        frames.append(surf)

    return frames


class Animacao:
    """
    Controla a troca de frames de uma sequência de imagens ao longo do
    tempo. Use update() a cada frame do jogo, e frame_atual para pegar
    a imagem a ser desenhada nesse instante.
    """

    def __init__(self, frames, velocidade=8):
        """
        frames: lista de Surfaces (ex: vinda de carregar_sequencia_animacao)
        velocidade: a cada quantos frames do JOGO a imagem troca
                    (menor = animação mais rápida)
        """
        self.frames = frames
        self.velocidade = max(1, velocidade)
        self.indice = 0
        self.contador = 0

    def atualizar(self):
        if len(self.frames) <= 1:
            return  # nada a animar
        self.contador += 1
        if self.contador >= self.velocidade:
            self.contador = 0
            self.indice = (self.indice + 1) % len(self.frames)

    def reiniciar(self):
        self.indice = 0
        self.contador = 0

    @property
    def frame_atual(self):
        return self.frames[self.indice]


def carregar_imagem(nome_arquivo, tamanho=None, cor_fallback=(255, 0, 255)):
    """
    Tenta carregar uma imagem de assets/images/<nome_arquivo>.
    Se não existir, devolve uma Surface colorida (placeholder) do tamanho
    pedido, para o jogo não quebrar enquanto os assets reais não chegam.
    """
    caminho = os.path.join(IMAGES_DIR, nome_arquivo)
    if tamanho is None:
        tamanho = (64, 64)

    if os.path.isfile(caminho):
        try:
            img = pygame.image.load(caminho).convert_alpha()
            if tamanho:
                img = pygame.transform.scale(img, tamanho)
            return img
        except pygame.error:
            pass

    # ---- Placeholder ----
    surf = pygame.Surface(tamanho, pygame.SRCALPHA)
    surf.fill(cor_fallback)
    pygame.draw.rect(surf, (0, 0, 0), surf.get_rect(), 2)
    return surf


def carregar_som(nome_arquivo):
    """
    Tenta carregar um som de assets/sounds/<nome_arquivo>.
    Se não existir ou o mixer falhar, devolve None (o jogo deve checar antes
    de tocar).
    """
    caminho = os.path.join(SOUNDS_DIR, nome_arquivo)
    if os.path.isfile(caminho):
        try:
            return pygame.mixer.Sound(caminho)
        except pygame.error:
            return None
    return None


def tocar_musica(nome_arquivo, loop=True, volume=0.5):
    """
    Tenta tocar uma música de fundo a partir de assets/sounds/<nome_arquivo>.
    Se o arquivo não existir, simplesmente não toca nada (sem travar o jogo).
    """
    caminho = os.path.join(SOUNDS_DIR, nome_arquivo)
    if os.path.isfile(caminho):
        try:
            pygame.mixer.music.load(caminho)
            pygame.mixer.music.set_volume(volume)
            pygame.mixer.music.play(-1 if loop else 0)
        except pygame.error:
            pass


def parar_musica():
    try:
        pygame.mixer.music.stop()
    except pygame.error:
        pass


def carregar_fonte(nome_arquivo, tamanho, fallback_sysfont="arial"):
    """
    Tenta carregar uma fonte customizada de assets/fonts/<nome_arquivo>.
    Se não existir, usa a fonte de sistema indicada em fallback_sysfont
    (Arial por padrão).
    """
    caminho = os.path.join(FONTS_DIR, nome_arquivo)
    if os.path.isfile(caminho):
        try:
            return pygame.font.Font(caminho, tamanho)
        except pygame.error:
            pass
    return pygame.font.SysFont(fallback_sysfont, tamanho)
