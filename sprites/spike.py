# sprites/spike.py
# Classe do Espinho: obstáculo fixo (não sólido - não bloqueia
# movimento) que causa dano ao herói sempre que ele tocar nele,
# independente da direção do contato.

import pygame
from settings import IMG_ESPINHO, DANO_ESPINHO
from utils import carregar_imagem


class Espinho(pygame.sprite.Sprite):
    def __init__(self, x, y, largura=60, altura=44):
        super().__init__()
        self.image = carregar_imagem(
            IMG_ESPINHO,
            tamanho=(largura, altura),
            cor_fallback=(200, 200, 200)
        )
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.dano = DANO_ESPINHO

    def desenhar(self, tela, deslocamento_camera):
        pos = (self.rect.x - deslocamento_camera, self.rect.y)
        tela.blit(self.image, pos)
