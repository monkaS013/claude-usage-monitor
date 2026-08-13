"""Widget flutuante de uso do plano Claude (sessão 5h + semana).

Lê ~/.claude/usage-monitor/rate_limits.json (gravado pelo statusline.py) e
exibe duas barras sempre-no-topo. Zero rede, zero credenciais, stdlib apenas.
"""

import ctypes
import json
import os
import socket
import time
import tkinter as tk
import tkinter.font as tkfont

DATA_DIR = os.path.join(os.path.expanduser("~"), ".claude", "usage-monitor")
DATA_FILE = os.path.join(DATA_DIR, "rate_limits.json")
CONFIG_FILE = os.path.join(DATA_DIR, "config.json")
SINGLE_INSTANCE_PORT = 53764
STALE_AFTER_S = 15 * 60

# Paleta validada p/ superfície escura (skill dataviz, references/palette.md)
SURFACE = "#1a1a19"
TROUGH = "#2c2c2a"
BORDER = "#383835"
INK = "#ffffff"
INK_2 = "#c3c2b7"
MUTED = "#898781"
STATUS = [(95, "#d03b3b"), (85, "#ec835a"), (60, "#fab219"), (0, "#0ca30c")]

WEEKDAYS_PT = ["seg", "ter", "qua", "qui", "sex", "sáb", "dom"]

# Mascote pixel-art do Claude Code (cor terracota da marca), animado por "bob"
CLAUDE_ORANGE = "#d97757"
SPRITE = [
    "..XX......XX..",
    "..XX......XX..",
    ".XXXXXXXXXXXX.",
    ".XXXXXXXXXXXX.",
    "XXXXXXXXXXXXXX",
    "XXXXXXXXXXXXXX",
    ".XXXXXXXXXXXX.",
    ".XXXXXXXXXXXX.",
    "..XX..XX..XX..",
]
SPRITE_CELL = 3


def status_color(pct: float) -> str:
    for floor, color in STATUS:
        if pct >= floor:
            return color
    return STATUS[-1][1]


def fmt_reset(resets_at, now: float) -> str:
    if not isinstance(resets_at, (int, float)):
        return ""
    delta = resets_at - now
    if delta <= 0:
        return "janela resetada"
    if delta < 48 * 3600:
        h, m = int(delta // 3600), int(delta % 3600 // 60)
        return f"reseta em {h}h{m:02d}" if h else f"reseta em {m}min"
    lt = time.localtime(resets_at)
    return f"reseta {WEEKDAYS_PT[lt.tm_wday]} {lt.tm_hour:02d}:{lt.tm_min:02d}"


class Meter:
    """Barra fina com pontas arredondadas (r=4) sobre trilho, no padrão dataviz."""

    HEIGHT = 8

    def __init__(self, parent: tk.Widget, label: str, fonts: dict):
        self.frame = tk.Frame(parent, bg=SURFACE)
        head = tk.Frame(self.frame, bg=SURFACE)
        head.pack(fill="x")
        tk.Label(head, text=label, bg=SURFACE, fg=INK_2, font=fonts["label"]).pack(side="left")
        self.pct_lbl = tk.Label(head, text="—", bg=SURFACE, fg=INK, font=fonts["value"])
        self.pct_lbl.pack(side="right")
        self.canvas = tk.Canvas(self.frame, height=self.HEIGHT, bg=SURFACE, highlightthickness=0)
        self.canvas.pack(fill="x", pady=(3, 1))
        self.reset_lbl = tk.Label(self.frame, text="", bg=SURFACE, fg=MUTED, font=fonts["small"], anchor="w")
        self.reset_lbl.pack(fill="x")
        self.pct: float | None = None
        self.canvas.bind("<Configure>", lambda _e: self.redraw())

    def rounded_bar(self, w: float, color: str) -> None:
        r = self.HEIGHT / 2
        if w < 2 * r:
            w = 2 * r  # largura mínima p/ as pontas
        self.canvas.create_oval(0, 0, 2 * r, self.HEIGHT, fill=color, outline="")
        self.canvas.create_oval(w - 2 * r, 0, w, self.HEIGHT, fill=color, outline="")
        self.canvas.create_rectangle(r, 0, w - r, self.HEIGHT, fill=color, outline="")

    def redraw(self) -> None:
        self.canvas.delete("all")
        full = self.canvas.winfo_width()
        if full <= 1:
            return
        self.rounded_bar(full, TROUGH)
        if self.pct is not None and self.pct > 0:
            self.rounded_bar(full * self.pct / 100, status_color(self.pct))

    def update(self, win: dict | None, now: float) -> None:
        if not win:
            self.pct = None
            self.pct_lbl.config(text="—", fg=MUTED)
            self.reset_lbl.config(text="sem dados")
        else:
            self.pct = win["pct"]
            self.pct_lbl.config(text=f"{win['pct']:.0f}%", fg=INK)
            self.reset_lbl.config(text=fmt_reset(win.get("resets_at"), now))
        self.redraw()


class Widget:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.withdraw()
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.configure(bg=BORDER)  # borda de 1px via padding do frame externo

        body = tk.Frame(self.root, bg=SURFACE)
        body.pack(fill="both", expand=True, padx=1, pady=1)

        fonts = {
            "title": tkfont.Font(family="Segoe UI", size=9, weight="bold"),
            "label": tkfont.Font(family="Segoe UI", size=9),
            "value": tkfont.Font(family="Segoe UI", size=10, weight="bold"),
            "small": tkfont.Font(family="Segoe UI", size=8),
        }

        head = tk.Frame(body, bg=SURFACE)
        head.pack(fill="x", padx=10, pady=(7, 2))
        self.sprite = tk.Canvas(head, width=len(SPRITE[0]) * SPRITE_CELL + 2,
                                height=len(SPRITE) * SPRITE_CELL + 3, bg=SURFACE, highlightthickness=0)
        self.sprite.pack(side="left", padx=(0, 6))
        self.sprite_frame = 0
        close = tk.Label(head, text="✕", bg=SURFACE, fg=MUTED, font=fonts["label"], cursor="hand2")
        close.pack(side="right")
        tk.Label(head, text="Claude", bg=SURFACE, fg=INK_2, font=fonts["title"]).pack(side="left")
        close.bind("<Button-1>", lambda _e: self.quit())
        close.bind("<Enter>", lambda _e: close.config(fg=INK))
        close.bind("<Leave>", lambda _e: close.config(fg=MUTED))

        self.five = Meter(body, "Sessão 5h", fonts)
        self.five.frame.pack(fill="x", padx=10, pady=(2, 4))
        self.seven = Meter(body, "Semana", fonts)
        self.seven.frame.pack(fill="x", padx=10, pady=(2, 4))

        self.stamp = tk.Label(body, text="aguardando dados do Claude Code…", bg=SURFACE,
                              fg=MUTED, font=fonts["small"], anchor="w")
        self.stamp.pack(fill="x", padx=10, pady=(0, 7))

        for w in (self.root, body, head, self.sprite):
            w.bind("<Button-1>", self.drag_start)
            w.bind("<B1-Motion>", self.drag_move)
            w.bind("<ButtonRelease-1>", lambda _e: self.save_config())
        self.root.bind("<Button-3>", self.context_menu)

        self.drag_off = (0, 0)
        self.mtime = 0.0
        self.data: dict = {}

        self.root.update_idletasks()
        w = 240
        h = self.root.winfo_reqheight()
        x, y = self.load_position(w, h)
        self.root.geometry(f"{w}x{h}+{x}+{y}")
        self.root.deiconify()
        self.animate_sprite()
        self.tick()

    def animate_sprite(self) -> None:
        self.sprite.delete("all")
        bob = self.sprite_frame  # alterna 0/1 px — respiração
        for r, row in enumerate(SPRITE):
            for col, ch in enumerate(row):
                if ch == "X":
                    x0 = col * SPRITE_CELL + 1
                    y0 = r * SPRITE_CELL + bob + 1
                    self.sprite.create_rectangle(x0, y0, x0 + SPRITE_CELL, y0 + SPRITE_CELL,
                                                 fill=CLAUDE_ORANGE, outline="")
        self.sprite_frame ^= 1
        self.root.after(600, self.animate_sprite)

    # ---- posição/config -------------------------------------------------
    def load_position(self, w: int, h: int) -> tuple[int, int]:
        sw, sh = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        x, y = sw - w - 16, sh - h - 60  # canto inferior direito
        try:
            with open(CONFIG_FILE, encoding="utf-8") as fh:
                cfg = json.load(fh)
            cx, cy = int(cfg["x"]), int(cfg["y"])
            if -20 <= cx <= sw - 40 and 0 <= cy <= sh - 40:  # fora da tela → default
                x, y = cx, cy
        except (OSError, ValueError, KeyError):
            pass
        return x, y

    def save_config(self) -> None:
        try:
            os.makedirs(DATA_DIR, exist_ok=True)
            with open(CONFIG_FILE, "w", encoding="utf-8") as fh:
                json.dump({"x": self.root.winfo_x(), "y": self.root.winfo_y()}, fh)
        except OSError:
            pass

    # ---- interação -------------------------------------------------------
    def drag_start(self, e: tk.Event) -> None:
        self.drag_off = (e.x_root - self.root.winfo_x(), e.y_root - self.root.winfo_y())

    def drag_move(self, e: tk.Event) -> None:
        self.root.geometry(f"+{e.x_root - self.drag_off[0]}+{e.y_root - self.drag_off[1]}")

    def context_menu(self, e: tk.Event) -> None:
        menu = tk.Menu(self.root, tearoff=0, bg=SURFACE, fg=INK_2,
                       activebackground=TROUGH, activeforeground=INK)
        menu.add_command(label="Fechar", command=self.quit)
        menu.tk_popup(e.x_root, e.y_root)

    def quit(self) -> None:
        self.save_config()
        self.root.destroy()

    # ---- dados ------------------------------------------------------------
    def tick(self) -> None:
        try:
            mtime = os.path.getmtime(DATA_FILE)
            if mtime != self.mtime:
                with open(DATA_FILE, encoding="utf-8") as fh:
                    self.data = json.load(fh)
                self.mtime = mtime
        except (OSError, ValueError):
            pass
        self.render()
        self.root.after(2000, self.tick)

    def render(self) -> None:
        now = time.time()
        if not self.data:
            self.stamp.config(text="aguardando dados do Claude Code…")
        else:
            self.five.update(self.data.get("five_hour"), now)
            self.seven.update(self.data.get("seven_day"), now)
            updated = self.data.get("updated_at") or 0
            if not updated:
                self.stamp.config(text="aguardando dados do Claude Code…")
                return
            lt = time.localtime(updated)
            text = f"atualizado às {lt.tm_hour:02d}:{lt.tm_min:02d}"
            age = now - updated
            if age > STALE_AFTER_S:
                text += f" · parado há {int(age // 60)}min"
            self.stamp.config(text=text)


def already_running() -> socket.socket | None:
    try:
        lock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        lock.bind(("127.0.0.1", SINGLE_INSTANCE_PORT))
        return lock
    except OSError:
        return None


def main() -> None:
    lock = already_running()
    if lock is None:
        return  # já há uma instância aberta
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except (AttributeError, OSError):
        pass
    app = Widget()
    app.root.mainloop()
    lock.close()


if __name__ == "__main__":
    main()
