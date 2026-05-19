"""
Wrapper CLI sobre src/analysis/red_flags.py.
Sem LLM. Lê JSON de input, executa heurísticas, salva resultado.
Funciona standalone — independente do Claude Code.
"""

import json
import sys
from pathlib import Path
from src.analysis.red_flags import analisar


def executar(caminho_input: Path) -> dict:
    """
    Lê cadastral.json ou societario.json, executa análise de red flags.
    Retorna dict com flags detectadas.
    """
    dados = json.loads(caminho_input.read_text())
    return analisar(dados)


def salvar(resultado: dict, destino: Path | None = None) -> Path:
    """Salva flags.json em output/<cnpj_limpo>/flags.json."""
    cnpj_limpo = resultado.get("cnpj", "00000000000000").replace(".", "").replace("/", "").replace("-", "")
    if destino is None:
        destino = Path("output") / cnpj_limpo / "flags.json"
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(json.dumps(resultado, ensure_ascii=False, indent=2))
    return destino


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python -m src.agents.red_flags <caminho/cadastral.json>")
        sys.exit(1)

    caminho = Path(sys.argv[1])
    if not caminho.exists():
        print(f"Arquivo não encontrado: {caminho}")
        sys.exit(1)

    resultado = executar(caminho)
    caminho_saida = salvar(resultado)
    print(f"Red flags analisados: {caminho_saida}")
    print(json.dumps(resultado, ensure_ascii=False, indent=2))
