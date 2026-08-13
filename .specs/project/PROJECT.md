# Monitor de uso do Claude

**Visão:** widget local no Windows 11, sempre visível, mostrando os percentuais REAIS de uso do plano Claude (sessão 5h + semana, mesmos números do `/usage`), sem abrir o app Claude.

**Restrição central (decisão do Vinicius, 23/07/2026):** usar SOMENTE o caminho oficial — o Claude Code (≥2.1.80; instalado: 2.1.216) entrega `rate_limits` no stdin do script de statusline. Zero token OAuth, zero endpoint não documentado, zero chamadas de rede.

**Arquitetura (2 processos + 1 arquivo):**

```
Claude Code ──stdin──▶ statusline.py ──grava──▶ ~/.claude/usage-monitor/rate_limits.json
                            │                                    ▲
                            ▼                                    │ lê (polling mtime)
                     linha de status                        widget.pyw (Tkinter,
                     dentro do Claude Code                  sempre-no-topo)
```

**Fora de escopo (v1):** custo estimado, histórico/gráfico, sub-quotas por modelo (statusline não entrega), tray icon.

Pesquisa que fundamentou as decisões: vault `Projetos/Monitor de uso Claude.md`.
