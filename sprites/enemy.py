# sprites/enemy.py
# Classes de monstro:
#   - Inimigo (monstro de patrulha clássico - anda no chão entre dois pontos)
#   - MonstroVoador (se move livremente no ar, num padrão de voo)
#   - MonstroAtirador (fica numa posição/patrulha curta e dispara projéteis)
#
# Todos podem ser derrotados pulando em cima deles (exceto quando
# explicitamente indicado), e causam dano ao herói em colisão lateral.

import pygame
import math
from settings import (
    IMG_INIMIGO, VELOCIDADE_INIMIGO,
    ANIM_MONSTRO_IDLE, ANIM_MONSTRO_WALK, VELOCIDADE_ANIM_MONSTRO,
    VELOCIDADE_MONSTRO_VOADOR, ANIM_MONSTRO_VOADOR_VOAR, VELOCIDADE_ANIM_MONSTRO_VOADOR,
    ANIM_MONSTRO_ATIRADOR_IDLE, VELOCIDADE_ANIM_MONSTRO_ATIRADOR, INTERVALO_TIRO_ATIRADOR
)
from utils import carregar_imagem, carregar_som, carregar_sequencia_animacao, Animacao
from sprites.projectile import Projetil

TAMANHO_MONSTRO = (48, 60)


class Inimigo(pygame.sprite.Sprite):
    """Monstro clássico: patrulha andando no chão entre dois pontos."""

    def __init__(self, x, y, distancia_patrulha=120):
        super().__init__()

        # ---------- Animações ----------
        frames_idle = carregar_sequencia_animacao(
            ANIM_MONSTRO_IDLE, tamanho=TAMANHO_MONSTRO, cor_fallback=(200, 60, 60)
        )
        frames_walk = carregar_sequencia_animacao(
            ANIM_MONSTRO_WALK, tamanho=TAMANHO_MONSTRO, cor_fallback=(200, 60, 60)
        )

        self.animacoes = {
            "idle": Animacao(frames_idle, velocidade=VELOCIDADE_ANIM_MONSTRO),
            "walk": Animacao(frames_walk, velocidade=VELOCIDADE_ANIM_MONSTRO),
        }
        # O monstro patrulha o tempo todo, então começa direto andando.
        self.estado_animacao = "walk"

        self.image = self.animacoes[self.estado_animacao].frame_atual
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        # Patrulha horizontal entre [x_inicial, x_inicial + distancia]
        self.x_inicial = x
        self.x_final = x + distancia_patrulha
        self.vel_x = VELOCIDADE_INIMIGO

        self.derrotavel_pulando_em_cima = True
        self.dano = 1
        self.derrotado = False
        self.som_derrota = carregar_som("enemy_defeat.wav")

    def atualizar(self, *_args, **_kwargs):
        if self.derrotado:
            return

        self.rect.x += self.vel_x

        if self.rect.x <= self.x_inicial:
            self.rect.x = self.x_inicial
            self.vel_x = abs(self.vel_x)
        elif self.rect.x >= self.x_final:
            self.rect.x = self.x_final
            self.vel_x = -abs(self.vel_x)

        # Sempre "walk" enquanto patrulha (distância > 0). Caso algum dia
        # exista um monstro estático (distancia_patrulha=0), ele fica em idle.
        novo_estado = "walk" if self.x_inicial != self.x_final else "idle"
        if novo_estado != self.estado_animacao:
            self.estado_animacao = novo_estado
            self.animacoes[self.estado_animacao].reiniciar()

        self.animacoes[self.estado_animacao].atualizar()
        self.image = self.animacoes[self.estado_animacao].frame_atual

    def imagem_com_direcao(self):
        if self.vel_x >= 0:
            return self.image
        return pygame.transform.flip(self.image, True, False)

    def derrotar(self):
        self.derrotado = True
        if self.som_derrota:
            self.som_derrota.play()
        self.kill()

    def desenhar(self, tela, deslocamento_camera):
        if not self.derrotado:
            pos = (self.rect.x - deslocamento_camera, self.rect.y)
            tela.blit(self.imagem_com_direcao(), pos)


class MonstroVoador(pygame.sprite.Sprite):
    """
    Monstro que se move livremente no ar, sem precisar de chão/plataforma
    embaixo. Voa em um padrão senoidal entre dois pontos horizontais,
    subindo e descendo suavemente - útil para sobrevoar abismos ou
    plataformas, forçando o jogador a desviar no ar.

    amplitude_vertical: quantos pixels ele sobe/desce em relação a y
    """

    def __init__(self, x, y, distancia_patrulha=160, amplitude_vertical=40):
        super().__init__()

        frames_voar = carregar_sequencia_animacao(
            ANIM_MONSTRO_VOADOR_VOAR, tamanho=TAMANHO_MONSTRO, cor_fallback=(160, 70, 200)
        )
        self.animacao = Animacao(frames_voar, velocidade=VELOCIDADE_ANIM_MONSTRO_VOADOR)

        self.image = self.animacao.frame_atual
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        self.x_inicial = x
        self.x_final = x + distancia_patrulha
        self.y_base = y
        self.amplitude_vertical = amplitude_vertical
        self.vel_x = VELOCIDADE_MONSTRO_VOADOR
        self.tempo = 0.0

        self.derrotavel_pulando_em_cima = True
        self.dano = 1
        self.derrotado = False
        self.som_derrota = carregar_som("enemy_defeat.wav")

    def atualizar(self, *_args, **_kwargs):
        if self.derrotado:
            return

        self.rect.x += self.vel_x
        if self.rect.x <= self.x_inicial:
            self.rect.x = self.x_inicial
            self.vel_x = abs(self.vel_x)
        elif self.rect.x >= self.x_final:
            self.rect.x = self.x_final
            self.vel_x = -abs(self.vel_x)

        # Movimento vertical senoidal (sobe e desce suavemente)
        self.tempo += 0.06
        self.rect.y = self.y_base + int(math.sin(self.tempo) * self.amplitude_vertical)

        self.animacao.atualizar()
        self.image = self.animacao.frame_atual

    def imagem_com_direcao(self):
        if self.vel_x >= 0:
            return self.image
        return pygame.transform.flip(self.image, True, False)

    def derrotar(self):
        self.derrotado = True
        if self.som_derrota:
            self.som_derrota.play()
        self.kill()

    def desenhar(self, tela, deslocamento_camera):
        if not self.derrotado:
            pos = (self.rect.x - deslocamento_camera, self.rect.y)
            tela.blit(self.imagem_com_direcao(), pos)


class MonstroAtirador(pygame.sprite.Sprite):
    """
    Monstro que fica numa posição (ou faz uma patrulha curta/opcional)
    e dispara projéteis periodicamente na direção em que está olhando.
    Não é derrotável pulando em cima por padrão (já que normalmente é
    posicionado para ser evitado/atacado à distância) - mas pode ser
    configurado como derrotável também.
    """

    def __init__(self, x, y, direcao_inicial=-1, distancia_patrulha=0,
                 derrotavel_pulando_em_cima=True):
        super().__init__()

        frames_idle = carregar_sequencia_animacao(
            ANIM_MONSTRO_ATIRADOR_IDLE, tamanho=TAMANHO_MONSTRO, cor_fallback=(90, 90, 200)
        )
        self.animacao = Animacao(frames_idle, velocidade=VELOCIDADE_ANIM_MONSTRO_ATIRADOR)

        self.image = self.animacao.frame_atual
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        self.x_inicial = x
        self.x_final = x + distancia_patrulha
        self.vel_x = VELOCIDADE_INIMIGO if distancia_patrulha != 0 else 0
        self.direcao = 1 if direcao_inicial >= 0 else -1

        self.timer_tiro = INTERVALO_TIRO_ATIRADOR
        self.projeteis = pygame.sprite.Group()

        self.derrotavel_pulando_em_cima = derrotavel_pulando_em_cima
        self.dano = 1
        self.derrotado = False
        self.som_derrota = carregar_som("enemy_defeat.wav")
        self.som_tiro = carregar_som("shoot.wav")

    def atualizar(self, plataformas=None, limite_mapa_largura=10_000):
        if self.derrotado:
            return

        # Patrulha curta opcional (se distancia_patrulha=0, fica parado)
        if self.vel_x != 0:
            self.rect.x += self.vel_x
            if self.rect.x <= self.x_inicial:
                self.rect.x = self.x_inicial
                self.vel_x = abs(self.vel_x)
                self.direcao = 1
            elif self.rect.x >= self.x_final:
                self.rect.x = self.x_final
                self.vel_x = -abs(self.vel_x)
                self.direcao = -1

        self.animacao.atualizar()
        self.image = self.animacao.frame_atual

        # Disparo periódico
        self.timer_tiro -= 1
        if self.timer_tiro <= 0:
            self.timer_tiro = INTERVALO_TIRO_ATIRADOR
            self.disparar()

        # Atualiza os projéteis já disparados por este monstro
        if plataformas is not None:
            for projetil in list(self.projeteis):
                projetil.atualizar(plataformas, limite_mapa_largura)

    def disparar(self):
        origem_x = self.rect.centerx + (self.rect.width // 2 * self.direcao)
        origem_y = self.rect.centery - 6
        projetil = Projetil(origem_x, origem_y, self.direcao)
        self.projeteis.add(projetil)
        if self.som_tiro:
            self.som_tiro.play()

    def imagem_com_direcao(self):
        if self.direcao >= 0:
            return self.image
        return pygame.transform.flip(self.image, True, False)

    def derrotar(self):
        self.derrotado = True
        if self.som_derrota:
            self.som_derrota.play()
        self.kill()

    def desenhar(self, tela, deslocamento_camera):
        if not self.derrotado:
            pos = (self.rect.x - deslocamento_camera, self.rect.y)
            tela.blit(self.imagem_com_direcao(), pos)
        for projetil in self.projeteis:
            projetil.desenhar(tela, deslocamento_camera)
