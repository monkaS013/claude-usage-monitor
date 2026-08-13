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

DATA_DIR = os.path.join(os.path.expanduser("~"), ".claude", "usage-monitor")


def atomic_write_json(path: str, payload: dict) -> None:
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(path), suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, ensure_ascii=False)
        os.replace(tmp, path)
    except OSError:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def window(raw: dict | None) -> dict | None:
    # rate_limits pode faltar até a 1ª resposta de API; cada janela pode faltar.
    if not isinstance(raw, dict):
        return None
    pct = raw.get("used_percentage")
    if not isinstance(pct, (int, float)):
        return None
    return {"pct": max(0.0, min(100.0, float(pct))), "resets_at": raw.get("resets_at")}


def main() -> None:
    import time

    data = json.loads(sys.stdin.read() or "{}")

    os.makedirs(DATA_DIR, exist_ok=True)
    atomic_write_json(os.path.join(DATA_DIR, "last_stdin.json"), data)

    limits = data.get("rate_limits") or {}
    five = window(limits.get("five_hour"))
    seven = window(limits.get("seven_day"))
    if five or seven:
        atomic_write_json(
            os.path.join(DATA_DIR, "rate_limits.json"),
            {"five_hour": five, "seven_day": seven, "updated_at": int(time.time())},
        )

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
