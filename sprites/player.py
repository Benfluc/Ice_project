# sprites/player.py
# Classe do Jogador (Herói): movimento horizontal, salto, gravidade,
# colisão com plataformas, vida, invencibilidade temporária e animações
# (idle/parado, walk/andando, jump/pulando).

import pygame
from settings import (
    IMG_HEROI, VELOCIDADE_JOGADOR, FORCA_SALTO, GRAVIDADE,
    VELOCIDADE_MAX_QUEDA, VIDA_INICIAL, INVENCIBILIDADE_FRAMES,
    LARGURA, ALTURA,
    ANIM_HEROI_IDLE, ANIM_HEROI_WALK, ANIM_HEROI_JUMP, VELOCIDADE_ANIM_HEROI
)
from utils import carregar_imagem, carregar_som, carregar_sequencia_animacao, Animacao

TAMANHO_HEROI = (48, 64)


class Jogador(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()

        # ---------- Animações ----------
        # Cada uma carrega "<prefixo>_1.png", "<prefixo>_2.png", etc.
        # Se os arquivos não existirem ainda, cai automaticamente no
        # placeholder colorido (1 frame só, sem animar).
        frames_idle = carregar_sequencia_animacao(
            ANIM_HEROI_IDLE, tamanho=TAMANHO_HEROI, cor_fallback=(70, 130, 200)
        )
        frames_walk = carregar_sequencia_animacao(
            ANIM_HEROI_WALK, tamanho=TAMANHO_HEROI, cor_fallback=(70, 130, 200)
        )
        frames_jump = carregar_sequencia_animacao(
            ANIM_HEROI_JUMP, tamanho=TAMANHO_HEROI, cor_fallback=(70, 130, 200)
        )

        self.animacoes = {
            "idle": Animacao(frames_idle, velocidade=VELOCIDADE_ANIM_HEROI),
            "walk": Animacao(frames_walk, velocidade=VELOCIDADE_ANIM_HEROI),
            "jump": Animacao(frames_jump, velocidade=VELOCIDADE_ANIM_HEROI),
        }
        self.estado_animacao = "idle"

        self.image = self.animacoes[self.estado_animacao].frame_atual
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        # Física
        self.vel_x = 0
        self.vel_y = 0
        self.no_chao = False
        self.olhando_direita = True
        self.plataforma_atual = None  # plataforma sólida em que está apoiado agora (se houver)

        # Status
        self.vida = VIDA_INICIAL
        self.vida_maxima = VIDA_INICIAL
        self.moedas = 0
        self.invencivel = False
        self.timer_invencivel = 0
        self.vivo = True

        # Sons
        self.som_salto = carregar_som("jump.wav")
        self.som_dano = carregar_som("hit.wav")

    def processar_input(self, teclas):
        self.vel_x = 0
        if teclas[pygame.K_LEFT] or teclas[pygame.K_a]:
            self.vel_x = -VELOCIDADE_JOGADOR
            self.olhando_direita = False
        if teclas[pygame.K_RIGHT] or teclas[pygame.K_d]:
            self.vel_x = VELOCIDADE_JOGADOR
            self.olhando_direita = True

    def saltar(self):
        if self.no_chao:
            self.vel_y = FORCA_SALTO
            self.no_chao = False
            if self.som_salto:
                self.som_salto.play()

    def aplicar_gravidade(self):
        self.vel_y += GRAVIDADE
        if self.vel_y > VELOCIDADE_MAX_QUEDA:
            self.vel_y = VELOCIDADE_MAX_QUEDA

    def mover_e_colidir(self, plataformas, limite_mapa_largura):
        # Só plataformas sólidas bloqueiam o jogador (uma plataforma
        # quebrada/caindo deixa de ser sólida e o jogador atravessa).
        plataformas_solidas = [p for p in plataformas if getattr(p, "solida", True)]

        # --- Movimento horizontal ---
        # Se o jogador estava em cima de uma plataforma móvel no frame
        # anterior, ele "anda junto" com ela antes do próprio input.
        if self.no_chao and getattr(self, "plataforma_atual", None) is not None:
            plat = self.plataforma_atual
            self.rect.x += getattr(plat, "delta_x", 0)

        self.rect.x += self.vel_x
        # Limites do mapa (não deixa sair da fase pelos lados)
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > limite_mapa_largura:
            self.rect.right = limite_mapa_largura

        for plataforma in plataformas_solidas:
            if self.rect.colliderect(plataforma.rect):
                if self.vel_x > 0:
                    self.rect.right = plataforma.rect.left
                elif self.vel_x < 0:
                    self.rect.left = plataforma.rect.right

        # --- Movimento vertical ---
        self.aplicar_gravidade()
        self.rect.y += self.vel_y
        estava_no_chao = self.no_chao
        self.no_chao = False
        plataforma_anterior = getattr(self, "plataforma_atual", None)
        self.plataforma_atual = None

        for plataforma in plataformas_solidas:
            if self.rect.colliderect(plataforma.rect):
                if self.vel_y > 0:
                    self.rect.bottom = plataforma.rect.top
                    self.vel_y = 0
                    self.no_chao = True
                    self.plataforma_atual = plataforma
                    if hasattr(plataforma, "notificar_pisada"):
                        plataforma.notificar_pisada()
                elif self.vel_y < 0:
                    self.rect.top = plataforma.rect.bottom
                    self.vel_y = 0

        # Se saiu de cima de uma plataforma quebradiça, avisa ela (para
        # poder contar a próxima pisada como um novo contato).
        if plataforma_anterior is not None and plataforma_anterior is not self.plataforma_atual:
            if hasattr(plataforma_anterior, "notificar_saida"):
                plataforma_anterior.notificar_saida()

        # Se cair no vazio (fora da tela por baixo), perde vida
        if self.rect.top > ALTURA + 200:
            self.receber_dano(self.vida)  # morte instantânea ao cair no abismo

    def receber_dano(self, quantidade=1):
        if self.invencivel or not self.vivo:
            return
        self.vida -= quantidade
        if self.som_dano:
            self.som_dano.play()
        if self.vida <= 0:
            self.vida = 0
            self.vivo = False
        else:
            self.invencivel = True
            self.timer_invencivel = INVENCIBILIDADE_FRAMES

    def atualizar_invencibilidade(self):
        if self.invencivel:
            self.timer_invencivel -= 1
            if self.timer_invencivel <= 0:
                self.invencivel = False

    def coletar_moeda(self):
        self.moedas += 1

    def atualizar_estado_animacao(self):
        """Decide qual animação (idle/walk/jump) deve estar ativa agora."""
        if not self.no_chao:
            novo_estado = "jump"
        elif self.vel_x != 0:
            novo_estado = "walk"
        else:
            novo_estado = "idle"

        if novo_estado != self.estado_animacao:
            self.estado_animacao = novo_estado
            self.animacoes[self.estado_animacao].reiniciar()

        self.animacoes[self.estado_animacao].atualizar()
        self.image = self.animacoes[self.estado_animacao].frame_atual

    def imagem_com_direcao(self):
        if self.olhando_direita:
            return self.image
        return pygame.transform.flip(self.image, True, False)

    def desenhar(self, tela, deslocamento_camera):
        # Pisca enquanto invencível
        if self.invencivel and (self.timer_invencivel // 5) % 2 == 0:
            return
        imagem_atual = self.imagem_com_direcao()
        pos = (self.rect.x - deslocamento_camera, self.rect.y)
        tela.blit(imagem_atual, pos)

    def atualizar(self, teclas, plataformas, limite_mapa_largura):
        if not self.vivo:
            return
        self.processar_input(teclas)
        self.mover_e_colidir(plataformas, limite_mapa_largura)
        self.atualizar_invencibilidade()
        self.atualizar_estado_animacao()
