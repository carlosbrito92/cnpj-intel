"""
Cliente Groq para chamadas de chat completion.
Usado pelos agentes de extração (cadastral, societario).
Sem lógica de negócio — apenas comunicação com a API.
"""

import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()


def _cliente() -> Groq:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY não encontrada. Verifique o .env.")
    return Groq(api_key=api_key)


def complete(
    prompt: str,
    model: str = "llama-3.1-8b-instant",
    system: str = "Você é um assistente de extração de dados estruturados. Responda apenas em JSON válido, sem texto adicional.",
    temperatura: float = 0.0,
    max_tokens: int = 1024,
) -> str:
    """
    Envia prompt para o Groq e retorna o texto da resposta.
    temperatura=0.0 garante output determinístico para extração.
    """
    cliente = _cliente()
    resposta = cliente.chat.completions.create(
        model=model,
        temperature=temperatura,
        max_tokens=max_tokens,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
    )
    return resposta.choices[0].message.content
