"""
Renderização de PDF via WeasyPrint + Jinja2.
Sem LLM. Recebe dict estruturado, produz arquivo PDF em disco.
"""

from datetime import date
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML, CSS


RENDER_DIR = Path(__file__).parent
TEMPLATE_FILE = "template.html"
CSS_FILE = RENDER_DIR / "style.css"


def _formatar_capital(valor) -> str:
    try:
        return f"R$ {float(valor):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except (TypeError, ValueError):
        return "—"


def _preparar_contexto(dados: dict, flags: dict, sintese: str) -> dict:
    meta = dados.get("_meta", {})
    atividade_principal = dados.get("atividade_principal") or []

    socios_raw = dados.get("socios") or dados.get("qsa") or []
    socios = [
        {
            "nome": s.get("nome") or s.get("nome_socio") or "—",
            "qualificacao": s.get("qualificacao_socio") or s.get("qualificacao") or "—",
            "tipo": s.get("tipo") or "—",
        }
        for s in socios_raw
    ]

    return {
        "cnpj": meta.get("formatado") or dados.get("cnpj", "—"),
        "razao_social": dados.get("razao_social", "—"),
        "nome_fantasia": dados.get("nome_fantasia") or "",
        "situacao_cadastral": (dados.get("situacao_cadastral") or "—").upper(),
        "natureza_juridica": dados.get("natureza_juridica") or "—",
        "porte": dados.get("porte") or "—",
        "capital_social": _formatar_capital(dados.get("capital_social")),
        "data_inicio_atividade": dados.get("data_inicio_atividade") or "—",
        "municipio": dados.get("municipio") or "—",
        "uf": dados.get("uf") or "—",
        "atividades": atividade_principal,
        "socios": socios,
        "flags": flags,
        "sintese": sintese,
        "data_geracao": date.today().strftime("%d/%m/%Y"),
    }


def render_report(
    dados: dict,
    flags: dict,
    sintese: str,
    destino: Path | None = None,
) -> Path:
    """
    Gera o relatório PDF.

    Args:
        dados:   dict retornado por src/sources (dados da Receita Federal)
        flags:   dict retornado por src/analysis/red_flags.analisar()
        sintese: string HTML/texto gerada pelo agente-redator
        destino: caminho do PDF de saída (opcional — padrão: output/<cnpj>/relatorio.pdf)

    Returns:
        Path do arquivo gerado.
    """
    meta = dados.get("_meta", {})
    cnpj_limpo = meta.get("limpo") or dados.get("cnpj", "00000000000000")

    if destino is None:
        destino = Path("output") / cnpj_limpo / "relatorio.pdf"

    destino.parent.mkdir(parents=True, exist_ok=True)

    env = Environment(loader=FileSystemLoader(str(RENDER_DIR)))
    template = env.get_template(TEMPLATE_FILE)
    contexto = _preparar_contexto(dados, flags, sintese)
    html_str = template.render(**contexto)

    HTML(string=html_str, base_url=str(RENDER_DIR)).write_pdf(
        str(destino),
        stylesheets=[CSS(filename=str(CSS_FILE))],
    )

    return destino


if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) < 2:
        print("Uso: python -m src.render.pdf <fixture.json>")
        sys.exit(1)

    fixture = json.loads(Path(sys.argv[1]).read_text())
    from src.analysis.red_flags import analisar
    flags = analisar(fixture)
    sintese = "<p>Síntese de exemplo gerada para teste de renderização.</p>"
    caminho = render_report(fixture, flags, sintese)
    print(f"PDF gerado: {caminho}")
