# Feature: widget-uso (v1)

Escopo: **Medium** — spec breve, design inline (acima no PROJECT.md), tasks em `tasks.md`.

## Requisitos

- **R1 — Coletor (statusline.py):** script de statusline configurado em `~/.claude/settings.json`. Lê o JSON do stdin, grava de forma atômica `~/.claude/usage-monitor/rate_limits.json` com `{five_hour: {pct, resets_at}, seven_day: {pct, resets_at}, updated_at}` e também `last_stdin.json` (bruto, p/ debug). Imprime uma linha de status útil (modelo + %5h + %semana). Nunca lança exceção (falha → linha mínima); rápido (<300 ms); tolera `rate_limits` ausente/parcial (campo pode faltar antes da 1ª resposta de API).
- **R2 — Widget (widget.pyw):** janela Tkinter compacta sempre-no-topo, tema escuro: barra Sessão 5h + barra Semana com %, countdown de reset ("reseta em 2h14" / "reseta seg 07:00", hora local), carimbo "atualizado às HH:MM". Cores por faixa de uso. Sem dado ainda → estado "aguardando dados do Claude Code". Dado velho (>15 min) → carimbo esmaecido/indicado.
- **R3 — Interação:** arrastável (clique e arrasta), lembra posição entre execuções (`config.json` ao lado do rate_limits.json), botão fechar, clique-direito → menu mínimo (Fechar). Instância única (lock ou mutex simples).
- **R4 — Auto-start:** atalho na pasta Startup do usuário rodando `pythonw.exe widget.pyw` (sem console).
- **R5 — Privacidade/segurança:** zero rede, zero leitura de credenciais; lê apenas o arquivo gravado pelo coletor.

## Verificação ponta a ponta

Com o Claude Code em uso, o widget mostra percentuais idênticos aos do `/usage` e atualiza sozinho; após fechar e reabrir o Windows/widget, posição preservada e último valor exibido com carimbo.

## Suposições registradas (aprovadas por silêncio na entrevista de 23/07)

- Código em `~/dev/claude-usage-monitor`; dados em `~/.claude/usage-monitor/`.
- Python 3.14 do sistema (`C:\Python314`), Tkinter incluso, zero dependências pip.
- Formato do stdin conforme doc oficial da statusline (`rate_limits.five_hour.used_percentage` 0–100 + `resets_at`); o coletor é defensivo a variações e o `last_stdin.json` permite corrigir rápido se o formato real divergir.
