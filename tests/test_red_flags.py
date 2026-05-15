"""
Testes para src/analysis/red_flags.py
Sem rede. Sem LLM. Input fixo — output previsível.
"""

import json
import pytest
from pathlib import Path
from src.analysis.red_flags import (
    analisar,
    flag_situacao_cadastral,
    flag_capital_social_baixo,
    flag_sem_capital_social,
    flag_alteracoes_societarias_recentes,
    flag_socio_pj_irregular,
    flag_empresa_recente,
    ALTO,
    MEDIO,
    BAIXO,
)

FIXTURES = Path("tests/fixtures")


def carregar_fixture(nome: str) -> dict:
    return json.loads((FIXTURES / f"{nome}.json").read_text())


# --- flag_situacao_cadastral ---

class TestSituacaoCadastral:
    def test_ativa_nao_gera_flag(self):
        assert flag_situacao_cadastral({"situacao_cadastral": "ATIVA"}) is None

    def test_suspensa_gera_flag_alto(self):
        resultado = flag_situacao_cadastral({"situacao_cadastral": "SUSPENSA"})
        assert resultado is not None
        assert resultado["severidade"] == ALTO
        assert resultado["codigo"] == "SITUACAO_IRREGULAR"

    def test_baixada_gera_flag_alto(self):
        resultado = flag_situacao_cadastral({"situacao_cadastral": "BAIXADA"})
        assert resultado["severidade"] == ALTO

    def test_ausente_gera_flag(self):
        resultado = flag_situacao_cadastral({})
        assert resultado is not None


# --- flag_capital_social ---

class TestCapitalSocial:
    def test_capital_normal_nao_gera_flag(self):
        assert flag_capital_social_baixo({"capital_social": 100000}) is None

    def test_capital_baixo_gera_flag_medio(self):
        resultado = flag_capital_social_baixo({"capital_social": 500})
        assert resultado is not None
        assert resultado["severidade"] == MEDIO
        assert resultado["codigo"] == "CAPITAL_SOCIAL_BAIXO"

    def test_capital_zero_nao_gera_flag_baixo(self):
        # zero é tratado por flag_sem_capital_social, não por esta
        assert flag_capital_social_baixo({"capital_social": 0}) is None

    def test_capital_zerado_gera_flag_sem_capital(self):
        resultado = flag_sem_capital_social({"capital_social": 0})
        assert resultado is not None
        assert resultado["codigo"] == "SEM_CAPITAL_SOCIAL"

    def test_capital_ausente_gera_flag_sem_capital(self):
        resultado = flag_sem_capital_social({})
        assert resultado is not None


# --- flag_socio_pj_irregular ---

class TestSocioPjIrregular:
    def test_sem_socios_nao_gera_flag(self):
        assert flag_socio_pj_irregular({}) is None

    def test_socio_pj_ativo_nao_gera_flag(self):
        dados = {"qsa": [{"tipo": "PJ", "nome": "HOLDING X", "situacao_cadastral": "ATIVA"}]}
        assert flag_socio_pj_irregular(dados) is None

    def test_socio_pj_irregular_gera_flag_alto(self):
        dados = {"qsa": [{"tipo": "PJ", "nome": "HOLDING X", "situacao_cadastral": "SUSPENSA"}]}
        resultado = flag_socio_pj_irregular(dados)
        assert resultado is not None
        assert resultado["severidade"] == ALTO
        assert "HOLDING X" in resultado["descricao"]

    def test_socio_pf_ignorado(self):
        dados = {"qsa": [{"tipo": "PF", "nome": "JOAO SILVA", "situacao_cadastral": "SUSPENSA"}]}
        assert flag_socio_pj_irregular(dados) is None


# --- flag_empresa_recente ---

class TestEmpresaRecente:
    def test_empresa_antiga_nao_gera_flag(self):
        assert flag_empresa_recente({"data_inicio_atividade": "2010-01-01"}) is None

    def test_empresa_recente_gera_flag_baixo(self):
        from datetime import date, timedelta
        data = (date.today() - timedelta(days=30)).strftime("%Y-%m-%d")
        resultado = flag_empresa_recente({"data_inicio_atividade": data})
        assert resultado is not None
        assert resultado["severidade"] == BAIXO

    def test_sem_data_nao_gera_flag(self):
        assert flag_empresa_recente({}) is None


# --- analisar (integração) ---

class TestAnalisar:
    def test_petrobras_sem_flags_criticos(self):
        fixture = carregar_fixture("petrobras")
        resultado = analisar(fixture)
        assert resultado["por_severidade"]["alto"] == 0

    def test_retorna_estrutura_correta(self):
        fixture = carregar_fixture("itau")
        resultado = analisar(fixture)
        assert "flags" in resultado
        assert "total" in resultado
        assert "por_severidade" in resultado

    def test_empresa_irregular_gera_flags(self):
        dados = {
            "situacao_cadastral": "SUSPENSA",
            "capital_social": 0,
            "_meta": {"formatado": "00.000.000/0001-00"},
        }
        resultado = analisar(dados)
        assert resultado["total"] >= 2
        assert resultado["por_severidade"]["alto"] >= 1
