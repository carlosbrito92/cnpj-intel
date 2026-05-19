"""
Agente de extração de dados societários.
Extrai quadro de sócios e histórico de alterações via Groq llama-8b.
Funciona standalone — independente do Claude Code.

Nota: em MEI/EI, o QSA frequentemente vem vazio. Nesses casos, o nome
do titular está na razão social (ex: "54.756.645 Carlos Alberto de Oliveira").
O agente detecta esse padrão e constrói o sócio a partir da razão social.
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
  "socios": [
    {{
      "nome": "string",
      "tipo": "PF ou PJ",
      "qualificacao": "string ou null",
      "data_entrada": "string YYYY-MM-DD ou null",
      "situacao_cadastral": "string ou null — apenas para sócios PJ"
    }}
  ],
  "historico_alteracoes": [
    {{
      "data": "string YYYY-MM-DD ou null",
      "descricao": "string ou null"
    }}
  ]
}}

Regras importantes:
1. Se o campo "qsa" ou "socios" vier vazio ou ausente, verifique a razão social.
2. Em MEI e Empresário Individual (EI), a razão social frequentemente contém
   o nome do titular diretamente (ex: "54.756.645 Carlos Alberto de Oliveira"
   ou "CARLOS ALBERTO DE OLIVEIRA 54756645"). Nesses casos, extraia o nome
   do titular da razão social, removendo CPF/números, e inclua como sócio PF
   com qualificacao "Titular / Empresário Individual".
3. Se não houver histórico de alterações nos dados, retorne lista vazia.
4. Se genuinamente não houver sócios e não for possível inferir da razão social,
   retorne lista vazia.

Dados brutos:
{dados_brutos}
"""


def extrair(raw: str) -> dict:
    """
    Recebe CNPJ, consulta API, extrai dados societários via Groq.
    Retorna dict estruturado + _meta original.
    """
    dados_brutos = buscar(raw)
    meta = dados_brutos.get("_meta", {})

    prompt = PROMPT_EXTRACAO.format(
        dados_brutos=json.dumps(dados_brutos, ensure_ascii=False, indent=2)
    )

    resposta = complete(prompt=prompt)

    resposta_limpa = resposta.strip()
    if resposta_limpa.startswith("```"):
        linhas = resposta_limpa.split("\n")
        resposta_limpa = "\n".join(linhas[1:-1])

    resultado = json.loads(resposta_limpa)
    resultado["_meta"] = meta
    resultado["_fonte"] = dados_brutos.get("_fonte", "cnpjws")

    return resultado


def salvar(resultado: dict, destino: Path | None = None) -> Path:
    """Salva o JSON extraído em output/<cnpj_limpo>/societario.json."""
    cnpj_limpo = resultado.get("_meta", {}).get("limpo", "00000000000000")
    if destino is None:
        destino = Path("output") / cnpj_limpo / "societario.json"
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(json.dumps(resultado, ensure_ascii=False, indent=2))
    return destino


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python -m src.agents.societario <CNPJ>")
        sys.exit(1)

    resultado = extrair(sys.argv[1])
    caminho = salvar(resultado)
    print(f"Societário extraído: {caminho}")
    print(json.dumps(resultado, ensure_ascii=False, indent=2))
