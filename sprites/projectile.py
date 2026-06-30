# sprites/projectile.py
# Classe do Projétil: disparado pelo MonstroAtirador, viaja em linha
# reta horizontal até sair da fase ou colidir com o herói/plataforma.

import pygame
from settings import IMG_PROJETIL, VELOCIDADE_PROJETIL, DANO_PROJETIL
from utils import carregar_imagem


class Projetil(pygame.sprite.Sprite):
    def __init__(self, x, y, direcao, largura=30, altura=22):
        """
        direcao: 1 para a direita, -1 para a esquerda.
        largura, altura: tamanho do projétil em pixels.
        """
        super().__init__()
        self.image_base = carregar_imagem(
            IMG_PROJETIL, tamanho=(largura, altura), cor_fallback=(220, 80, 30)
        )
        self.image = (
            self.image_base if direcao >= 0
            else pygame.transform.flip(self.image_base, True, False)
        )
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        self.direcao = 1 if direcao >= 0 else -1
        self.vel_x = VELOCIDADE_PROJETIL * self.direcao
        self.dano = DANO_PROJETIL
        self.ativo = True

    def atualizar(self, plataformas, limite_mapa_largura):
        if not self.ativo:
            return

        self.rect.x += self.vel_x

        # Sai dos limites da fase -> remove
        if self.rect.right < 0 or self.rect.left > limite_mapa_largura:
            self.ativo = False
            self.kill()
            return

        # Colide com alguma plataforma sólida -> remove (some na parede/chão)
        for plataforma in plataformas:
            if getattr(plataforma, "solida", True) and self.rect.colliderect(plataforma.rect):
                self.ativo = False
                self.kill()
                return

    def desenhar(self, tela, deslocamento_camera):
        pos = (self.rect.x - deslocamento_camera, self.rect.y)
        tela.blit(self.image, pos)
