"""Coletor de statusline do Claude Code.

Recebe o JSON de sessão no stdin (doc: code.claude.com/docs/en/statusline),
persiste os rate_limits em ~/.claude/usage-monitor/ para o widget e imprime
uma linha de status para o próprio Claude Code.

Restrições: stdlib apenas; nunca lançar exceção (statusline não pode quebrar).
"""

import json
import os
import sys
import tempfile
import time

DATA_DIR = os.path.join(os.path.expanduser("~"), ".claude", "usage-monitor")


def atomic_write_json(path: str, payload: dict) -> None:
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(path), suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, ensure_ascii=False)
        for _ in range(3):
            try:
                os.replace(tmp, path)
                return
            except PermissionError:
                # o leitor (widget) pode segurar o destino por alguns ms no Windows
                time.sleep(0.01)
        os.replace(tmp, path)
    except OSError:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def cleanup_tmp(now: float) -> None:
    # .tmp órfãos de processos mortos entre mkstemp e replace
    try:
        for name in os.listdir(DATA_DIR):
            if name.endswith(".tmp"):
                path = os.path.join(DATA_DIR, name)
                try:
                    if now - os.path.getmtime(path) > 3600:
                        os.unlink(path)
                except OSError:
                    pass
    except OSError:
        pass


def window(raw: dict | None) -> dict | None:
    # rate_limits pode faltar até a 1ª resposta de API; cada janela pode faltar.
    if not isinstance(raw, dict):
        return None
    pct = raw.get("used_percentage")
    if not isinstance(pct, (int, float)):
        return None
    resets = raw.get("resets_at")
    if not isinstance(resets, (int, float)) or not 0 < resets < 4e9:
        resets = None  # epoch em ms/lixo estouraria time.localtime no Windows
    return {"pct": max(0.0, min(100.0, float(pct))), "resets_at": resets}


def main() -> None:
    # stdin pode vir como cp1252 no spawn da statusline; caminhos no JSON têm acento
    raw = sys.stdin.buffer.read().decode("utf-8", "replace")
    data = json.loads(raw or "{}")

    now = time.time()
    os.makedirs(DATA_DIR, exist_ok=True)
    cleanup_tmp(now)

    limits = data.get("rate_limits") or {}
    five = window(limits.get("five_hour"))
    seven = window(limits.get("seven_day"))
    if five or seven:
        try:
            atomic_write_json(
                os.path.join(DATA_DIR, "rate_limits.json"),
                {"five_hour": five, "seven_day": seven, "updated_at": int(now)},
            )
        except OSError:
            pass  # colisão com o leitor: perde 1 ciclo, o próximo refresh corrige
    else:
        # sem rate_limits (1ª resposta ainda não veio ou o formato mudou) → stdin p/ debug
        try:
            atomic_write_json(os.path.join(DATA_DIR, "last_stdin.json"), data)
        except OSError:
            pass

    model = (data.get("model") or {}).get("display_name") or "?"
    ctx = (data.get("context_window") or {}).get("used_percentage")
    parts = [f"[{model}]"]
    if isinstance(ctx, (int, float)):
        parts.append(f"ctx {ctx:.0f}%")
    parts.append(f"5h {five['pct']:.0f}%" if five else "5h —")
    parts.append(f"sem {seven['pct']:.0f}%" if seven else "sem —")
    print(" · ".join(parts))


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        main()
    except Exception:  # noqa: BLE001 — statusline nunca pode quebrar
        print("[usage-monitor] sem dados")
