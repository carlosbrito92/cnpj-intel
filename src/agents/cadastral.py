"""
Agente de extração de dados cadastrais.
Consulta CNPJ.ws (com fallback BrasilAPI), estrutura via Groq llama-8b.
Funciona standalone — independente do Claude Code.
"""

import json
import sys
from pathlib import Path
from src.sources import buscar
from src.llm.groq_client import complete


PROMPT_EXTRACAO = """
Você recebe dados brutos de CNPJ retornados pela API da Receita Federal.
Extraia e retorne APENAS um JSON com os seguintes campos:

{{
  "cnpj": "string — CNPJ formatado XX.XXX.XXX/XXXX-XX",
  "razao_social": "string",
  "nome_fantasia": "string ou null",
  "situacao_cadastral": "string — ex: ATIVA, SUSPENSA, BAIXADA",
  "data_situacao_cadastral": "string YYYY-MM-DD ou null",
  "natureza_juridica": "string ou null",
  "porte": "string ou null",
  "capital_social": "number ou null",
  "data_inicio_atividade": "string YYYY-MM-DD ou null",
  "logradouro": "string ou null",
  "numero": "string ou null",
  "municipio": "string ou null",
  "uf": "string (2 letras) ou null",
  "cep": "string ou null",
  "atividade_principal": [
    {{"codigo": "string", "descricao": "string"}}
  ]
}}

Dados brutos:
{dados_brutos}
"""


def extrair(raw: str) -> dict:
    """
    Recebe CNPJ, consulta API, extrai dados cadastrais via Groq.
    Retorna dict estruturado + _meta original.
    """
    dados_brutos = buscar(raw)
    meta = dados_brutos.get("_meta", {})

    prompt = PROMPT_EXTRACAO.format(
        dados_brutos=json.dumps(dados_brutos, ensure_ascii=False, indent=2)
    )

    resposta = complete(prompt=prompt)

    # Remove possíveis blocos de markdown antes de parsear
    resposta_limpa = resposta.strip()
    if resposta_limpa.startswith("```"):
        linhas = resposta_limpa.split("\n")
        resposta_limpa = "\n".join(linhas[1:-1])

    resultado = json.loads(resposta_limpa)
    resultado["_meta"] = meta
    resultado["_fonte"] = dados_brutos.get("_fonte", "cnpjws")

    return resultado


def salvar(resultado: dict, destino: Path | None = None) -> Path:
    """Salva o JSON extraído em output/<cnpj_limpo>/cadastral.json."""
    cnpj_limpo = resultado.get("_meta", {}).get("limpo", "00000000000000")
    if destino is None:
        destino = Path("output") / cnpj_limpo / "cadastral.json"
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(json.dumps(resultado, ensure_ascii=False, indent=2))
    return destino


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python -m src.agents.cadastral <CNPJ>")
        sys.exit(1)

    resultado = extrair(sys.argv[1])
    caminho = salvar(resultado)
    print(f"Cadastral extraído: {caminho}")
    print(json.dumps(resultado, ensure_ascii=False, indent=2))
