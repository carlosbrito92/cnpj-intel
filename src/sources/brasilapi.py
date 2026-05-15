"""
Cliente HTTP para a BrasilAPI — fallback quando CNPJ.ws falha.
Sem LLM. Sem rate limit documentado — backoff conservador incluso.
"""

import time
import httpx
from src.sources.normalize import normalizar


BASE_URL = "https://brasilapi.com.br/api/cnpj/v1"
MAX_TENTATIVAS = 3
BACKOFF_BASE = 10  # segundos


def buscar(raw: str) -> dict:
    """
    Recebe CNPJ em qualquer formato, valida, consulta BrasilAPI.
    Retorna dict com dados brutos da API + metadados de normalização.
    Levanta ValueError para CNPJ inválido ou não encontrado.
    Levanta RuntimeError se API falhar após todas as tentativas.
    """
    meta = normalizar(raw)
    limpo = meta["limpo"]
    url = f"{BASE_URL}/{limpo}"

    for tentativa in range(1, MAX_TENTATIVAS + 1):
        try:
            response = httpx.get(url, timeout=15)

            if response.status_code == 200:
                dados = response.json()
                dados["_meta"] = meta
                dados["_fonte"] = "brasilapi"
                return dados

            if response.status_code == 429:
                espera = BACKOFF_BASE * tentativa
                print(f"[brasilapi] Rate limit atingido. Aguardando {espera}s...")
                time.sleep(espera)
                continue

            if response.status_code == 404:
                raise ValueError(f"CNPJ não encontrado: {meta['formatado']}")

            response.raise_for_status()

        except httpx.TimeoutException:
            if tentativa == MAX_TENTATIVAS:
                raise RuntimeError(f"[brasilapi] Timeout após {MAX_TENTATIVAS} tentativas.")
            time.sleep(BACKOFF_BASE * tentativa)

    raise RuntimeError(f"[brasilapi] Falha após {MAX_TENTATIVAS} tentativas.")


if __name__ == "__main__":
    import sys
    import json

    if len(sys.argv) < 2:
        print("Uso: python -m src.sources.brasilapi <CNPJ>")
        sys.exit(1)

    resultado = buscar(sys.argv[1])
    print(json.dumps(resultado, ensure_ascii=False, indent=2))
