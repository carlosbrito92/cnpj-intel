"""
Testes para src/sources/normalize.py
Sem rede. Sem LLM. 100% determinístico.
"""

import pytest
from src.sources.normalize import limpar, validar, formatar, normalizar


class TestLimpar:
    def test_remove_pontuacao(self):
        assert limpar("33.000.167/0001-01") == "33000167000101"

    def test_ja_limpo(self):
        assert limpar("33000167000101") == "33000167000101"

    def test_remove_espacos(self):
        assert limpar("33 000 167 0001 01") == "33000167000101"


class TestValidar:
    def test_cnpj_valido_petrobras(self):
        assert validar("33000167000101") is True

    def test_cnpj_valido_itau(self):
        assert validar("60701190000104") is True

    def test_cnpj_invalido_digito(self):
        assert validar("33000167000100") is False

    def test_cnpj_invalido_zeros(self):
        assert validar("00000000000000") is False

    def test_cnpj_invalido_curto(self):
        assert validar("1234") is False


class TestFormatar:
    def test_formata_corretamente(self):
        assert formatar("33000167000101") == "33.000.167/0001-01"

    def test_formata_itau(self):
        assert formatar("60701190000104") == "60.701.190/0001-04"

    def test_levanta_erro_invalido(self):
        with pytest.raises(ValueError):
            formatar("1234")


class TestNormalizar:
    def test_retorna_dict_completo(self):
        resultado = normalizar("33.000.167/0001-01")
        assert resultado["limpo"] == "33000167000101"
        assert resultado["formatado"] == "33.000.167/0001-01"
        assert resultado["valido"] is True

    def test_aceita_sem_formatacao(self):
        resultado = normalizar("33000167000101")
        assert resultado["formatado"] == "33.000.167/0001-01"

    def test_levanta_erro_cnpj_invalido(self):
        with pytest.raises(ValueError):
            normalizar("11111111111111")
