# settings.py
# Configurações gerais do jogo (telas, cores, física, caminhos de assets)

import os

# ---------- JANELA ----------
LARGURA = 960
ALTURA = 540
FPS = 60
TITULO = "Ice Adventure"

# ---------- CORES ----------
BRANCO = (255, 255, 255)
PRETO = (0, 0, 0)
CINZA = (60, 60, 60)
CINZA_CLARO = (120, 120, 120)
VERDE = (60, 180, 75)
VERDE_CLARO = (100, 220, 110)
VERMELHO = (200, 60, 60)
AMARELO = (240, 200, 40)
AZUL_CEU = (135, 206, 235)
AZUL_ESCURO = (20, 30, 60)

# ---------- FÍSICA ----------
GRAVIDADE = 0.8
VELOCIDADE_JOGADOR = 5
FORCA_SALTO = -15
VELOCIDADE_MAX_QUEDA = 18

# ---------- JOGADOR ----------
VIDA_INICIAL = 3
INVENCIBILIDADE_FRAMES = 90  # frames de invencibilidade após receber dano

# ---------- INIMIGOS ----------
VELOCIDADE_INIMIGO = 2
VELOCIDADE_MONSTRO_VOADOR = 2
VELOCIDADE_PROJETIL = 6
INTERVALO_TIRO_ATIRADOR = 90       # a cada quantos frames o atirador dispara
DANO_ESPINHO = 1
DANO_PROJETIL = 1

# ---------- PLATAFORMAS ESPECIAIS ----------
VELOCIDADE_PLATAFORMA_MOVEL = 1.5
TEMPO_TREMER_PLATAFORMA_CAINDO = 45   # frames tremendo antes de cair, após o herói pisar
TEMPO_QUEDA_PLATAFORMA_CAINDO = 40    # frames até desaparecer de vez (caindo da tela)
PISADAS_PARA_QUEBRAR = 3              # quantas vezes pisar até a plataforma quebradiça quebrar

# ---------- CAMINHOS ----------
# Quando o jogo é empacotado em .exe pelo PyInstaller (modo --onefile),
# os arquivos ficam extraídos numa pasta temporária acessível via
# sys._MEIPASS. Quando rodando normalmente via "python main.py", usamos
# a pasta onde este arquivo está. Isso garante que assets/ seja encontrado
# nos dois casos.
import sys

if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

ASSETS_DIR = os.path.join(BASE_DIR, "assets")
IMAGES_DIR = os.path.join(ASSETS_DIR, "images")
SOUNDS_DIR = os.path.join(ASSETS_DIR, "sounds")
FONTS_DIR = os.path.join(ASSETS_DIR, "fonts")

# ---------- ARQUIVO DE PROGRESSO (SAVE) ----------
# IMPORTANTE: isso fica fora de BASE_DIR de propósito. Quando o jogo
# roda como .exe (PyInstaller --onefile), BASE_DIR pode ser uma pasta
# TEMPORÁRIA que é recriada/apagada a cada execução - salvar o
# progresso lá faria ele "esquecer" tudo a cada vez que o jogo abre.
# Por isso usamos a pasta pessoal do usuário (a mesma onde ficam
# configurações de outros programas), que persiste entre execuções.
if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
    PASTA_SAVE = os.path.join(os.path.expanduser("~"), ".ice_adventure")
else:
    # Rodando via "python main.py": salva ao lado do código mesmo,
    # para facilitar encontrar o arquivo durante o desenvolvimento.
    PASTA_SAVE = BASE_DIR

if not os.path.isdir(PASTA_SAVE):
    try:
        os.makedirs(PASTA_SAVE, exist_ok=True)
    except OSError:
        PASTA_SAVE = BASE_DIR  # fallback se não conseguir criar a pasta

ARQUIVO_SAVE = os.path.join(PASTA_SAVE, "savegame.json")

# Nomes genéricos dos arquivos de imagem (troque pelos nomes reais depois)
IMG_HEROI = "heroi.png"            # imagem única do herói (fallback se não houver animação)
IMG_INIMIGO = "monstro.png"        # imagem única do monstro/inimigo (fallback se não houver animação)
IMG_MOEDA = "moeda.png"            # imagem da moeda

# ---------- ANIMAÇÕES (sequências de frames) ----------
# Cada animação é uma série de arquivos: "<prefixo>_1.png", "<prefixo>_2.png", ...
# O jogo detecta automaticamente quantos frames existem em cada uma.
ANIM_HEROI_IDLE = "heroi_idle"      # heroi_idle_1.png, heroi_idle_2.png, ...
ANIM_HEROI_WALK = "heroi_walk"      # heroi_walk_1.png, heroi_walk_2.png, ...
ANIM_HEROI_JUMP = "heroi_jump"      # heroi_jump_1.png, heroi_jump_2.png, ...

ANIM_MONSTRO_IDLE = "monstro_idle"  # monstro_idle_1.png, monstro_idle_2.png, ...
ANIM_MONSTRO_WALK = "monstro_walk"  # monstro_walk_1.png, monstro_walk_2.png, ...

VELOCIDADE_ANIM_HEROI = 8    # menor = troca de frame mais rápida (em frames do jogo)
VELOCIDADE_ANIM_MONSTRO = 10
IMG_PLATAFORMA = "plataforma.png"  # textura do bloco/plataforma/chão
IMG_PLATAFORMA_MOVEL = "plataforma_movel.png"      # textura da plataforma que se move
IMG_PLATAFORMA_CAINDO = "plataforma_caindo.png"    # textura da plataforma que cai após pisar
IMG_PLATAFORMA_QUEBRADICA = "plataforma_quebradica.png"  # textura da plataforma quebradiça
IMG_ESPINHO = "espinho.png"        # textura do obstáculo de espinhos
IMG_PROJETIL = "projetil.png"      # imagem do projétil disparado pelo monstro atirador
IMG_BACKGROUND = "background.png"  # imagem de fundo padrão (usada se a fase não tiver uma própria)
IMG_BANDEIRA = "bandeira.png"      # bandeira/objetivo final da fase
IMG_MENU_BACKGROUND = "menu_background.png"  # imagem de fundo do menu principal
IMG_CORACAO = "coracao.png"        # ícone de coração (vida) exibido no HUD

# Animações dos monstros novos (mesmo padrão: "<prefixo>_1.png", "<prefixo>_2.png", ...)
ANIM_MONSTRO_VOADOR_VOAR = "monstro_voador_voar"      # monstro_voador_voar_1.png, ...
ANIM_MONSTRO_ATIRADOR_IDLE = "monstro_atirador_idle"  # monstro_atirador_idle_1.png, ...
VELOCIDADE_ANIM_MONSTRO_VOADOR = 10
VELOCIDADE_ANIM_MONSTRO_ATIRADOR = 12

# Nomes genéricos dos arquivos de áudio
MUSICA_MENU = "menu_music.mp3"
MUSICA_FASE = "music.mp3"
SOM_MOEDA = "coin.wav"
SOM_SALTO = "jump.wav"
SOM_DANO = "hit.wav"
SOM_DERROTA_INIMIGO = "enemy_defeat.wav"
SOM_TIRO = "shoot.wav"
SOM_PLATAFORMA_QUEBRANDO = "platform_break.wav"
SOM_VITORIA = "victory.wav"
SOM_GAMEOVER = "gameover.wav"

# Fonte genérica (opcional - troque pelo arquivo .ttf real depois)
FONTE_PRINCIPAL = "fonte.ttf"
FONTE_TUTORIAL = "fonte_tutorial.ttf"  # fonte usada só na tela de tutorial (opcional)
