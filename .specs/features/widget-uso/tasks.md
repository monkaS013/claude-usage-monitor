# Tasks — widget-uso v1

| # | Task | Depende | Done when |
|---|------|---------|-----------|
| T1 | Esqueleto do projeto + git init | — | dirs criados, git inicializado |
| T2 | `statusline.py` (R1) | T1 | teste com stdin simulado gera JSON correto + linha de status; exceção simulada não quebra |
| T3 | `widget.pyw` (R2, R3) | T1 | com JSON simulado: barras/cores/countdown/carimbo corretos; arrasto persiste posição; instância única |
| T4 | Configurar `statusLine` em settings.json (backup antes) | T2 | settings válido (JSON parse) + backup criado |
| T5 | Validação real ponta a ponta | T2–T4 | `rate_limits.json` gravado por sessão real; % do widget = `/usage` |
| T6 | Review adversarial (workflow multi-lente) + fixes | T2–T3 | findings confirmados corrigidos |
| T7 | Atalho Startup + iniciar widget (R4) | T3, T5 | .lnk na pasta Startup; widget rodando |
| T8 | Registro vault + memória + commit final | T5–T7 | nota do projeto atualizada; commits atômicos |

Status (24/07): T1–T4, T6, T7 ✅. T6 = review adversarial (3 lentes × verificadores): 16 findings, 13 confirmados (~9 únicos), TODOS corrigidos e re-validados — stdin utf-8 via buffer (acento no cwd derrubava o coletor), tick com after em finally + shape-hardening (polling não morre mais), localtime guardado (epoch ms), retry no os.replace + cleanup de .tmp, validação de posição contra o desktop virtual (multi-monitor), largura escalada por DPI (150%), barras esmaecidas + "janela resetada" quando a janela venceu, "parado há" humanizado (10h40/2d), drag só grava config com movimento real, last_stdin.json só quando rate_limits falta, install.ps1 + README. 3 findings refutados empiricamente (lock de porta efêmera ×2, wrap de ids do Canvas). Testes: 4 cenários do coletor OK + widget vivo sob arquivo malformado (screenshots). Extra: mascote pixel-art animado (pedido mid-turn). **T5 (única pendência): abrir uma sessão NOVA do Claude Code** → statusline aparece e o widget converge pro `/usage`. T8 ✅.
