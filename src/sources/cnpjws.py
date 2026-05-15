"""
Cliente HTTP para a API CNPJ.ws.
Sem LLM. Rate limit: 3 req/min — backoff exponencial incluso.
"""

import time
import httpx
from src.sources.normalize import normalizar


BASE_URL = "https://publica.cnpj.ws/cnpj"
MAX_TENTATIVAS = 3
BACKOFF_BASE = 20  # segundos — respeita 3 req/min


def buscar(raw: str) -> dict:
    """
    Recebe CNPJ em qualquer formato, valida, consulta CNPJ.ws.
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
                return dados

            if response.status_code == 429:
                espera = BACKOFF_BASE * tentativa
                print(f"[cnpjws] Rate limit atingido. Aguardando {espera}s...")
                time.sleep(espera)
                continue

            if response.status_code == 404:
                raise ValueError(f"CNPJ não encontrado na Receita Federal: {meta['formatado']}")

            # 5xx e outros — tenta novamente
            if tentativa < MAX_TENTATIVAS:
                time.sleep(BACKOFF_BASE * tentativa)
                continue

        except httpx.TimeoutException:
            if tentativa == MAX_TENTATIVAS:
                raise RuntimeError(f"[cnpjws] Timeout após {MAX_TENTATIVAS} tentativas.")
            time.sleep(BACKOFF_BASE * tentativa)

    raise RuntimeError(f"[cnpjws] Falha após {MAX_TENTATIVAS} tentativas.")


if __name__ == "__main__":
    import sys
    import json

    if len(sys.argv) < 2:
        print("Uso: python -m src.sources.cnpjws <CNPJ>")
        sys.exit(1)

    resultado = buscar(sys.argv[1])
    print(json.dumps(resultado, ensure_ascii=False, indent=2))
