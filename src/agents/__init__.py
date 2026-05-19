"""
Agentes de extração e análise — scripts standalone invocados pelo Claude Code.
Cada agente funciona independentemente do orquestrador.
"""

from src.agents.cadastral import extrair as extrair_cadastral
from src.agents.societario import extrair as extrair_societario
from src.agents.red_flags import executar as executar_red_flags

__all__ = [
    "extrair_cadastral",
    "extrair_societario",
    "executar_red_flags",
]
