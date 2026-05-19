"""
Testes para src/llm/groq_client.py e src/llm/router.py
Sem chamadas reais à API — mocks via unittest.mock.
"""

from unittest.mock import MagicMock, patch
import pytest
from src.llm.groq_client import complete
from src.llm.router import Tarefa, get_rota, get_modelo, get_provider


# --- Router ---

class TestRouter:
    def test_extracao_usa_groq(self):
        provider, modelo = get_rota(Tarefa.EXTRACAO)
        assert provider == "groq"
        assert "llama" in modelo

    def test_sintese_usa_anthropic(self):
        provider, modelo = get_rota(Tarefa.SINTESE)
        assert provider == "anthropic"
        assert "haiku" in modelo

    def test_orquestracao_usa_sonnet(self):
        provider, modelo = get_rota(Tarefa.ORQUESTRACAO)
        assert provider == "anthropic"
        assert "sonnet" in modelo

    def test_get_modelo_retorna_string(self):
        assert isinstance(get_modelo(Tarefa.EXTRACAO), str)

    def test_get_provider_retorna_string(self):
        assert isinstance(get_provider(Tarefa.SINTESE), str)


# --- Groq client ---

class TestGroqClient:
    @patch("src.llm.groq_client.Groq")
    def test_complete_retorna_texto(self, mock_groq_class):
        mock_choice = MagicMock()
        mock_choice.message.content = '{"resultado": "ok"}'
        mock_groq_class.return_value.chat.completions.create.return_value.choices = [mock_choice]

        with patch.dict("os.environ", {"GROQ_API_KEY": "fake-key"}):
            resultado = complete(prompt="teste")

        assert resultado == '{"resultado": "ok"}'

    @patch("src.llm.groq_client.Groq")
    def test_complete_usa_temperatura_zero(self, mock_groq_class):
        mock_choice = MagicMock()
        mock_choice.message.content = "{}"
        mock_groq_class.return_value.chat.completions.create.return_value.choices = [mock_choice]

        with patch.dict("os.environ", {"GROQ_API_KEY": "fake-key"}):
            complete(prompt="teste")

        call_kwargs = mock_groq_class.return_value.chat.completions.create.call_args.kwargs
        assert call_kwargs["temperature"] == 0.0

    def test_sem_api_key_levanta_runtime_error(self):
        with patch.dict("os.environ", {}, clear=True):
            with patch("src.llm.groq_client.os.getenv", return_value=None):
                with pytest.raises(RuntimeError, match="GROQ_API_KEY"):
                    complete(prompt="teste")
