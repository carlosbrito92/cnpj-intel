"""
Entrypoint CLI — cnpj-intel <CNPJ> [opções]
"""

import typer
from typing import Annotated
from rich.console import Console

app = typer.Typer(
    name="cnpj-intel",
    help="Inteligência empresarial via CNPJ — relatório PDF em segundos.",
    add_completion=False,
)

console = Console()


@app.command()
def main(
    cnpj: Annotated[str, typer.Argument(help="CNPJ da empresa (qualquer formato)")],
    output: Annotated[str, typer.Option("--output", "-o", help="Formato de saída: pdf | md | json")] = "pdf",
    modo: Annotated[str, typer.Option("--mode", "-m", help="Modo de operação: public | internal")] = "public",
) -> None:
    """
    Gera relatório de inteligência empresarial para o CNPJ informado.
    """
    if output not in ("pdf", "md", "json"):
        console.print("[red]Formato inválido. Use: pdf, md ou json.[/red]")
        raise typer.Exit(code=1)

    if modo not in ("public", "internal"):
        console.print("[red]Modo inválido. Use: public ou internal.[/red]")
        raise typer.Exit(code=1)

    from src.orchestrator import executar
    executar(cnpj=cnpj, modo=modo, output_format=output)


if __name__ == "__main__":
    app()
