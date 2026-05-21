"""
Agente redator — síntese executiva em linguagem de compliance.
Usa Groq llama-3.1-8b-instant (free tier).
Funciona standalone — independente do orquestrador.
"""

import json
import sys
from pathlib import Path
from src.llm.groq_client import complete


PROMPT_SINTESE = """
Você é um analista de compliance especializado em inteligência empresarial brasileira.
Redija uma síntese executiva concisa sobre a empresa abaixo, em português formal.

A síntese deve:
- Ter entre 3 e 5 parágrafos
- Apresentar o perfil da empresa (atividade, porte, tempo de existência)
- Comentar a situação cadastral e societária
- Destacar os red flags identificados, se houver
- Concluir com uma avaliação geral de risco (baixo, médio ou alto)
- Usar linguagem de relatório de compliance — objetiva, sem especulação
- NÃO inventar informações além do que está nos dados fornecidos

Dados cadastrais:
{cadastral}

Dados societários:
{societario}

Red flags detectados:
{flags}

Retorne apenas o texto da síntese em HTML simples (use apenas <p> e <strong>).
Sem explicações adicionais.
"""


def sintetizar(cadastral: dict, societario: dict, flags: dict) -> str:
    """
    Gera síntese executiva a partir dos dados extraídos.
    Retorna string HTML com a síntese.
    """
    prompt = PROMPT_SINTESE.format(
        cadastral=json.dumps(cadastral, ensure_ascii=False, indent=2),
        societario=json.dumps(societario, ensure_ascii=False, indent=2),
        flags=json.dumps(flags, ensure_ascii=False, indent=2),
    )

    resposta = complete(
        prompt=prompt,
        system="Você é um analista de compliance. Retorne apenas HTML simples com <p> e <strong>. Sem markdown.",
        temperatura=0.2,
        max_tokens=1024,
    )

    # Remove possíveis blocos de markdown
    resposta_limpa = resposta.strip()
    if resposta_limpa.startswith("```"):
        linhas = resposta_limpa.split("\n")
        resposta_limpa = "\n".join(linhas[1:-1])

    return resposta_limpa


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Uso: python -m src.agents.redator <cadastral.json> <societario.json> <flags.json>")
        sys.exit(1)

    cadastral = json.loads(Path(sys.argv[1]).read_text())
    societario = json.loads(Path(sys.argv[2]).read_text())
    flags = json.loads(Path(sys.argv[3]).read_text())

    sintese = sintetizar(cadastral, societario, flags)
    print(sintese)
