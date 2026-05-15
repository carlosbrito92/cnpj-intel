"""
Validação e normalização de CNPJ.
Sem LLM. Sem chamadas externas. Puramente determinístico.
"""

import re
from stdnum.br import cnpj


def limpar(raw: str) -> str:
    """Remove formatação — aceita '12.345.678/0001-90' ou '12345678000190'."""
    return re.sub(r"\D", "", raw)


def validar(raw: str) -> bool:
    """Retorna True se o CNPJ for válido (dígito verificador correto)."""
    return cnpj.is_valid(limpar(raw))


def formatar(raw: str) -> str:
    """Retorna CNPJ no formato '12.345.678/0001-90'."""
    c = limpar(raw)
    if len(c) != 14:
        raise ValueError(f"CNPJ inválido: {raw}")
    return f"{c[:2]}.{c[2:5]}.{c[5:8]}/{c[8:12]}-{c[12:]}"


def normalizar(raw: str) -> dict:
    """
    Ponto de entrada principal.
    Retorna dict com raw, limpo, formatado e válido.
    Levanta ValueError se inválido.
    """
    limpo = limpar(raw)
    if not validar(limpo):
        raise ValueError(f"CNPJ inválido: {raw}")
    return {
        "raw": raw,
        "limpo": limpo,
        "formatado": formatar(limpo),
        "valido": True,
    }
