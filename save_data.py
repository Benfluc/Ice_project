# save_data.py
# Persistência simples do progresso do jogador: guarda qual foi a
# fase mais avançada já desbloqueada, em um arquivo JSON no disco
# (veja ARQUIVO_SAVE em settings.py para o caminho exato).
#
# O arquivo sobrevive entre execuções do jogo (fechar e abrir de
# novo), tanto rodando via "python main.py" quanto pelo .exe gerado
# com PyInstaller.

import json
import os

from settings import ARQUIVO_SAVE

# Estrutura padrão usada quando não existe save ainda, ou quando o
# arquivo está corrompido/ilegível.
_PROGRESSO_PADRAO = {
    "fase_mais_avancada_desbloqueada": 1,
}


def carregar_progresso():
    """
    Lê o progresso salvo no disco. Se o arquivo não existir ou estiver
    corrompido, retorna o progresso padrão (só a Fase 1 desbloqueada)
    sem travar o jogo.
    """
    if not os.path.isfile(ARQUIVO_SAVE):
        return dict(_PROGRESSO_PADRAO)

    try:
        with open(ARQUIVO_SAVE, "r", encoding="utf-8") as arquivo:
            dados = json.load(arquivo)
        if not isinstance(dados, dict) or "fase_mais_avancada_desbloqueada" not in dados:
            return dict(_PROGRESSO_PADRAO)
        # Garante que o valor é um inteiro válido (>= 1)
        dados["fase_mais_avancada_desbloqueada"] = max(
            1, int(dados.get("fase_mais_avancada_desbloqueada", 1))
        )
        return dados
    except (json.JSONDecodeError, OSError, ValueError, TypeError):
        return dict(_PROGRESSO_PADRAO)


def salvar_progresso(dados):
    """
    Grava o dicionário de progresso no disco. Falhas de escrita (ex:
    permissão negada) são ignoradas silenciosamente - o jogo continua
    funcionando normalmente, só sem persistir o progresso dessa vez.
    """
    try:
        with open(ARQUIVO_SAVE, "w", encoding="utf-8") as arquivo:
            json.dump(dados, arquivo, indent=2, ensure_ascii=False)
    except OSError:
        pass


def obter_fase_desbloqueada():
    """Retorna o número da fase mais avançada já desbloqueada (>= 1)."""
    progresso = carregar_progresso()
    return progresso["fase_mais_avancada_desbloqueada"]


def desbloquear_fase(numero_fase):
    """
    Marca a fase indicada (e todas anteriores) como desbloqueada, se
    ela for mais avançada do que o progresso atual salvo. Não retrocede
    progresso (se o jogador já tinha desbloqueado a Fase 3 e de algum
    jeito isso for chamado com Fase 2, o save permanece na Fase 3).
    """
    progresso = carregar_progresso()
    if numero_fase > progresso["fase_mais_avancada_desbloqueada"]:
        progresso["fase_mais_avancada_desbloqueada"] = numero_fase
        salvar_progresso(progresso)


def resetar_progresso():
    """Apaga todo o progresso salvo, voltando a só a Fase 1 desbloqueada."""
    salvar_progresso(dict(_PROGRESSO_PADRAO))
