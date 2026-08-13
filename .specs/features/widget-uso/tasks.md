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

Status: T1 em andamento.
