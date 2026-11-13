"""Speedcube-Timer – Phase 1: UI-Grundgerüst + Farb-Event."""
import random
import sqlite3
import sys
import time
from datetime import datetime
from pathlib import Path

import customtkinter as ctk

# times.db liegt neben main.py bzw. neben der fertigen .exe
# (in der .exe zeigt __file__ auf einen Temp-Ordner -> Zeiten wären weg)
if getattr(sys, "frozen", False):
    BASE_DIR = Path(sys.executable).parent
else:
    BASE_DIR = Path(__file__).parent
DB_PATH = BASE_DIR / "times.db"

# --- Konstanten (zentral, damit wir sie später leicht ändern können) ---
COLOR_IDLE = "white"
COLOR_PRESSED = "#ff4040"   # Rot: Taste gedrückt
COLOR_RELEASED = "#40ff60"  # Grün: Taste losgelassen


class Database:
    """Speichert Zeiten lokal in SQLite."""

    def __init__(self, path=DB_PATH):
        self.conn = sqlite3.connect(path)
        self._create_table()

    def _create_table(self):
        with self.conn:  # "with" = automatisch speichern (commit)
            self.conn.execute(
                """CREATE TABLE IF NOT EXISTS solves (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    time_sec REAL NOT NULL,
                    timestamp TEXT NOT NULL
                )"""
            )

    def save_time(self, seconds: float):
        now = datetime.now().isoformat(timespec="seconds")
        with self.conn:
            self.conn.execute(
                "INSERT INTO solves (time_sec, timestamp) VALUES (?, ?)",
                (seconds, now),
            )

    def get_last_5(self) -> list[float]:
        # Neueste zuerst: höchste id = zuletzt gespeichert
        rows = self.conn.execute(
            "SELECT time_sec FROM solves ORDER BY id DESC LIMIT 5"
        ).fetchall()
        return [row[0] for row in rows]

    def get_ao5(self) -> float | None:
        times = self.get_last_5()
        if len(times) < 5:
            return None  # Ao5 braucht genau 5 Zeiten
        middle = sorted(times)[1:-1]  # schnellste + langsamste raus
        return sum(middle) / 3


class Scrambler:
    """Erzeugt zufällige Scrambles ohne gleiche Seite direkt hintereinander."""

    FACES = ["U", "D", "F", "B", "R", "L"]
    MODIFIERS = ["", "'", "2"]  # einfach, invertiert, doppelt

    def __init__(self, length: int = 20):
        self.length = length

    def generate(self) -> str:
        moves = []
        last_face = None
        for _ in range(self.length):
            face = self._pick_face(last_face)
            moves.append(face + random.choice(self.MODIFIERS))
            last_face = face
        return " ".join(moves)

    def _pick_face(self, last_face):
        # Letzte Seite ausschließen -> nie "R R'" oder "U2 U"
        allowed = [f for f in self.FACES if f != last_face]
        return random.choice(allowed)


class ScrambleBar(ctk.CTkLabel):
    """Oben: zeigt den Scramble an."""

    def __init__(self, master):
        super().__init__(master, text="R U R' U'", font=ctk.CTkFont(size=28))

    def set_scramble(self, text: str):
        self.configure(text=text)


class TimerDisplay(ctk.CTkLabel):
    """Mitte: große Zeitanzeige mit Farbwechsel."""

    def __init__(self, master):
        super().__init__(
            master, text="0.000",
            font=ctk.CTkFont(size=120, weight="bold"),
            text_color=COLOR_IDLE,
        )

    def set_color(self, color: str):
        self.configure(text_color=color)

    def set_time(self, seconds: float):
        self.configure(text=f"{seconds:.3f}")  # z.B. "12.345"


class HistorySidebar(ctk.CTkFrame):
    """Rechts: Liste der letzten 5 Zeiten."""

    def __init__(self, master):
        super().__init__(master, width=200)
        ctk.CTkLabel(self, text="Letzte 5 Zeiten",
                     font=ctk.CTkFont(size=18, weight="bold")).pack(pady=10)
        # 5 Platzhalter-Labels, die wir später mit echten Zeiten füllen
        self.rows = [ctk.CTkLabel(self, text="–") for _ in range(5)]
        for row in self.rows:
            row.pack(pady=4)
        # Ao5-Label ganz unten
        self.ao5_label = ctk.CTkLabel(
            self, text="Ao5: –", font=ctk.CTkFont(size=18, weight="bold"))
        self.ao5_label.pack(side="bottom", pady=15)

    def set_ao5(self, value: float | None):
        text = f"Ao5: {value:.3f}" if value is not None else "Ao5: –"
        self.ao5_label.configure(text=text)

    def set_times(self, times: list[float]):
        # Fehlende Zeilen bleiben "–", vorhandene zeigen "12.345"
        for i, row in enumerate(self.rows):
            text = f"{times[i]:.3f}" if i < len(times) else "–"
            row.configure(text=text)


class App(ctk.CTk):
    """Hauptfenster: baut das Layout und bindet die Leertaste."""

    def __init__(self):
        super().__init__()
        self.title("Speedcube Timer")
        self.geometry("1100x500")
        self.scrambler = Scrambler()
        self.db = Database()
        self.state = "IDLE"          # IDLE -> READY -> RUNNING -> IDLE
        self.start_time = 0.0
        self._after_id = None        # merkt sich den geplanten Update-Aufruf
        self._space_held = False     # filtert Tasten-Wiederholung beim Halten
        self._build_layout()
        self._bind_events()
        self._refresh_history()  # alte Zeiten direkt beim Start zeigen

    def _build_layout(self):
        # Spalte 0 wächst mit, Spalte 1 (Sidebar) bleibt fest
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.scramble = ScrambleBar(self)
        self.scramble.grid(row=0, column=0, pady=20, sticky="ew")

        self.timer = TimerDisplay(self)
        self.timer.grid(row=1, column=0)

        self.sidebar = HistorySidebar(self)
        self.sidebar.grid(row=0, column=1, rowspan=2, padx=10, pady=10, sticky="ns")

    def _bind_events(self):
        # Fenster-weit lauschen, egal welches Widget den Fokus hat
        self.bind("<KeyPress-space>", self._on_space_press)
        self.bind("<KeyRelease-space>", self._on_space_release)

    def _on_space_press(self, event):
        if self._space_held:  # Halten sendet wiederholt "press" -> ignorieren
            return
        self._space_held = True
        if self.state == "IDLE":
            self.timer.set_color(COLOR_PRESSED)
            self.state = "READY"
        elif self.state == "RUNNING":
            self._stop_timer()

    def _on_space_release(self, event):
        self._space_held = False
        if self.state == "READY":
            self.timer.set_color(COLOR_RELEASED)
            self.scramble.set_scramble(self.scrambler.generate())
            self.start_time = time.time()
            self.state = "RUNNING"
            self._update_timer()

    def _stop_timer(self):
        # Zuerst den geplanten Update-Aufruf abbrechen, dann Endzeit zeigen
        if self._after_id is not None:
            self.after_cancel(self._after_id)
            self._after_id = None
        final_time = time.time() - self.start_time
        self.timer.set_time(final_time)
        self.timer.set_color(COLOR_IDLE)
        self.state = "IDLE"
        self.db.save_time(final_time)
        self._refresh_history()

    def _refresh_history(self):
        self.sidebar.set_times(self.db.get_last_5())
        self.sidebar.set_ao5(self.db.get_ao5())

    def _update_timer(self):
        if self.state != "RUNNING":
            return
        self.timer.set_time(time.time() - self.start_time)
        self._after_id = self.after(10, self._update_timer)


if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    App().mainloop()
