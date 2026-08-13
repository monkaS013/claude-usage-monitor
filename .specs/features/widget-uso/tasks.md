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
| T8 | Documentação + commit final | T5–T7 | notas do projeto atualizadas; commits atômicos |

Status (24/07): T1–T4, T6, T7 ✅. T6 = review adversarial (3 lentes × verificadores): 16 findings, 13 confirmados (~9 únicos), TODOS corrigidos e re-validados — stdin utf-8 via buffer (acento no cwd derrubava o coletor), tick com after em finally + shape-hardening (polling não morre mais), localtime guardado (epoch ms), retry no os.replace + cleanup de .tmp, validação de posição contra o desktop virtual (multi-monitor), largura escalada por DPI (150%), barras esmaecidas + "janela resetada" quando a janela venceu, "parado há" humanizado (10h40/2d), drag só grava config com movimento real, last_stdin.json só quando rate_limits falta, install.ps1 + README. 3 findings refutados empiricamente (lock de porta efêmera ×2, wrap de ids do Canvas). Testes: 4 cenários do coletor OK + widget vivo sob arquivo malformado (screenshots). Extra: mascote pixel-art animado (pedido mid-turn). T5 ✅ (24/07): causa-raiz do "não aparece" era o `statusLine.command` com backslashes (`C:\Python314\...`) — o spawn passa por shell estilo bash que engole `\` e falha SILENCIOSAMENTE (sem linha, sem erro). Corrigido p/ a forma dos hooks (`python "C:/.../statusline.py"`) → dados reais fluindo (5h 16% / semana 2%, barras verdes, updated_at avançando) SEM precisar de sessão nova — o statusLine é relido a quente; o "só ativa em sessão nova" de 23/07 era artefato do comando quebrado. T8 ✅. **Feature 100% validada ponta a ponta.**
