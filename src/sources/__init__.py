"""
Camada de fontes externas — IO com APIs públicas de CNPJ.
Sem LLM. Toda lógica aqui é determinística e testável sem rede (via mocks).
"""

from src.sources.cnpjws import buscar as buscar_cnpjws
from src.sources.brasilapi import buscar as buscar_brasilapi
from src.sources.normalize import normalizar, validar, formatar, limpar


def buscar(raw: str) -> dict:
    """
    Ponto de entrada principal da camada de fontes.
    Tenta CNPJ.ws primeiro — fallback para BrasilAPI em caso de falha.
    """
    try:
        dados = buscar_cnpjws(raw)
        dados["_fonte"] = "cnpjws"
        return dados
    except RuntimeError:
        print("[sources] CNPJ.ws indisponível — tentando BrasilAPI...")
        return buscar_brasilapi(raw)


__all__ = [
    "buscar",
    "buscar_cnpjws",
    "buscar_brasilapi",
    "normalizar",
    "validar",
    "formatar",
    "limpar",
]
