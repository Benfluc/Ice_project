"""
main.py
Ponto de entrada do jogo "Ice Adventure".

Controla a máquina de estados principal:
    MENU -> TUTORIAL -> JOGO -> (volta pro MENU ou SAI)
    MENU -> SELECAO_FASE -> JOGO (a partir da fase escolhida)

Para rodar:
    python main.py
"""

import pygame
import sys

from settings import LARGURA, ALTURA, FPS, TITULO
from menu import TelaMenu, TelaTutorial, TelaSelecaoFase
from game_screen import TelaJogo


class Jogo:
    def __init__(self):
        pygame.init()
        try:
            pygame.mixer.init()
        except pygame.error:
            print("Aviso: não foi possível inicializar o áudio. O jogo continuará sem som.")

        self.tela = pygame.display.set_mode((LARGURA, ALTURA))
        pygame.display.set_caption(TITULO)
        self.relogio = pygame.time.Clock()

        self.estado = "menu"  # menu | tutorial | selecao_fase | jogo

        self.tela_menu = TelaMenu(self.tela)
        self.tela_tutorial = None
        self.tela_selecao_fase = None
        self.tela_jogo = None

    def ir_para_menu(self):
        self.estado = "menu"
        self.tela_menu = TelaMenu(self.tela)

    def ir_para_tutorial(self):
        self.estado = "tutorial"
        self.tela_tutorial = TelaTutorial(self.tela)

    def ir_para_selecao_fase(self):
        self.estado = "selecao_fase"
        self.tela_selecao_fase = TelaSelecaoFase(self.tela)

    def ir_para_jogo(self, fase_inicial=1):
        self.estado = "jogo"
        self.tela_jogo = TelaJogo(self.tela, fase_inicial=fase_inicial)

    def rodar(self):
        rodando = True
        while rodando:
            if self.estado == "menu":
                acao = self.tela_menu.rodar_frame()
                if acao == "iniciar":
                    self.ir_para_jogo(fase_inicial=1)
                elif acao == "selecionar_fase":
                    self.ir_para_selecao_fase()
                elif acao == "tutorial":
                    self.ir_para_tutorial()
                elif acao == "sair":
                    rodando = False

            elif self.estado == "tutorial":
                acao = self.tela_tutorial.rodar_frame()
                if acao == "menu":
                    self.ir_para_menu()

            elif self.estado == "selecao_fase":
                acao = self.tela_selecao_fase.rodar_frame()
                if acao == "menu":
                    self.ir_para_menu()
                elif isinstance(acao, tuple) and acao[0] == "jogar":
                    self.ir_para_jogo(fase_inicial=acao[1])

            elif self.estado == "jogo":
                acao = self.tela_jogo.rodar_frame()
                if acao == "menu":
                    self.ir_para_menu()

            pygame.display.flip()
            self.relogio.tick(FPS)

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    jogo = Jogo()
    jogo.rodar()
