# cnpj-intel

> CLI de inteligência empresarial via CNPJ — pipeline multi-agente com Claude Code.

![Status](https://img.shields.io/badge/status-em%20construção-yellow)
![Python](https://img.shields.io/badge/python-3.11%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

## O que é

`cnpj-intel` recebe um CNPJ e produz um relatório PDF de inteligência empresarial,
orquestrando subagentes Claude Code especializados com roteamento de modelos por custo.

```bash
cnpj-intel 12.345.678/0001-90 --output pdf
```

## Status

🚧 **Em construção — v1 em desenvolvimento ativo.**

Acompanhe o processo na série [Building in the Open](#) no LinkedIn.

## Arquitetura

Pipeline multi-agente com least privilege em duas dimensões: permissões de ferramentas e nível de modelo.
Orquestrador (Claude Sonnet)
├── agente-cadastral   → Groq llama-8b  — extração de dados cadastrais
├── agente-societario  → Groq llama-8b  — quadro societário
├── agente-red-flags   → Python puro    — heurísticas determinísticas
└── agente-redator     → Claude Haiku   — síntese executiva em PDF

Custo estimado por relatório: **R$ 0,07 a R$ 0,20**.

## Instalação

```bash
# Requer Python 3.11+ e uv
uv tool install git+https://github.com/carlosbrito92/cnpj-intel
```

## Configuração

```bash
cp .env.example .env
# Preencha ANTHROPIC_API_KEY e GROQ_API_KEY
```

## Uso

```bash
# Relatório PDF (modo público, default)
cnpj-intel 12.345.678/0001-90

# Saída em markdown
cnpj-intel 12.345.678/0001-90 --output md

# Modo interno (requer configuração local)
cnpj-intel 12.345.678/0001-90 --mode internal
```

## Uso ético

Esta ferramenta consulta exclusivamente dados públicos disponibilizados pela Receita Federal
via APIs abertas. Não acessa cadastros restritos, dados privados ou informações de pessoas físicas além
do necessário para identificação societária. O uso para fins de assédio, fraude ou vigilância
não autorizada é expressamente vedado.

## Roadmap

- [x] Fase 0 — Setup e fundação
- [ ] Fase 1 — Camada de dados (CNPJ.ws + BrasilAPI)
- [ ] Fase 2 — Red flags determinísticos
- [ ] Fase 3 — Renderização de PDF
- [ ] Fase 3.5 — Camada LLM e agentes Python
- [ ] Fase 4 — Subagentes Claude Code
- [ ] Fase 5 — Orquestrador e CLI
- [ ] Fase 6 — Modo interno e cache
- [ ] Fase 7 — Polimento para portfólio

## License

MIT © Carlos Brito
