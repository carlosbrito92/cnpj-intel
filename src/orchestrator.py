"""
Orquestrador Python puro — coordena agentes em sequência.
Sem LLM próprio. Reporta progresso via Rich.
"""

import json
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

from src.agents.cadastral import extrair as extrair_cadastral, salvar as salvar_cadastral
from src.agents.societario import extrair as extrair_societario, salvar as salvar_societario
from src.agents.red_flags import executar as executar_flags, salvar as salvar_flags
from src.analysis.red_flags import analisar
from src.render.pdf import render_report

console = Console()


def _cabecalho(cnpj: str) -> None:
    console.print(Panel(
        f"[bold white]CNPJ Intelligence CLI[/bold white]\n"
        f"[dim]Processando:[/dim] [cyan]{cnpj}[/cyan]",
        box=box.DOUBLE_EDGE,
        border_style="blue",
        padding=(1, 4),
    ))


def _etapa(numero: int, total: int, descricao: str) -> None:
    console.print(f"\n[dim]\\[{numero}/{total}][/dim] [bold]{descricao}[/bold]")


def _ok(mensagem: str) -> None:
    console.print(f"  [green]✓[/green] {mensagem}")


def _erro(mensagem: str) -> None:
    console.print(f"  [red]✗[/red] {mensagem}")


def _resumo_flags(flags: dict) -> None:
    if flags["total"] == 0:
        console.print("  [green]Nenhuma irregularidade detectada.[/green]")
        return

    table = Table(box=box.SIMPLE, show_header=True, header_style="dim")
    table.add_column("Código", style="dim", width=32)
    table.add_column("Severidade", width=10)
    table.add_column("Descrição")

    cores = {"alto": "red", "medio": "yellow", "baixo": "blue"}

    for flag in flags["flags"]:
        cor = cores.get(flag["severidade"], "white")
        table.add_row(
            flag["codigo"],
            f"[{cor}]{flag['severidade'].upper()}[/{cor}]",
            flag["descricao"],
        )

    console.print(table)


def executar(cnpj: str, modo: str = "public", output_format: str = "pdf") -> Path:
    """
    Pipeline principal. Executa agentes em sequência e gera relatório.

    Args:
        cnpj:          CNPJ em qualquer formato
        modo:          'public' ou 'internal'
        output_format: 'pdf', 'md' ou 'json'

    Returns:
        Path do arquivo gerado.
    """
    TOTAL_ETAPAS = 5
    _cabecalho(cnpj)

    # Etapa 1 — Dados cadastrais
    _etapa(1, TOTAL_ETAPAS, "Extraindo dados cadastrais...")
    try:
        cadastral = extrair_cadastral(cnpj)
        salvar_cadastral(cadastral)
        _ok(f"Razão social: {cadastral.get('razao_social', '—')}")
        _ok(f"Situação: {cadastral.get('situacao_cadastral', '—')}")
    except Exception as e:
        _erro(f"Falha na extração cadastral: {e}")
        raise

    # Etapa 2 — Dados societários
    _etapa(2, TOTAL_ETAPAS, "Extraindo quadro societário...")
    try:
        societario = extrair_societario(cnpj)
        salvar_societario(societario)
        n_socios = len(societario.get("socios") or [])
        _ok(f"{n_socios} sócio(s) identificado(s)")
    except Exception as e:
        _erro(f"Falha na extração societária: {e}")
        raise

    # Etapa 3 — Red flags
    _etapa(3, TOTAL_ETAPAS, "Analisando red flags...")
    dados_combinados = {**cadastral, "socios": societario.get("socios", [])}
    flags = analisar(dados_combinados)
    salvar_flags(flags)
    _resumo_flags(flags)

    # Etapa 4 — Síntese executiva
    _etapa(4, TOTAL_ETAPAS, "Gerando síntese executiva...")
    try:
        from src.agents.redator import sintetizar
        sintese = sintetizar(cadastral, societario, flags)
        _ok("Síntese gerada.")
    except Exception as e:
        _erro(f"Falha na síntese: {e}")
        sintese = "<p>Síntese indisponível.</p>"

    # Etapa 5 — Renderização
    _etapa(5, TOTAL_ETAPAS, "Renderizando relatório...")
    try:
        dados_relatorio = {**cadastral, "socios": societario.get("socios", [])}
        caminho = render_report(dados_relatorio, flags, sintese)
        _ok(f"Relatório gerado: [cyan]{caminho}[/cyan]")
    except Exception as e:
        _erro(f"Falha na renderização: {e}")
        raise

    console.print(Panel(
        f"[bold green]Concluído![/bold green]\n"
        f"[dim]Arquivo:[/dim] [cyan]{caminho}[/cyan]",
        border_style="green",
        padding=(1, 4),
    ))

    return caminho
