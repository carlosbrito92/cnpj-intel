"""
Roteador de modelos — ponto central para decisão de provider/modelo por tarefa.
Trocar provider = mudar apenas este arquivo.
"""

from enum import Enum


class Tarefa(Enum):
    EXTRACAO = "extracao"       # dados estruturados → Groq llama-8b
    SINTESE = "sintese"         # prosa final → Claude Haiku
    ORQUESTRACAO = "orquestracao"  # decisões de fluxo → Claude Sonnet


# Mapeamento tarefa → (provider, modelo)
_ROTA: dict[Tarefa, tuple[str, str]] = {
    Tarefa.EXTRACAO: ("groq", "llama-3.1-8b-instant"),
    Tarefa.SINTESE: ("anthropic", "claude-haiku-4-5"),
    Tarefa.ORQUESTRACAO: ("anthropic", "claude-sonnet-4-6"),
}


def get_rota(tarefa: Tarefa) -> tuple[str, str]:
    """
    Retorna (provider, modelo) para a tarefa informada.

    Exemplo:
        provider, modelo = get_rota(Tarefa.EXTRACAO)
        # ("groq", "llama-3.1-8b-instant")
    """
    return _ROTA[tarefa]


def get_modelo(tarefa: Tarefa) -> str:
    """Retorna apenas o nome do modelo."""
    return _ROTA[tarefa][1]


def get_provider(tarefa: Tarefa) -> str:
    """Retorna apenas o provider."""
    return _ROTA[tarefa][0]
