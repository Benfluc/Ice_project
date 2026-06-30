# Ice Adventure — Jogo 2D de Plataforma

Jogo 2D de plataforma feito em Python com Pygame. O herói avança da
esquerda para a direita, coleta moedas, derrota monstros (saltando em
cima deles) e vence ao tocar a bandeira no final da fase.

## Requisitos

- Python 3.8+
- Pygame

Instalar dependência:

```bash
pip install pygame
```

## Como executar

```bash
python main.py
```

## Estrutura do projeto

```
platform_game/
├── main.py            # Ponto de entrada (máquina de estados: menu/tutorial/jogo)
├── settings.py         # Constantes: tela, cores, física, nomes de arquivos de assets
├── utils.py            # Carregamento de imagens/sons/fontes com placeholder automático
├── save_data.py         # Persistência do progresso (fases desbloqueadas) em savegame.json
├── menu.py             # Menu (Iniciar/Selecionar Fase/Tutorial/Sair), Seleção de Fase, Tutorial
├── game_screen.py       # Tela de gameplay: câmera, HUD, vitória/derrota
├── level.py             # Layout de TODAS as fases (plataformas, moedas, inimigos, bandeira, background)
├── sprites/
│   ├── player.py        # Classe do Jogador (movimento, salto, vida, dano)
│   ├── enemy.py          # Inimigo, MonstroVoador, MonstroAtirador
│   ├── projectile.py      # Classe do Projétil (disparado pelo MonstroAtirador)
│   ├── spike.py            # Classe do Espinho (obstáculo fixo que causa dano)
│   ├── coin.py              # Classe da Moeda (coleta, animação)
│   └── platform.py          # Plataforma, PlataformaMovel, PlataformaCaindo, PlataformaQuebradica
└── assets/
    ├── images/           # heroi.png, monstro.png, moeda.png, etc (veja LEIA-ME.txt)
    ├── sounds/            # music.mp3, coin.wav, jump.wav, etc (veja LEIA-ME.txt)
    └── fonts/              # fonte.ttf (opcional)
```

## Assets (sprites, música, etc.)

Todos os nomes de arquivo usados pelo jogo são **genéricos** e estão
centralizados em `settings.py`:

```python
IMG_HEROI = "heroi.png"
IMG_INIMIGO = "monstro.png"
IMG_MOEDA = "moeda.png"
IMG_PLATAFORMA = "plataforma.png"
IMG_BACKGROUND = "background.png"
IMG_BANDEIRA = "bandeira.png"
IMG_MENU_BACKGROUND = "menu_background.png"
IMG_CORACAO = "coracao.png"

MUSICA_MENU = "menu_music.mp3"
MUSICA_FASE = "music.mp3"
SOM_MOEDA = "coin.wav"
SOM_SALTO = "jump.wav"
SOM_DANO = "hit.wav"
SOM_DERROTA_INIMIGO = "enemy_defeat.wav"
SOM_VITORIA = "victory.wav"
SOM_GAMEOVER = "gameover.wav"
```

### Animações do herói e do monstro

O herói e o monstro usam **sequências de frames numerados** em vez de
uma imagem única. Coloque os arquivos em `assets/images/` seguindo o
padrão `<prefixo>_<numero>.png`, começando em 1:

```
heroi_idle_1.png, heroi_idle_2.png, ...   -> parado
heroi_walk_1.png, heroi_walk_2.png, ...   -> andando
heroi_jump_1.png, heroi_jump_2.png, ...   -> pulando

monstro_idle_1.png, monstro_idle_2.png, ... -> parado
monstro_walk_1.png, monstro_walk_2.png, ... -> andando
```

O jogo detecta automaticamente quantos frames existem em cada
sequência — não precisa editar nada no código, só adicionar os
arquivos. A velocidade de troca de frame é ajustável em
`settings.py` (`VELOCIDADE_ANIM_HEROI` e `VELOCIDADE_ANIM_MONSTRO`,
menor valor = animação mais rápida). Sprites virados para a esquerda
são gerados automaticamente por espelhamento — desenhe apenas a
versão olhando para a direita.

Basta colocar seus arquivos finais dentro de `assets/images/` e
`assets/sounds/` com esses nomes — ou editar os nomes em
`settings.py` para apontar para os arquivos que você já tem.

**Importante:** enquanto os arquivos reais não existem, o jogo usa
formas geométricas coloridas como placeholder (não trava, não dá
erro). Isso permite testar e jogar mesmo antes de ter a arte final.

## Controles

| Tecla            | Ação                  |
|-------------------|------------------------|
| ← / A             | Mover para a esquerda |
| → / D             | Mover para a direita  |
| ESPAÇO / ↑ / W    | Saltar                |
| ESC               | Voltar ao menu         |
| ENTER             | Jogar de novo (na tela de vitória/derrota) |

Derrote monstros saltando em cima deles. Colidir com um monstro pelo
lado causa dano ao herói. Perder toda a vida ou cair em um abismo
encerra a fase (Game Over). Tocar a bandeira avança para a próxima
fase (ou vence o jogo, se for a última fase).

## Múltiplas fases

O jogo já vem com **2 fases** prontas e suporta qualquer quantidade.
Ao tocar a bandeira no final de uma fase:
- Se houver uma próxima fase na lista, mostra uma tela de transição
  (~2 segundos) e carrega a fase seguinte automaticamente
- Vida e moedas **resetam** a cada fase nova (cada fase começa com
  vida cheia e 0 moedas)
- Se for a última fase da lista, o jogo declara vitória final

### Como adicionar a Fase 3 (ou mais)

Tudo fica em `level.py`:

1. Copie uma função `construir_fase_N()` existente (ex: a da Fase 2)
2. Renomeie para `construir_fase_3()` e ajuste as listas de
   `segmentos_chao`, `plataformas_flutuantes`, `posicoes_moedas` e
   `posicoes_inimigos` com o layout que quiser
3. Defina `nome="Fase 3"` e `imagem_background="background_fase3.png"`
4. Adicione `construir_fase_3` na lista `FASES`, no final do arquivo:
   ```python
   FASES = [
       construir_fase_1,
       construir_fase_2,
       construir_fase_3,
   ]
   ```
5. Coloque o arquivo `background_fase3.png` em `assets/images/`

Pronto — o jogo passa a ter 3 fases automaticamente, na ordem da
lista. Não é preciso alterar nada em `game_screen.py` ou `main.py`.
A tela de seleção de fases (veja abaixo) também se adapta sozinha
à quantidade de fases que existir.

## Seleção de fase e progresso salvo

O menu principal tem um botão **"Selecionar Fase"** que abre uma
tela com um botão para cada fase do jogo. Fases que o jogador ainda
não desbloqueou aparecem acinzentadas e não são clicáveis.

- Vencer uma fase desbloqueia permanentemente a próxima
- O progresso é salvo em disco (arquivo `savegame.json`) e
  **persiste entre execuções** - fechar e abrir o jogo de novo (ou
  o `.exe`) mantém as fases já desbloqueadas
- Escolher uma fase pelo seletor inicia o jogo direto a partir dela,
  com vida cheia e 0 moedas (igual a qualquer início de fase)
- O save nunca "retrocede": se você já desbloqueou a Fase 3, ele
  continua valendo mesmo se depois você jogar e perder na Fase 1

**Onde o save fica salvo:** ao rodar via `python main.py`, o arquivo
`savegame.json` fica na mesma pasta do código (fácil de encontrar
durante o desenvolvimento). Ao rodar como `.exe` empacotado pelo
PyInstaller, ele fica na pasta pessoal do usuário (`.ice_adventure`
dentro da pasta do usuário), porque a pasta temporária que o
PyInstaller usa para o `.exe` é apagada a cada execução - salvar lá
faria o jogo "esquecer" o progresso toda vez que fosse aberto.

**Para resetar o progresso** (testar do zero), apague o arquivo
`savegame.json`, ou chame `save_data.resetar_progresso()` em
`save_data.py`.

## Plataformas especiais

Além da `Plataforma` comum (fixa), existem três variações - todas
criadas em `level.py`, dentro dos parâmetros de `_montar_fase()`:

**Plataforma móvel** (anda entre dois pontos, horizontal ou vertical;
o herói se move junto quando está em cima):
```python
plataformas_moveis = [
    # (x, y, largura, altura, ponto_final, eixo)
    (1450, 300, 100, 24, 1650, "horizontal"),  # anda de x=1450 até x=1650
    (2950, 420, 100, 24, 200, "vertical"),     # sobe/desce entre y=420 e y=200
]
```

**Plataforma que cai** (normal até o herói pisar; depois treme e cai):
```python
plataformas_caindo = [
    (3450, 380, 110, 24),  # (x, y, largura, altura)
]
```
Tempos ajustáveis em `settings.py`: `TEMPO_TREMER_PLATAFORMA_CAINDO`
(quanto treme antes de cair) e `TEMPO_QUEDA_PLATAFORMA_CAINDO`.

**Plataforma quebradiça** (quebra após algumas pisadas):
```python
plataformas_quebradicas = [
    (3850, 340, 100, 24),         # usa o padrão de settings.py (3 pisadas)
    (3900, 340, 100, 24, 5),      # ou customize: (x, y, largura, altura, pisadas)
]
```
Padrão ajustável em `settings.py`: `PISADAS_PARA_QUEBRAR`.

Todos esses parâmetros são passados para `_montar_fase()` dentro da
função `construir_fase_N()` da fase desejada - veja a Fase 2 em
`level.py` para um exemplo completo já funcionando de cada tipo.

## Espinhos

Obstáculo fixo (não bloqueia movimento, só causa dano ao toque):
```python
posicoes_espinhos = [
    (1080, CHAO_Y - 24),               # (x, y) - usa tamanho padrão 40x24
    (2600, CHAO_Y - 24, 60, 24),       # ou (x, y, largura, altura) customizado
]
```
Dano ajustável em `settings.py`: `DANO_ESPINHO`.

## Monstros novos

**Monstro voador** (voa livremente, sem precisar de chão; sobe e desce
em padrão suave entre dois pontos):
```python
posicoes_monstros_voadores = [
    # (x, y, distancia_patrulha, amplitude_vertical)
    (2050, 280, 150, 35),
]
```

**Monstro atirador** (dispara projéteis periodicamente; pode ficar
parado ou patrulhar uma distância curta):
```python
posicoes_monstros_atiradores = [
    # (x, y, direcao_inicial, distancia_patrulha)
    (3000, CHAO_Y - 48, -1, 0),  # -1 = atira p/ esquerda; 0 = fica parado
]
```
Por padrão o monstro atirador **não é derrotável pulando em cima**
(pense nele como "para ser evitado/desviado", não atacado corpo a
corpo) - mas isso é configurável passando
`derrotavel_pulando_em_cima=True` ao criar um `MonstroAtirador`
diretamente em `level.py`, se quiser permitir.

Intervalo de tiro e velocidade do projétil ajustáveis em
`settings.py`: `INTERVALO_TIRO_ATIRADOR`, `VELOCIDADE_PROJETIL`,
`DANO_PROJETIL`.

## Tamanho de espinhos e projéteis

**Espinho**: tamanho padrão é 40x24px (em `sprites/spike.py`, linha
`def __init__(self, x, y, largura=40, altura=24)`). Pode customizar
por espinho direto na lista da fase:
```python
posicoes_espinhos = [
    (1080, CHAO_Y - 24),               # usa o padrão 40x24
    (2600, CHAO_Y - 24, 60, 30),       # (x, y, largura, altura) customizado
]
```

**Projétil**: tamanho padrão é 20x12px. Para mudar o padrão de todos
os atiradores, edite `tamanho_projetil=(20, 12)` em
`sprites/enemy.py`, na assinatura de `MonstroAtirador.__init__`. Para
customizar um atirador específico, passe o parâmetro ao criá-lo em
`level.py`:
```python
inimigos.add(MonstroAtirador(3000, CHAO_Y - 48, tamanho_projetil=(40, 20)))
```
(a lista simples `posicoes_monstros_atiradores` não inclui esse
parâmetro - para usá-lo, crie o `MonstroAtirador` diretamente como no
exemplo acima, dentro da função da fase).

## Personalizando dificuldade/física

Ajustes como velocidade do herói, força do salto, gravidade,
velocidade dos inimigos e vida inicial estão todos centralizados em
`settings.py`.
