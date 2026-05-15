"""
Heurísticas determinísticas de red flags para dados de CNPJ.
Sem LLM. Sem chamadas externas. Totalmente testável com input fixo.
"""

from datetime import date, datetime
from typing import Any


# --- Tipos de severidade ---
ALTO = "alto"
MEDIO = "medio"
BAIXO = "baixo"


def _hoje() -> date:
    return date.today()


def _parsear_data(valor: str | None) -> date | None:
    if not valor:
        return None
    for fmt in ("%Y-%m-%d", "%d/%m/%Y"):
        try:
            return datetime.strptime(valor, fmt).date()
        except ValueError:
            continue
    return None


def flag_situacao_cadastral(dados: dict) -> dict | None:
    """Empresa com situação diferente de ATIVA."""
    situacao = (dados.get("situacao_cadastral") or "").upper()
    if situacao != "ATIVA":
        return {
            "codigo": "SITUACAO_IRREGULAR",
            "severidade": ALTO,
            "descricao": f"Situação cadastral: {situacao or 'não informada'}.",
        }
    return None


def flag_capital_social_baixo(dados: dict) -> dict | None:
    """Capital social abaixo de R$ 1.000."""
    capital = dados.get("capital_social") or 0
    try:
        capital = float(capital)
    except (TypeError, ValueError):
        return None
    if 0 < capital < 1000:
        return {
            "codigo": "CAPITAL_SOCIAL_BAIXO",
            "severidade": MEDIO,
            "descricao": f"Capital social declarado de R$ {capital:,.2f} — abaixo de R$ 1.000,00.",
        }
    return None


def flag_sem_capital_social(dados: dict) -> dict | None:
    """Capital social zerado ou ausente."""
    capital = dados.get("capital_social")
    if capital is None or float(capital) == 0:
        return {
            "codigo": "SEM_CAPITAL_SOCIAL",
            "severidade": MEDIO,
            "descricao": "Capital social zerado ou não informado.",
        }
    return None


def flag_alteracoes_societarias_recentes(dados: dict) -> dict | None:
    """Mais de 3 alterações no quadro societário no último ano."""
    historico = dados.get("historico_alteracoes") or []
    um_ano_atras = _hoje().replace(year=_hoje().year - 1)
    recentes = [
        h for h in historico
        if _parsear_data(h.get("data")) and _parsear_data(h.get("data")) >= um_ano_atras
    ]
    if len(recentes) > 3:
        return {
            "codigo": "ALTERACOES_SOCIETARIAS_FREQUENTES",
            "severidade": MEDIO,
            "descricao": f"{len(recentes)} alterações societárias no último ano.",
        }
    return None


def flag_socio_pj_irregular(dados: dict) -> dict | None:
    """Sócio pessoa jurídica com situação cadastral irregular."""
    socios = dados.get("socios") or dados.get("qsa") or []
    irregulares = [
        s for s in socios
        if s.get("tipo") == "PJ"
        and (s.get("situacao_cadastral") or "").upper() not in ("ATIVA", "")
    ]
    if irregulares:
        nomes = ", ".join(s.get("nome", "N/A") for s in irregulares)
        return {
            "codigo": "SOCIO_PJ_IRREGULAR",
            "severidade": ALTO,
            "descricao": f"Sócio(s) PJ com situação irregular: {nomes}.",
        }
    return None


def flag_empresa_recente(dados: dict) -> dict | None:
    """Empresa com menos de 6 meses de existência."""
    data_abertura = _parsear_data(dados.get("data_inicio_atividade"))
    if not data_abertura:
        return None
    dias = (_hoje() - data_abertura).days
    if dias < 180:
        return {
            "codigo": "EMPRESA_RECENTE",
            "severidade": BAIXO,
            "descricao": f"Empresa constituída há {dias} dias.",
        }
    return None


# --- Executor principal ---

HEURISTICAS = [
    flag_situacao_cadastral,
    flag_capital_social_baixo,
    flag_sem_capital_social,
    flag_alteracoes_societarias_recentes,
    flag_socio_pj_irregular,
    flag_empresa_recente,
]


def analisar(dados: dict) -> dict:
    """
    Executa todas as heurísticas sobre os dados de um CNPJ.
    Retorna dict com lista de flags e contagem por severidade.
    """
    flags = []
    for heuristica in HEURISTICAS:
        resultado = heuristica(dados)
        if resultado:
            flags.append(resultado)

    return {
        "cnpj": dados.get("_meta", {}).get("formatado", "N/A"),
        "flags": flags,
        "total": len(flags),
        "por_severidade": {
            ALTO: sum(1 for f in flags if f["severidade"] == ALTO),
            MEDIO: sum(1 for f in flags if f["severidade"] == MEDIO),
            BAIXO: sum(1 for f in flags if f["severidade"] == BAIXO),
        },
    }
