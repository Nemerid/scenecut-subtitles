#!/usr/bin/env python3
"""
Scene Cut Subtitles — Pont VLC
Application desktop pour connecter Scene Cut à VLC media player.
Double-cliquer pour lancer, puis cliquer "Connecter VLC" dans Scene Cut.
"""

import asyncio
import json
import os
import sys
import tempfile
import threading
import tkinter as tk
from tkinter import font as tkfont
import urllib.parse

try:
    import aiohttp
    import websockets
except ImportError as e:
    # Afficher une erreur conviviale si les deps manquent (ne devrait pas arriver avec le binaire)
    import tkinter.messagebox as mb
    root = tk.Tk(); root.withdraw()
    mb.showerror("Dépendance manquante",
        f"Bibliothèque manquante : {e}\n\nVeuillez contacter votre administrateur.")
    sys.exit(1)

# ── Configuration ────────────────────────────────────────────────────────────
VLC_HOST     = "http://localhost:8080"
VLC_PASSWORD = "scenecut"
WS_PORT      = 8765
POLL_MS      = 40
VERSION      = "1.1"

SUBTITLE_FILE = os.path.join(tempfile.gettempdir(), "scenecut_sub.srt")

# ── État partagé (thread-safe via GIL pour les types simples) ────────────────
_gui_ref = None   # référence à l'objet GUI pour les callbacks depuis asyncio


# ── Logique bridge (asyncio) ─────────────────────────────────────────────────

def make_auth():
    return aiohttp.BasicAuth("", VLC_PASSWORD)


async def vlc_request(session, path=""):
    url = f"{VLC_HOST}/requests/status.json{path}"
    async with session.get(
        url, auth=make_auth(), timeout=aiohttp.ClientTimeout(total=1),
    ) as r:
        return await r.json(content_type=None)


async def poll_loop(ws, session):
    last_ms = -1
    while True:
        try:
            data    = await vlc_request(session)
            time_ms = round(data.get("time", 0) * 1000)
            state   = data.get("state", "stopped")
            if time_ms != last_ms:
                last_ms = time_ms
                await ws.send(json.dumps({
                    "type": "timeupdate", "ms": time_ms, "state": state,
                }))
            if _gui_ref:
                _gui_ref.set_vlc_status("ok", f"VLC {state}")
        except asyncio.CancelledError:
            raise
        except Exception:
            if _gui_ref:
                _gui_ref.set_vlc_status("error", "VLC non détecté")
        await asyncio.sleep(POLL_MS / 1000)


async def reload_with_subtitle(session):
    data       = await vlc_request(session)
    saved_time = data.get("time", 0)
    plid       = data.get("currentplid", -1)

    if plid >= 0:
        await vlc_request(session, f"?command=pl_play&id={plid}")
        await asyncio.sleep(0.7)
        await vlc_request(session, "?command=pl_pause")
        await asyncio.sleep(0.1)
        await vlc_request(session, f"?command=seek&val={int(saved_time)}")
        await asyncio.sleep(0.15)

    encoded = urllib.parse.quote(SUBTITLE_FILE, safe="/")
    await vlc_request(session, f"?command=addsubtitle&val={encoded}")


async def handle_client(ws):
    addr = getattr(ws, "remote_address", "?")
    if _gui_ref:
        _gui_ref.set_sc_status("ok", f"Scene Cut connecté")

    async with aiohttp.ClientSession() as session:
        poll_task = asyncio.create_task(poll_loop(ws, session))
        try:
            async for raw in ws:
                try:
                    msg = json.loads(raw)

                    if msg.get("type") == "seek":
                        ms = float(msg["ms"])
                        val = int(ms / 1000)
                        print(f"  → Seek : ms={ms}  val={val}", flush=True)
                        await vlc_request(session, f"?command=seek&val={val}")

                    elif msg.get("type") == "transport":
                        action = msg.get("action")
                        if action == "play_pause":
                            await vlc_request(session, "?command=pl_pause")
                        elif action == "seek_rel":
                            delta_s = float(msg.get("delta_ms", 0)) / 1000
                            sign = "%2B" if delta_s >= 0 else "-"
                            await vlc_request(session, f"?command=seek&val={sign}{abs(delta_s):.3f}")
                        elif action == "frame_step":
                            await vlc_request(session, "?command=frame")

                    elif msg.get("type") == "subtitles":
                        srt = msg.get("srt", "")
                        with open(SUBTITLE_FILE, "w", encoding="utf-8") as f:
                            f.write(srt)
                        await reload_with_subtitle(session)

                except Exception:
                    pass
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            poll_task.cancel()
            if _gui_ref:
                _gui_ref.set_sc_status("idle", "En attente de Scene Cut…")
                _gui_ref.set_vlc_status("idle", "—")


_current_loop  = None
_stop_event    = None   # asyncio.Event — signale l'arrêt propre du serveur


async def run_server():
    global _stop_event
    _stop_event = asyncio.Event()
    if _gui_ref:
        _gui_ref.set_sc_status("idle", "En attente de Scene Cut…")
    try:
        async with websockets.serve(handle_client, None, WS_PORT):
            await _stop_event.wait()   # attend le signal d'arrêt
    except OSError:
        if _gui_ref:
            _gui_ref.set_sc_status("error", f"Port {WS_PORT} occupé — cliquer Relancer")


def start_asyncio_loop():
    global _current_loop
    loop = asyncio.new_event_loop()
    _current_loop = loop
    asyncio.set_event_loop(loop)
    loop.run_until_complete(run_server())


def restart_server():
    global _current_loop, _stop_event
    if _gui_ref:
        _gui_ref.set_sc_status("idle", "Redémarrage…")
        _gui_ref.set_vlc_status("idle", "—")
    # Signaler l'arrêt propre — le async with se ferme et libère le port
    if _current_loop and _stop_event and _current_loop.is_running():
        _current_loop.call_soon_threadsafe(_stop_event.set)
        # Lancer le nouveau serveur après que le port soit libéré
        threading.Timer(0.6, lambda: threading.Thread(
            target=start_asyncio_loop, daemon=True
        ).start()).start()
    else:
        threading.Thread(target=start_asyncio_loop, daemon=True).start()


# ── Interface graphique ──────────────────────────────────────────────────────

DARK_BG    = "#1a1a2e"
CARD_BG    = "#16213e"
TEXT_MAIN  = "#e2e8f0"
TEXT_DIM   = "#94a3b8"
VIOLET     = "#8b5cf6"
GREEN      = "#22c55e"
RED        = "#ef4444"
ORANGE     = "#f97316"
IDLE_COLOR = "#475569"

STATUS_COLORS = {
    "ok":    GREEN,
    "error": RED,
    "idle":  IDLE_COLOR,
    "warn":  ORANGE,
}


class BridgeGUI:
    def __init__(self, root):
        global _gui_ref
        _gui_ref = self
        self.root = root
        self._build_ui()

    def _build_ui(self):
        r = self.root
        r.title("Scene Cut Subtitles")
        r.configure(bg=DARK_BG)
        r.resizable(False, False)

        # Titre
        title_frame = tk.Frame(r, bg=VIOLET, height=52)
        title_frame.pack(fill="x")
        title_frame.pack_propagate(False)

        tk.Label(
            title_frame, text="Scene Cut Subtitles",
            bg=VIOLET, fg="white",
            font=("Helvetica", 14, "bold"),
        ).pack(side="left", padx=16, pady=14)

        tk.Label(
            title_frame, text=f"v{VERSION}",
            bg=VIOLET, fg="#ddd6fe",
            font=("Helvetica", 10),
        ).pack(side="right", padx=16, pady=18)

        # Carte statuts
        card = tk.Frame(r, bg=CARD_BG, padx=20, pady=16)
        card.pack(fill="x", padx=16, pady=(14, 0))

        tk.Label(card, text="ÉTAT", bg=CARD_BG, fg=TEXT_DIM,
                 font=("Helvetica", 9, "bold")).grid(row=0, column=0, columnspan=3,
                 sticky="w", pady=(0, 8))

        # VLC
        tk.Label(card, text="VLC", bg=CARD_BG, fg=TEXT_DIM,
                 font=("Helvetica", 10), width=9, anchor="w").grid(row=1, column=0, sticky="w")
        self._vlc_dot = tk.Label(card, text="●", bg=CARD_BG, fg=IDLE_COLOR,
                                  font=("Helvetica", 12))
        self._vlc_dot.grid(row=1, column=1, padx=(0, 8))
        self._vlc_lbl = tk.Label(card, text="—", bg=CARD_BG, fg=TEXT_DIM,
                                  font=("Helvetica", 10), anchor="w")
        self._vlc_lbl.grid(row=1, column=2, sticky="w")

        # Scene Cut
        tk.Label(card, text="Scene Cut", bg=CARD_BG, fg=TEXT_DIM,
                 font=("Helvetica", 10), width=9, anchor="w").grid(row=2, column=0, sticky="w",
                 pady=(8, 0))
        self._sc_dot = tk.Label(card, text="●", bg=CARD_BG, fg=IDLE_COLOR,
                                 font=("Helvetica", 12))
        self._sc_dot.grid(row=2, column=1, padx=(0, 8), pady=(8, 0))
        self._sc_lbl = tk.Label(card, text="Démarrage…", bg=CARD_BG, fg=TEXT_DIM,
                                 font=("Helvetica", 10), anchor="w")
        self._sc_lbl.grid(row=2, column=2, sticky="w", pady=(8, 0))

        # Instructions VLC
        info = tk.Frame(r, bg=DARK_BG, padx=16)
        info.pack(fill="x", pady=(14, 0))

        tk.Label(info, text="Configuration VLC (une seule fois) :", bg=DARK_BG,
                 fg=TEXT_DIM, font=("Helvetica", 9, "bold"), anchor="w").pack(fill="x")

        instructions = (
            "Préférences → Tout afficher → Interface\n"
            "→ Interfaces principales → cocher Web\n"
            "→ Lua → Lua HTTP → Mot de passe : scenecut\n"
            "Redémarrer VLC, puis cliquer Connecter VLC dans Scene Cut."
        )
        tk.Label(info, text=instructions, bg=DARK_BG, fg=TEXT_DIM,
                 font=("Helvetica", 9), justify="left", anchor="w",
                 wraplength=340).pack(fill="x", pady=(4, 0))

        # Boutons — tk.Label pour forcer les couleurs (tk.Button ignore bg sur macOS)
        btn_frame = tk.Frame(r, bg=DARK_BG)
        btn_frame.pack(pady=16)

        def make_btn(parent, text, bg, hover_bg, command):
            lbl = tk.Label(parent, text=text, bg=bg, fg="white",
                           font=("Helvetica", 10, "bold"),
                           padx=18, pady=7, cursor="hand2")
            lbl.pack(side="left", padx=6)
            lbl.bind("<Button-1>", lambda e: command())
            lbl.bind("<Enter>",    lambda e: lbl.configure(bg=hover_bg))
            lbl.bind("<Leave>",    lambda e: lbl.configure(bg=bg))
            return lbl

        make_btn(btn_frame, "  Relancer  ", "#334155", "#475569", restart_server)
        make_btn(btn_frame, "  Quitter  ",  VIOLET,    "#7c3aed",  self.root.destroy)

        # Centrer la fenêtre maintenant que tous les widgets sont créés
        r.update_idletasks()
        w = max(380, r.winfo_reqwidth())
        h = max(300, r.winfo_reqheight())
        sw = r.winfo_screenwidth()
        sh = r.winfo_screenheight()
        r.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")

    def set_vlc_status(self, status: str, text: str):
        color = STATUS_COLORS.get(status, IDLE_COLOR)
        self.root.after(0, lambda: (
            self._vlc_dot.configure(fg=color),
            self._vlc_lbl.configure(fg=TEXT_MAIN if status == "ok" else TEXT_DIM, text=text),
        ))

    def set_sc_status(self, status: str, text: str):
        color = STATUS_COLORS.get(status, IDLE_COLOR)
        self.root.after(0, lambda: (
            self._sc_dot.configure(fg=color),
            self._sc_lbl.configure(fg=TEXT_MAIN if status == "ok" else TEXT_DIM, text=text),
        ))


# ── Point d'entrée ───────────────────────────────────────────────────────────

def main():
    root = tk.Tk()
    gui  = BridgeGUI(root)

    # Lancer le bridge dans un thread daemon
    t = threading.Thread(target=start_asyncio_loop, daemon=True)
    t.start()

    root.mainloop()


if __name__ == "__main__":
    main()
