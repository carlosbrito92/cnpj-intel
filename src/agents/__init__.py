"""
Agentes de extração e análise — scripts standalone invocados pelo orquestrador.
Cada agente funciona independentemente.
"""

from src.agents.cadastral import extrair as extrair_cadastral
from src.agents.societario import extrair as extrair_societario
from src.agents.red_flags import executar as executar_red_flags
from src.agents.redator import sintetizar

__all__ = [
    "extrair_cadastral",
    "extrair_societario",
    "executar_red_flags",
    "sintetizar",
]
