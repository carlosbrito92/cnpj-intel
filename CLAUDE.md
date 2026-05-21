# CNPJ Intelligence CLI — Contrato do Projeto

## O que é
CLI Python que recebe um CNPJ e produz relatório PDF de inteligência empresarial,
orquestrando agentes especializados via Python puro.

## Não-objetivos
- Não é um web app
- Não substitui due diligence humana — produz briefing pré-analisado
- Não acessa dados privados ou de cadastros restritos

## Convenções inegociáveis
- Commits em PT-BR
- Um arquivo por vez no protocolo navigator/pilot
- Toda mudança em `src/` tem teste correspondente em `tests/`
- Modo público é o default; modo interno nunca é demonstrado publicamente
- Nenhum dado de caso real do Ruvixx em qualquer commit

## Stack fixada
- Python 3.11+, uv, typer, httpx, weasyprint, jinja2
- CLI: typer + rich + tqdm
- Lint/format: ruff
- Testes: pytest + respx

## Decisões arquiteturais fixadas

### Orquestrador: Python puro
Decisão tomada na Fase 4. Motivos:
- Ferramenta replicável gratuitamente (sem chave Anthropic obrigatória)
- Narrativa LinkedIn mais forte: "construí o orquestrador do zero"
- Fluxo sequencial bem definido — framework genérico seria over-engineering
- Debugging simples — sem abstração de grafo

### Claude Code CLI
Removido como orquestrador. A pasta `.claude/agents/` não é mais utilizada.

## Roteamento de modelos (não negociável sem revisão do plano)
| Agente        | Modelo                  | Provider   | Motivo                          |
|---------------|-------------------------|------------|---------------------------------|
| Cadastral     | llama-3.1-8b-instant    | Groq       | Extração de JSON estruturado    |
| Societário    | llama-3.1-8b-instant    | Groq       | Extração de JSON estruturado    |
| Red Flags     | — (sem LLM)             | —          | Heurísticas determinísticas     |
| Redator       | llama-3.1-8b-instant    | Groq       | Síntese executiva — free tier   |
| Orquestrador  | — (Python puro)         | —          | Coordenação sequencial          |

## Camadas e fronteiras
- `src/sources/`    — IO com APIs externas (sem LLM)
- `src/analysis/`   — heurísticas determinísticas (sem LLM)
- `src/agents/`     — scripts wrapper que chamam Groq diretamente
- `src/llm/`        — clientes e roteador de modelos
- `src/render/`     — geração de PDF (sem LLM)
- `src/orchestrator.py` — coordena agentes em sequência, reporta progresso via Rich
- `src/cli.py`      — entrypoint Typer

## Ambiente de desenvolvimento
Fases 0–7 inteiramente no chat navigator/pilot + terminal local.
Sem dependência de Claude Code CLI como runtime.

## Modo de operação
- `public`   → fontes públicas, output em `./output/`, sem cache
- `internal` → + SQLite local em `~/.cnpj-intel/cache.db`, audit log (v1.5+)

## Fora da v1 (não abrir escopo)
- Sherlock / OSINT
- Cruzamento entre CNPJs
- Sanções OFAC / PEP
- Web UI
- LangGraph ou frameworks de agente
- Multi-tenancy / SaaS

## Fase atual
4 — Orquestrador Python puro
