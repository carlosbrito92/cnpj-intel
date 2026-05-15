# CNPJ Intelligence CLI — Contrato do Projeto

## O que é
CLI Python que recebe um CNPJ e produz relatório PDF de inteligência empresarial,
orquestrando subagentes Claude Code especializados.

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
- Lint/format: ruff
- Testes: pytest + respx

## Roteamento de modelos (não negociável sem revisão do plano)
| Agente        | Modelo                  | Provider   | Motivo                          |
|---------------|-------------------------|------------|---------------------------------|
| Cadastral     | llama-3.1-8b-instant    | Groq       | Extração de JSON estruturado    |
| Societário    | llama-3.1-8b-instant    | Groq       | Extração de JSON estruturado    |
| Red Flags     | — (sem LLM)             | —          | Heurísticas determinísticas     |
| Redator       | claude-haiku-4-5        | Anthropic  | Síntese executiva visível       |
| Orquestrador  | claude-sonnet-4-6       | Anthropic  | Coordenação e tratamento de falhas |

## Camadas e fronteiras
- `src/sources/`    — IO com APIs externas (sem LLM)
- `src/analysis/`   — heurísticas determinísticas (sem LLM)
- `src/agents/`     — scripts wrapper que chamam Groq diretamente; funcionam sem Claude Code ativo
- `src/llm/`        — clientes e roteador de modelos (`router.py` é o único lugar para trocar provider)
- `src/render/`     — geração de PDF (sem LLM)
- `.claude/agents/` — wrappers minimalistas Claude Code sobre `src/agents/`

## Ambiente de desenvolvimento por fase

### Fases 0–3.5 — Chat navigator/pilot (aqui)
Desenvolvimento acontece nesta conversa. Código gerado é copiado e commitado manualmente.
Abrange: setup, camada de dados, red flags, renderização de PDF, camada LLM e scripts `src/agents/`.

### Fase 4 em diante — Claude Code CLI no terminal
A partir da criação dos subagentes em `.claude/agents/`, o Claude Code passa a ser o runtime.
Gatilho concreto: `python -m src.agents.cadastral <cnpj>` funcionando com sucesso →
abrir `claude` no terminal dentro do repo e testar invocação via subagente.
O protocolo navigator/pilot continua — muda apenas o ambiente de execução.

## Modo de operação
- `public`   → fontes públicas, output em `./output/`, sem cache (demonstrável publicamente)
- `internal` → + SQLite local em `~/.cnpj-intel/cache.db`, audit log, opcional `--enable-osint` (v1.5+)

## Fora da v1 (não abrir escopo)
- Sherlock / OSINT
- Cruzamento entre CNPJs
- Sanções OFAC / PEP
- Web UI
- Ruflo
- Multi-tenancy / SaaS

## Fase atual
0 — Setup e fundação
