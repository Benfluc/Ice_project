# sprites/platform.py
# Classes de plataforma: a Plataforma comum (fixa) e três variações
# especiais: PlataformaMovel (anda entre dois pontos), PlataformaCaindo
# (cai um tempo depois do herói pisar) e PlataformaQuebradica (quebra
# após algumas pisadas).

import pygame
from settings import (
    IMG_PLATAFORMA, IMG_PLATAFORMA_MOVEL, IMG_PLATAFORMA_CAINDO, IMG_PLATAFORMA_QUEBRADICA,
    VELOCIDADE_PLATAFORMA_MOVEL, TEMPO_TREMER_PLATAFORMA_CAINDO, TEMPO_QUEDA_PLATAFORMA_CAINDO,
    PISADAS_PARA_QUEBRAR
)
from utils import carregar_imagem, carregar_som


class Plataforma(pygame.sprite.Sprite):
    """Plataforma comum, fixa, sólida. Usada para chão e blocos normais."""

    def __init__(self, x, y, largura, altura):
        super().__init__()
        self.image = carregar_imagem(
            IMG_PLATAFORMA,
            tamanho=(largura, altura),
            cor_fallback=(90, 60, 30)
        )
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        # Atributos usados pela física do jogador (mover_e_colidir).
        # Plataformas comuns não se movem e nunca "somem".
        self.delta_x = 0     # quanto essa plataforma se moveu neste frame (eixo x)
        self.delta_y = 0     # quanto essa plataforma se moveu neste frame (eixo y)
        self.solida = True   # se False, o jogador atravessa (usado quando quebra/cai)

    def atualizar(self):
        """Plataforma comum não tem comportamento próprio; existe para
        manter a mesma interface das plataformas especiais."""
        self.delta_x = 0
        self.delta_y = 0

    def desenhar(self, tela, deslocamento_camera):
        if not self.solida and not getattr(self, "visivel_quebrada", True):
            return
        pos = (self.rect.x - deslocamento_camera, self.rect.y)
        tela.blit(self.image, pos)


class PlataformaMovel(Plataforma):
    """
    Plataforma que anda continuamente entre dois pontos (vai e volta).
    Pode se mover na horizontal OU na vertical - defina apenas um dos
    pares de limite (veja eixo).

    eixo: "horizontal" ou "vertical"
    ponto_inicial / ponto_final: as duas posições entre as quais ela
    oscila (no eixo escolhido - x para horizontal, y para vertical).
    """

    def __init__(self, x, y, largura, altura, ponto_final, eixo="horizontal",
                 velocidade=None):
        super().__init__(x, y, largura, altura)
        # Reaproveita o carregamento, mas com a textura própria de
        # plataforma móvel (cai no mesmo placeholder se não existir).
        self.image = carregar_imagem(
            IMG_PLATAFORMA_MOVEL,
            tamanho=(largura, altura),
            cor_fallback=(70, 110, 150)
        )

        self.eixo = eixo
        self.velocidade = velocidade if velocidade is not None else VELOCIDADE_PLATAFORMA_MOVEL

        if eixo == "horizontal":
            self.ponto_inicial = x
            self.ponto_final = ponto_final
        else:  # vertical
            self.ponto_inicial = y
            self.ponto_final = ponto_final

        self.sentido = 1  # 1 = andando para ponto_final, -1 = voltando

    def atualizar(self):
        movimento = self.velocidade * self.sentido

        if self.eixo == "horizontal":
            self.rect.x += movimento
            self.delta_x = movimento
            self.delta_y = 0
            limite_min = min(self.ponto_inicial, self.ponto_final)
            limite_max = max(self.ponto_inicial, self.ponto_final)
            if self.rect.x <= limite_min:
                self.rect.x = limite_min
                self.sentido = 1
            elif self.rect.x >= limite_max:
                self.rect.x = limite_max
                self.sentido = -1
        else:  # vertical
            self.rect.y += movimento
            self.delta_x = 0
            self.delta_y = movimento
            limite_min = min(self.ponto_inicial, self.ponto_final)
            limite_max = max(self.ponto_inicial, self.ponto_final)
            if self.rect.y <= limite_min:
                self.rect.y = limite_min
                self.sentido = 1
            elif self.rect.y >= limite_max:
                self.rect.y = limite_max
                self.sentido = -1


class PlataformaCaindo(Plataforma):
    """
    Plataforma que parece normal, mas começa a tremer assim que o
    herói pisa nela, e depois de um tempo cai (deixa de ser sólida e
    desliza para fora da tela) até desaparecer.

    Use o método notificar_pisada() quando o jogador estiver apoiado
    nela (chamado pela tela de jogo a cada frame em que há contato).
    """

    def __init__(self, x, y, largura, altura):
        super().__init__(x, y, largura, altura)
        self.image_normal = carregar_imagem(
            IMG_PLATAFORMA_CAINDO,
            tamanho=(largura, altura),
            cor_fallback=(160, 130, 60)
        )
        self.image = self.image_normal

        self.estado = "normal"  # normal | tremendo | caindo | destruida
        self.timer = 0
        self.visivel_quebrada = True

    def notificar_pisada(self):
        if self.estado == "normal":
            self.estado = "tremendo"
            self.timer = TEMPO_TREMER_PLATAFORMA_CAINDO

    def atualizar(self):
        self.delta_x = 0
        self.delta_y = 0

        if self.estado == "tremendo":
            self.timer -= 1
            # Pequeno tremor visual (desloca a imagem +-2px)
            deslocamento = 2 if (self.timer // 3) % 2 == 0 else -2
            self._offset_tremor = deslocamento
            if self.timer <= 0:
                self.estado = "caindo"
                self.timer = TEMPO_QUEDA_PLATAFORMA_CAINDO
                self.solida = False  # já não sustenta o jogador

        elif self.estado == "caindo":
            self.timer -= 1
            self.rect.y += 6  # cai/desliza para fora da tela
            self.delta_y = 6
            if self.timer <= 0:
                self.estado = "destruida"
                self.visivel_quebrada = False
                self.kill()

    def desenhar(self, tela, deslocamento_camera):
        if self.estado == "destruida":
            return
        offset = getattr(self, "_offset_tremor", 0) if self.estado == "tremendo" else 0
        pos = (self.rect.x - deslocamento_camera + offset, self.rect.y)
        tela.blit(self.image, pos)


class PlataformaQuebradica(Plataforma):
    """
    Plataforma que quebra depois de ser pisada algumas vezes (cada
    "pisada" conta quando o jogador aterriza nela vindo de cima).
    Após o número configurado de pisadas, ela desaparece de vez.
    """

    def __init__(self, x, y, largura, altura, pisadas_para_quebrar=None):
        super().__init__(x, y, largura, altura)
        self.image = carregar_imagem(
            IMG_PLATAFORMA_QUEBRADICA,
            tamanho=(largura, altura),
            cor_fallback=(150, 90, 90)
        )
        self.pisadas_maximas = (
            pisadas_para_quebrar if pisadas_para_quebrar is not None else PISADAS_PARA_QUEBRAR
        )
        self.pisadas_restantes = self.pisadas_maximas
        self.ja_pisada_neste_contato = False
        self.quebrada = False
        self.som_quebra = carregar_som("platform_break.wav")

    def notificar_pisada(self):
        """Chamado pela tela de jogo quando o herói aterriza em cima."""
        if self.quebrada or self.ja_pisada_neste_contato:
            return
        self.ja_pisada_neste_contato = True
        self.pisadas_restantes -= 1
        if self.pisadas_restantes <= 0:
            self.quebrada = True
            self.solida = False
            if self.som_quebra:
                self.som_quebra.play()
            self.kill()

    def notificar_saida(self):
        """Chamado quando o herói deixa de estar em contato (reseta o
        controle de 'já contou essa pisada')."""
        self.ja_pisada_neste_contato = False

    def atualizar(self):
        self.delta_x = 0
        self.delta_y = 0

    def desenhar(self, tela, deslocamento_camera):
        if self.quebrada:
            return
        # Visual fica mais "rachado" conforme perde pisadas: aqui usamos
        # transparência crescente como indicador simples sem precisar de
        # sprites extras (substitua por imagens de estágios se quiser).
        alpha = int(255 * (self.pisadas_restantes / self.pisadas_maximas))
        imagem = self.image.copy()
        imagem.set_alpha(max(80, alpha))
        pos = (self.rect.x - deslocamento_camera, self.rect.y)
        tela.blit(imagem, pos)

