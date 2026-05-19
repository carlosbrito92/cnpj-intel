"""
Camada de abstração sobre providers de LLM.
Ponto único de entrada para decisões de modelo e comunicação com APIs.
"""

from src.llm.router import Tarefa, get_rota, get_modelo, get_provider
from src.llm.groq_client import complete

__all__ = [
    "Tarefa",
    "get_rota",
    "get_modelo",
    "get_provider",
    "complete",
]
