# Claude usage monitor

*[Português](README.pt-BR.md)*

A floating Windows 11 widget that shows the **real** usage of your Claude plan — the 5-hour session and the week, the same numbers as `/usage` — without opening the Claude app.

<p align="center">
  <img src="docs/demo.gif" alt="Claude usage widget: animated pixel-art mascot and bars for the 5-hour session and the week" width="320">
</p>

## How it works

```
Claude Code ──stdin──▶ statusline.py ──▶ ~/.claude/usage-monitor/rate_limits.json ──▶ widget.pyw
```

- `statusline.py`: set as `statusLine` in `~/.claude/settings.json`. On every Claude Code refresh it writes the official `rate_limits` and prints `[Model] · ctx X% · 5h Y% · wk Z%` at the bottom of Claude Code.
- `widget.pyw`: an always-on-top window (Tkinter, pure stdlib) with two bars, a reset countdown, a refresh timestamp, and the mascot. Draggable (position persists); right-click → Close; single instance.
- **Zero network, zero tokens**: only the official, documented statusline channel.

## Install / restart

```powershell
powershell -ExecutionPolicy Bypass -File install.ps1
```

Creates the Startup shortcut (auto-start on logon) and launches the widget. To uninstall, delete the `Claude Usage Monitor.lnk` shortcut from the Startup folder (`Win+R` → `shell:startup`).

## Known limitations (v1)

- It updates while a Claude Code session is running (the statusline is event-driven). Idle, it freezes on the last value with a "stale for X" note.
- The statusline only starts in a **new** Claude Code session, and `rate_limits` arrive only after the session's first response.
- No weekly per-model sub-quotas (the official statusline doesn't expose them).
