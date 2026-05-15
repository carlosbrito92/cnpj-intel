"""
Testes para src/sources/cnpjws.py e brasilapi.py
Usa respx para mockar HTTP — sem rede real.
"""

import json
import pytest
import respx
import httpx
from pathlib import Path

from src.sources.cnpjws import buscar as buscar_cnpjws
from src.sources.brasilapi import buscar as buscar_brasilapi
from src.sources import buscar


FIXTURES = Path("tests/fixtures")


def carregar_fixture(nome: str) -> dict:
    return json.loads((FIXTURES / f"{nome}.json").read_text())


# --- CNPJ.ws ---

class TestCnpjws:
    @respx.mock
    def test_busca_com_sucesso(self):
        fixture = carregar_fixture("petrobras")
        cnpj_limpo = fixture["_meta"]["limpo"]

        respx.get(f"https://publica.cnpj.ws/cnpj/{cnpj_limpo}").mock(
            return_value=httpx.Response(200, json=fixture)
        )

        resultado = buscar_cnpjws("33.000.167/0001-01")
        assert resultado["cnpj"] == cnpj_limpo

    @respx.mock
    def test_levanta_erro_404(self):
        respx.get("https://publica.cnpj.ws/cnpj/00000000000191").mock(
            return_value=httpx.Response(404)
        )

        with pytest.raises(ValueError, match="não encontrado"):
            buscar_cnpjws("00.000.000/0001-91")

    @respx.mock
    def test_levanta_runtime_error_apos_tentativas(self):
        respx.get("https://publica.cnpj.ws/cnpj/33000167000101").mock(
            return_value=httpx.Response(500)
        )

        with pytest.raises(Exception):
            buscar_cnpjws("33.000.167/0001-01")


# --- BrasilAPI ---

class TestBrasilapi:
    @respx.mock
    def test_busca_com_sucesso(self):
        fixture = carregar_fixture("itau")
        cnpj_limpo = fixture["_meta"]["limpo"]

        respx.get(f"https://brasilapi.com.br/api/cnpj/v1/{cnpj_limpo}").mock(
            return_value=httpx.Response(200, json=fixture)
        )

        resultado = buscar_brasilapi("60.701.190/0001-04")
        assert resultado["cnpj"] == cnpj_limpo

    @respx.mock
    def test_levanta_erro_404(self):
        respx.get("https://brasilapi.com.br/api/cnpj/v1/00000000000191").mock(
            return_value=httpx.Response(404)
        )

        with pytest.raises(ValueError, match="não encontrado"):
            buscar_brasilapi("00.000.000/0001-91")


# --- Fallback ---

class TestFallback:
    @respx.mock
    def test_fallback_para_brasilapi(self):
        fixture = carregar_fixture("magazineluiza")
        cnpj_limpo = fixture["_meta"]["limpo"]

        respx.get(f"https://publica.cnpj.ws/cnpj/{cnpj_limpo}").mock(
            return_value=httpx.Response(500)
        )
        respx.get(f"https://brasilapi.com.br/api/cnpj/v1/{cnpj_limpo}").mock(
            return_value=httpx.Response(200, json=fixture)
        )

        resultado = buscar("47.960.950/0001-21")
        assert resultado["_fonte"] == "brasilapi"
