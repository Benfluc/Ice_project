# sprites/coin.py
# Classe da Moeda: item coletável que aumenta a pontuação do jogador.

import pygame
import math
from settings import IMG_MOEDA
from utils import carregar_imagem, carregar_som


class Moeda(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = carregar_imagem(IMG_MOEDA, tamanho=(28, 28), cor_fallback=(240, 200, 40))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        self.y_original = y
        self.tempo = 0  # usado para animação de flutuação

        self.som_coleta = carregar_som("coin.wav")
        self.coletada = False

    def atualizar(self):
        # Pequena animação de flutuação (sobe e desce suavemente)
        self.tempo += 0.1
        self.rect.y = self.y_original + int(math.sin(self.tempo) * 4)

    def coletar(self):
        self.coletada = True
        if self.som_coleta:
            self.som_coleta.play()

    def desenhar(self, tela, deslocamento_camera):
        if not self.coletada:
            pos = (self.rect.x - deslocamento_camera, self.rect.y)
            tela.blit(self.image, pos)
