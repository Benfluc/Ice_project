# menu.py
# Menu principal do jogo com as opções: Iniciar, Tutorial e Sair.
# Inclui também a tela de Tutorial (mostra os comandos do jogo).

import pygame
import sys

from settings import (
    LARGURA, ALTURA, BRANCO, PRETO, CINZA, CINZA_CLARO, AZUL_CEU, AZUL_ESCURO,
    VERDE, VERDE_CLARO, AZUL_ESCURO, AMARELO, IMG_MENU_BACKGROUND, MUSICA_MENU,
    FONTE_TUTORIAL
)
from utils import carregar_imagem, carregar_fonte, tocar_musica
import save_data
from level import TOTAL_FASES, construir_fase


class Botao:
    """Botão simples e reutilizável para o menu."""

    def __init__(self, texto, x, y, largura, altura, fonte):
        self.texto = texto
        self.rect = pygame.Rect(x, y, largura, altura)
        self.fonte = fonte
        self.hover = False

    def atualizar_hover(self, pos_mouse):
        self.hover = self.rect.collidepoint(pos_mouse)

    def clicado(self, evento):
        return (
            evento.type == pygame.MOUSEBUTTONDOWN
            and evento.button == 1
            and self.rect.collidepoint(evento.pos)
        )

    def desenhar(self, tela):
        cor_fundo = AZUL_ESCURO if self.hover else AZUL_CEU
        cor_borda = BRANCO
        pygame.draw.rect(tela, cor_fundo, self.rect, border_radius=10)
        pygame.draw.rect(tela, cor_borda, self.rect, width=3, border_radius=10)

        texto_render = self.fonte.render(self.texto, True, PRETO)
        pos_x = self.rect.centerx - texto_render.get_width() // 2
        pos_y = self.rect.centery - texto_render.get_height() // 2
        tela.blit(texto_render, (pos_x, pos_y))


class TelaMenu:
    """Tela do menu principal."""

    def __init__(self, tela):
        self.tela = tela
        self.fonte_titulo = carregar_fonte("fonte.ttf", 56)
        self.fonte_botao = carregar_fonte("fonte.ttf", 32)
        self.fonte_rodape = carregar_fonte("fonte.ttf", 18)

        self.background = carregar_imagem(
            IMG_MENU_BACKGROUND, tamanho=(LARGURA, ALTURA), cor_fallback=AZUL_ESCURO
        )

        largura_botao, altura_botao = 285, 50
        espacamento = 12
        centro_x = LARGURA // 2 - largura_botao // 2
        y_inicial = 215

        self.botao_iniciar = Botao(
            "Iniciar", centro_x, y_inicial, largura_botao, altura_botao, self.fonte_botao
        )
        self.botao_selecionar_fase = Botao(
            "Selecionar Fase", centro_x, y_inicial + (altura_botao + espacamento),
            largura_botao, altura_botao, self.fonte_botao
        )
        self.botao_tutorial = Botao(
            "Tutorial", centro_x, y_inicial + 2 * (altura_botao + espacamento),
            largura_botao, altura_botao, self.fonte_botao
        )
        self.botao_sair = Botao(
            "Sair", centro_x, y_inicial + 3 * (altura_botao + espacamento),
            largura_botao, altura_botao, self.fonte_botao
        )

        tocar_musica(MUSICA_MENU, loop=True, volume=0.4)

    def processar_eventos(self):
        """
        Retorna uma string com a ação escolhida: "iniciar",
        "selecionar_fase", "tutorial", "sair" ou None se nada foi
        clicado neste frame.
        """
        pos_mouse = pygame.mouse.get_pos()
        self.botao_iniciar.atualizar_hover(pos_mouse)
        self.botao_selecionar_fase.atualizar_hover(pos_mouse)
        self.botao_tutorial.atualizar_hover(pos_mouse)
        self.botao_sair.atualizar_hover(pos_mouse)

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if self.botao_iniciar.clicado(evento):
                return "iniciar"
            if self.botao_selecionar_fase.clicado(evento):
                return "selecionar_fase"
            if self.botao_tutorial.clicado(evento):
                return "tutorial"
            if self.botao_sair.clicado(evento):
                return "sair"

            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
                return "sair"

        return None

    def desenhar(self):
        self.tela.blit(self.background, (0, 0))

        titulo_texto = self.fonte_titulo.render("Ice Adventure", True, BRANCO)
        self.tela.blit(
            titulo_texto,
            (LARGURA // 2 - titulo_texto.get_width() // 2, 130)
        )

        self.botao_iniciar.desenhar(self.tela)
        self.botao_selecionar_fase.desenhar(self.tela)
        self.botao_tutorial.desenhar(self.tela)
        self.botao_sair.desenhar(self.tela)

        rodape = self.fonte_rodape.render("Use o mouse para navegar pelo menu", True, PRETO)
        self.tela.blit(rodape, (LARGURA // 2 - rodape.get_width() // 2, ALTURA - 40))

    def rodar_frame(self):
        acao = self.processar_eventos()
        self.desenhar()
        return acao


class BotaoFase(Botao):
    """
    Botão de uma fase específica na tela de seleção. Pode estar
    bloqueado (fase ainda não desbloqueada) - nesse caso aparece
    acinzentado e não reage a cliques.
    """

    def __init__(self, numero_fase, nome_fase, x, y, largura, altura, fonte, desbloqueada):
        super().__init__(nome_fase, x, y, largura, altura, fonte)
        self.numero_fase = numero_fase
        self.desbloqueada = desbloqueada

    def clicado(self, evento):
        if not self.desbloqueada:
            return False
        return super().clicado(evento)

    def desenhar(self, tela):
        if not self.desbloqueada:
            cor_fundo = (90, 90, 90)
            cor_borda = (140, 140, 140)
            cor_texto = (160, 160, 160)
        else:
            cor_fundo = AZUL_CEU if self.hover else AZUL_ESCURO
            cor_borda = BRANCO
            cor_texto = PRETO

        pygame.draw.rect(tela, cor_fundo, self.rect, border_radius=10)
        pygame.draw.rect(tela, cor_borda, self.rect, width=3, border_radius=10)

        texto_render = self.fonte.render(self.texto, True, cor_texto)
        pos_x = self.rect.centerx - texto_render.get_width() // 2
        pos_y = self.rect.centery - texto_render.get_height() // 2 - (6 if not self.desbloqueada else 0)
        tela.blit(texto_render, (pos_x, pos_y))

        if not self.desbloqueada:
            fonte_cadeado = pygame.font.SysFont("arial", 16)
            texto_cadeado = fonte_cadeado.render("Bloqueada", True, cor_texto)
            pos_x2 = self.rect.centerx - texto_cadeado.get_width() // 2
            tela.blit(texto_cadeado, (pos_x2, pos_y + texto_render.get_height() + 2))


class TelaSelecaoFase:
    """
    Tela de seleção de fase: mostra um botão para cada fase do jogo.
    Fases além da mais avançada já desbloqueada aparecem bloqueadas
    (acinzentadas, não clicáveis). Selecionar uma fase desbloqueada
    inicia o jogo direto a partir dela (vida/moedas começam do zero,
    igual a qualquer início de fase).
    """

    def __init__(self, tela):
        self.tela = tela
        self.fonte_titulo = carregar_fonte("fonte.ttf", 44)
        self.fonte_botao = carregar_fonte("fonte.ttf", 26)
        self.fonte_rodape = carregar_fonte("fonte.ttf", 18)

        self.background = carregar_imagem(
            IMG_MENU_BACKGROUND, tamanho=(LARGURA, ALTURA), cor_fallback=AZUL_ESCURO
        )

        self.fase_desbloqueada_ate = save_data.obter_fase_desbloqueada()

        # Monta um botão por fase existente no jogo (TOTAL_FASES vem
        # de level.py, então isso se adapta automaticamente se você
        # adicionar mais fases no futuro).
        self.botoes_fase = []
        largura_botao, altura_botao = 220, 70
        espacamento = 20
        colunas = min(TOTAL_FASES, 4)
        total_largura = colunas * largura_botao + (colunas - 1) * espacamento
        x_inicial = LARGURA // 2 - total_largura // 2
        y_inicial = 220

        for indice in range(TOTAL_FASES):
            numero_fase = indice + 1
            nome_fase = construir_fase(numero_fase)["nome"]
            linha = indice // colunas
            coluna = indice % colunas
            x = x_inicial + coluna * (largura_botao + espacamento)
            y = y_inicial + linha * (altura_botao + espacamento)
            desbloqueada = numero_fase <= self.fase_desbloqueada_ate

            self.botoes_fase.append(
                BotaoFase(numero_fase, nome_fase, x, y, largura_botao, altura_botao,
                          self.fonte_botao, desbloqueada)
            )

        largura_voltar, altura_voltar = 200, 50
        self.botao_voltar = Botao(
            "Voltar", LARGURA // 2 - largura_voltar // 2, ALTURA - 80,
            largura_voltar, altura_voltar, self.fonte_botao
        )

    def processar_eventos(self):
        """
        Retorna ("jogar", numero_fase) se uma fase desbloqueada foi
        escolhida, "menu" se o jogador pediu para voltar, ou None.
        """
        pos_mouse = pygame.mouse.get_pos()
        for botao in self.botoes_fase:
            botao.atualizar_hover(pos_mouse)
        self.botao_voltar.atualizar_hover(pos_mouse)

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            for botao in self.botoes_fase:
                if botao.clicado(evento):
                    return ("jogar", botao.numero_fase)

            if self.botao_voltar.clicado(evento):
                return "menu"

            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
                return "menu"

        return None

    def desenhar(self):
        self.tela.blit(self.background, (0, 0))

        overlay = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 90))
        self.tela.blit(overlay, (0, 0))

        titulo = self.fonte_titulo.render("Selecionar Fase", True, BRANCO)
        self.tela.blit(titulo, (LARGURA // 2 - titulo.get_width() // 2, 110))

        for botao in self.botoes_fase:
            botao.desenhar(self.tela)

        self.botao_voltar.desenhar(self.tela)

        rodape = self.fonte_rodape.render(
            "Vença uma fase para desbloquear a próxima", True, PRETO
        )
        self.tela.blit(rodape, (LARGURA // 2 - rodape.get_width() // 2, ALTURA - 30))

    def rodar_frame(self):
        acao = self.processar_eventos()
        self.desenhar()
        return acao


class TelaTutorial:
    """Pequena janela/tela com os comandos do jogo."""

    def __init__(self, tela):
        self.tela = tela
        # Fonte separada da usada no menu/HUD, só para esta tela.
        # Se assets/fonts/fonte_tutorial.ttf não existir, usa um sysfont
        # diferente do Arial (Consolas) como alternativa visual.
        self.fonte_titulo = carregar_fonte(FONTE_TUTORIAL, 38, fallback_sysfont="consolas")
        self.fonte_texto = carregar_fonte(FONTE_TUTORIAL, 20, fallback_sysfont="consolas")
        self.fonte_botao = carregar_fonte(FONTE_TUTORIAL, 24, fallback_sysfont="consolas")

        # "Pequena janela" central com os comandos, sobre um fundo escurecido
        largura_janela, altura_janela = 680, 420
        self.rect_janela = pygame.Rect(
            LARGURA // 2 - largura_janela // 2,
            ALTURA // 2 - altura_janela // 2,
            largura_janela,
            altura_janela
        )

        self.comandos = [
            ("← / A", "Move para a esquerda"),
            ("→ / D", "Move para a direita"),
            ("ESPAÇO / ↑ / W", "Salta"),
            ("Pular sobre o monstro", "Derrota o inimigo"),
            ("Chegar ao portal", "Vence a fase"),
            ("ESC", "Volta ao menu"),
        ]

        largura_botao, altura_botao = 200, 50
        self.botao_voltar = Botao(
            "Voltar",
            LARGURA // 2 - largura_botao // 2,
            self.rect_janela.bottom - 70,
            largura_botao,
            altura_botao,
            self.fonte_botao
        )

    def processar_eventos(self):
        pos_mouse = pygame.mouse.get_pos()
        self.botao_voltar.atualizar_hover(pos_mouse)

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if self.botao_voltar.clicado(evento):
                return "menu"

            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
                return "menu"

        return None

    def desenhar(self):
        # Fundo escurecido (a "tela de trás")
        self.tela.fill(AZUL_ESCURO)
        overlay = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        self.tela.blit(overlay, (0, 0))

        # "Janela" do tutorial
        pygame.draw.rect(self.tela, CINZA, self.rect_janela, border_radius=14)
        pygame.draw.rect(self.tela, BRANCO, self.rect_janela, width=3, border_radius=14)

        titulo = self.fonte_titulo.render("Como Jogar", True, AMARELO)
        self.tela.blit(
            titulo,
            (self.rect_janela.centerx - titulo.get_width() // 2, self.rect_janela.top + 20)
        )

        y = self.rect_janela.top + 95
        largura_maxima = self.rect_janela.width - 60  # margem de 30px de cada lado

        for tecla, descricao in self.comandos:
            linha = f"{tecla}  -  {descricao}"
            texto_render = self.fonte_texto.render(linha, True, BRANCO)

            if texto_render.get_width() <= largura_maxima:
                self.tela.blit(texto_render, (self.rect_janela.left + 30, y))
                y += 34
            else:
                # Quebra em duas linhas (tecla numa linha, descrição na outra)
                texto_tecla = self.fonte_texto.render(tecla, True, AMARELO)
                texto_descricao = self.fonte_texto.render(descricao, True, BRANCO)
                self.tela.blit(texto_tecla, (self.rect_janela.left + 30, y))
                y += 28
                self.tela.blit(texto_descricao, (self.rect_janela.left + 30, y))
                y += 34

        self.botao_voltar.desenhar(self.tela)

    def rodar_frame(self):
        acao = self.processar_eventos()
        self.desenhar()
        return acao
