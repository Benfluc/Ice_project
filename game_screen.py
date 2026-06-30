# game_screen.py
# Tela principal de gameplay: roda a fase atual, controla a câmera, o
# HUD (vida, moedas), detecta vitória (chegar na bandeira -> avança de
# fase, ou vence o jogo na última) e derrota (perder toda a vida).

import pygame
import sys
import os

from settings import (
    LARGURA, ALTURA, BRANCO, PRETO, AZUL_CEU, VERMELHO, VERDE,
    AMARELO, IMG_BACKGROUND, IMG_CORACAO, MUSICA_FASE, SOM_VITORIA, SOM_GAMEOVER,
    IMAGES_DIR
)
from sprites.player import Jogador
from level import construir_fase, TOTAL_FASES
from utils import carregar_imagem, carregar_fonte, tocar_musica, parar_musica, carregar_som, desenhar_coracao
import save_data

# Quanto tempo (em frames) a tela de "Fase concluída" fica visível
# antes de carregar a próxima fase automaticamente.
DURACAO_TRANSICAO_FRAMES = 120  # ~2 segundos a 60 FPS


class TelaJogo:
    def __init__(self, tela, fase_inicial=1):
        self.tela = tela
        self.fase_inicial = fase_inicial
        self.fonte_hud = carregar_fonte("fonte.ttf", 28)
        self.fonte_grande = carregar_fonte("fonte.ttf", 64)
        self.fonte_media = carregar_fonte("fonte.ttf", 32)

        self.background = carregar_imagem(IMG_BACKGROUND, tamanho=(LARGURA, ALTURA), cor_fallback=AZUL_CEU)

        # Ícone de coração (vida) no HUD. Se coracao.png não existir,
        # usamos um coração desenhado (fallback) em vez de um placeholder
        # quadrado, pra já ficar com a cara certa.
        self.tem_imagem_coracao = os.path.isfile(os.path.join(IMAGES_DIR, IMG_CORACAO))
        if self.tem_imagem_coracao:
            self.imagem_coracao = carregar_imagem(IMG_CORACAO, tamanho=(28, 28))
            self.imagem_coracao_vazio = self.imagem_coracao.copy()
            self.imagem_coracao_vazio.fill((90, 90, 90, 255), special_flags=pygame.BLEND_RGBA_MULT)

        self.som_vitoria = carregar_som(SOM_VITORIA)
        self.som_gameover = carregar_som(SOM_GAMEOVER)

        # Vida e moedas resetam ao trocar de fase (cada fase começa do zero)
        self.numero_fase = fase_inicial
        self.jogador = None

        self.iniciar_jogo_novo()

    def iniciar_jogo_novo(self):
        """
        Começa o jogo com vida/moedas reiniciadas, a partir da fase
        indicada em self.fase_inicial (normalmente 1, mas pode ser
        outra se o jogador escolheu pelo seletor de fases no menu).
        """
        self.numero_fase = self.fase_inicial
        self.carregar_fase(self.numero_fase)

    def carregar_fase(self, numero_fase):
        """
        Carrega os dados da fase indicada. O jogador é sempre recriado
        do zero (vida cheia, 0 moedas), já que vida e moedas resetam a
        cada fase.
        """
        dados_fase = construir_fase(numero_fase)
        self.nome_fase = dados_fase["nome"]
        self.plataformas = dados_fase["plataformas"]
        self.moedas = dados_fase["moedas"]
        self.inimigos = dados_fase["inimigos"]
        self.espinhos = dados_fase.get("espinhos", pygame.sprite.Group())
        self.bandeira = dados_fase["bandeira"]
        self.largura_fase = dados_fase["largura_fase"]

        # Background: usa o da fase se especificado, senão o padrão
        nome_background = dados_fase.get("imagem_background")
        if nome_background:
            self.background = carregar_imagem(nome_background, tamanho=(LARGURA, ALTURA), cor_fallback=AZUL_CEU)
        else:
            self.background = carregar_imagem(IMG_BACKGROUND, tamanho=(LARGURA, ALTURA), cor_fallback=AZUL_CEU)

        self.jogador = Jogador(50, ALTURA - 120)

        self.camera_x = 0
        self.estado = "jogando"  # jogando | transicao_fase | venceu | perdeu
        self.timer_transicao = 0
        self.som_finalizacao_tocado = False

        tocar_musica(MUSICA_FASE, loop=True, volume=0.4)

    def reiniciar(self):
        """Reinicia o jogo inteiro do começo (usado após vitória/derrota final)."""
        self.iniciar_jogo_novo()

    def atualizar_camera(self):
        """Centraliza a câmera no jogador, limitando às bordas da fase."""
        alvo = self.jogador.rect.centerx - LARGURA // 2
        alvo = max(0, min(alvo, self.largura_fase - LARGURA))
        self.camera_x = alvo

    def checar_colisoes_moedas(self):
        for moeda in self.moedas:
            if not moeda.coletada and self.jogador.rect.colliderect(moeda.rect):
                moeda.coletar()
                self.jogador.coletar_moeda()

    def checar_colisoes_inimigos(self):
        for inimigo in list(self.inimigos):
            if inimigo.derrotado:
                continue
            if self.jogador.rect.colliderect(inimigo.rect):
                derrotavel = getattr(inimigo, "derrotavel_pulando_em_cima", True)
                caindo_por_cima = (
                    derrotavel and
                    self.jogador.vel_y > 0 and
                    self.jogador.rect.bottom - inimigo.rect.top < 25
                )
                if caindo_por_cima:
                    inimigo.derrotar()
                    self.jogador.vel_y = -10  # pequeno "ricochete" ao pisar no inimigo
                else:
                    self.jogador.receber_dano(getattr(inimigo, "dano", 1))

            # Projéteis disparados por este inimigo (se for um atirador)
            projeteis = getattr(inimigo, "projeteis", None)
            if projeteis:
                for projetil in list(projeteis):
                    if projetil.ativo and self.jogador.rect.colliderect(projetil.rect):
                        self.jogador.receber_dano(getattr(projetil, "dano", 1))
                        projetil.ativo = False
                        projetil.kill()

    def checar_colisoes_espinhos(self):
        for espinho in self.espinhos:
            if self.jogador.rect.colliderect(espinho.rect):
                self.jogador.receber_dano(getattr(espinho, "dano", 1))

    def checar_vitoria(self):
        if not self.jogador.rect.colliderect(self.bandeira.rect):
            return

        if self.numero_fase >= TOTAL_FASES:
            # Última fase concluída -> vitória final do jogo.
            # Garante que tudo fica marcado como desbloqueado.
            save_data.desbloquear_fase(TOTAL_FASES)
            self.estado = "venceu"
        else:
            # Desbloqueia a próxima fase permanentemente no save
            save_data.desbloquear_fase(self.numero_fase + 1)
            # Ainda há próxima fase -> mostra transição e depois avança
            self.estado = "transicao_fase"
            self.timer_transicao = DURACAO_TRANSICAO_FRAMES
            parar_musica()

    def processar_eventos(self):
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    return "menu"  # volta ao menu
                if evento.key in (pygame.K_SPACE, pygame.K_UP, pygame.K_w):
                    if self.estado == "jogando":
                        self.jogador.saltar()
                if evento.key == pygame.K_RETURN:
                    if self.estado in ("venceu", "perdeu"):
                        self.reiniciar()
        return None

    def atualizar(self):
        if self.estado == "transicao_fase":
            self.timer_transicao -= 1
            if self.timer_transicao <= 0:
                self.numero_fase += 1
                self.carregar_fase(self.numero_fase)
            return

        if self.estado != "jogando":
            return

        teclas = pygame.key.get_pressed()

        for plataforma in self.plataformas:
            plataforma.atualizar()

        self.jogador.atualizar(teclas, self.plataformas, self.largura_fase)

        for inimigo in self.inimigos:
            inimigo.atualizar(self.plataformas, self.largura_fase)

        for moeda in self.moedas:
            moeda.atualizar()

        self.checar_colisoes_moedas()
        self.checar_colisoes_inimigos()
        self.checar_colisoes_espinhos()
        self.checar_vitoria()

        if not self.jogador.vivo:
            self.estado = "perdeu"

        self.atualizar_camera()

        if self.estado in ("venceu", "perdeu") and not self.som_finalizacao_tocado:
            parar_musica()
            if self.estado == "venceu" and self.som_vitoria:
                self.som_vitoria.play()
            elif self.estado == "perdeu" and self.som_gameover:
                self.som_gameover.play()
            self.som_finalizacao_tocado = True

    def desenhar_hud(self):
        # Vida (corações)
        for i in range(self.jogador.vida_maxima):
            cheio = i < self.jogador.vida
            x = 30 + i * 35
            y = 30
            if self.tem_imagem_coracao:
                imagem = self.imagem_coracao if cheio else self.imagem_coracao_vazio
                self.tela.blit(imagem, (x - 14, y - 14))
            else:
                cor = VERMELHO if cheio else (90, 90, 90)
                desenhar_coracao(self.tela, x, y, 24, cor)

        # Moedas
        texto_moedas = self.fonte_hud.render(f"Moedas: {self.jogador.moedas}", True, PRETO)
        self.tela.blit(texto_moedas, (LARGURA - texto_moedas.get_width() - 20, 18))

        # Nome da fase atual (ex: "Fase 1")
        texto_fase = self.fonte_hud.render(self.nome_fase, True, PRETO)
        self.tela.blit(texto_fase, (LARGURA - texto_fase.get_width() - 20, 46))

        # Dica de saída
        texto_dica = self.fonte_hud.render("ESC: Menu", True, PRETO)
        self.tela.blit(texto_dica, (LARGURA // 2 - texto_dica.get_width() // 2, 10))

    def desenhar_tela_fim(self, titulo, cor_titulo, subtitulo):
        overlay = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        self.tela.blit(overlay, (0, 0))

        texto_titulo = self.fonte_grande.render(titulo, True, cor_titulo)
        self.tela.blit(
            texto_titulo,
            (LARGURA // 2 - texto_titulo.get_width() // 2, ALTURA // 2 - 100)
        )

        texto_sub = self.fonte_media.render(subtitulo, True, BRANCO)
        self.tela.blit(
            texto_sub,
            (LARGURA // 2 - texto_sub.get_width() // 2, ALTURA // 2 - 20)
        )

        texto_instrucao = self.fonte_hud.render(
            "ENTER: Jogar de novo   |   ESC: Menu", True, BRANCO
        )
        self.tela.blit(
            texto_instrucao,
            (LARGURA // 2 - texto_instrucao.get_width() // 2, ALTURA // 2 + 50)
        )

    def desenhar_tela_transicao(self):
        overlay = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.tela.blit(overlay, (0, 0))

        texto_titulo = self.fonte_grande.render(f"{self.nome_fase} concluída!", True, VERDE)
        self.tela.blit(
            texto_titulo,
            (LARGURA // 2 - texto_titulo.get_width() // 2, ALTURA // 2 - 60)
        )

        texto_sub = self.fonte_media.render(
            f"Preparando Fase {self.numero_fase + 1}...", True, BRANCO
        )
        self.tela.blit(
            texto_sub,
            (LARGURA // 2 - texto_sub.get_width() // 2, ALTURA // 2 + 20)
        )

        texto_aviso = self.fonte_hud.render(
            "Vida e moedas serão reiniciadas", True, (220, 220, 220)
        )
        self.tela.blit(
            texto_aviso,
            (LARGURA // 2 - texto_aviso.get_width() // 2, ALTURA // 2 + 70)
        )

    def desenhar(self):
        # Fundo (parallax simples: fundo fixo, repete se necessário)
        self.tela.blit(self.background, (0, 0))

        for plataforma in self.plataformas:
            plataforma.desenhar(self.tela, self.camera_x)

        for moeda in self.moedas:
            moeda.desenhar(self.tela, self.camera_x)

        for espinho in self.espinhos:
            espinho.desenhar(self.tela, self.camera_x)

        for inimigo in self.inimigos:
            inimigo.desenhar(self.tela, self.camera_x)

        self.bandeira.desenhar(self.tela, self.camera_x)

        self.jogador.desenhar(self.tela, self.camera_x)

        self.desenhar_hud()

        if self.estado == "transicao_fase":
            self.desenhar_tela_transicao()
        elif self.estado == "venceu":
            self.desenhar_tela_fim("VOCÊ VENCEU!", VERDE, f"Moedas coletadas: {self.jogador.moedas}")
        elif self.estado == "perdeu":
            self.desenhar_tela_fim("GAME OVER", VERMELHO, "Você perdeu toda a vida")

    def rodar_frame(self):
        """
        Executa um frame da tela de jogo.
        Retorna "menu" se o jogador pediu para voltar ao menu, senão None.
        """
        resultado = self.processar_eventos()
        self.atualizar()
        self.desenhar()
        return resultado
