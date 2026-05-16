"""
Camada de renderização — geração de PDF via WeasyPrint + Jinja2.
Sem LLM. Entrada: dicts estruturados. Saída: arquivo PDF em disco.
"""

from src.render.pdf import render_report

__all__ = ["render_report"]
