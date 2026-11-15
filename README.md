# Cube Solver inclusive Time tracking

Timer für Zauberwürfel mit Mischalgorithmus, Zeiten-Speicher und Lösungsanleitungen.

**Ausprobieren:** https://thebrina91.github.io/Cube-Solver-inclusive-Time-tracking/

## Über das Projekt
Alle Zauberwürfel, die in diesem Projekt vorkommen, besitze ich selbst.
Ich wollte mir meinen eigenen Solver mit Timer bauen, um meine Schnelligkeit zu trainieren und neue Würfel lösen zu lernen.

## Was drin ist
- `main.py`: Desktop-App (Python, CustomTkinter, SQLite). Zeiten landen in `times.db`.
- `index.html`: Web-App. Läuft im Browser, ohne Installation.
  - Timer für 2x2, 3x3, 3x3 Mirror, 4x4, Pyraminx, Skewb, Megaminx, Gear 3x3, Gear Zylinder, Gear Ball, Gear Pyraminx
  - Mischalgorithmus je Würfel
  - Letzte 5 Zeiten, Beste 10, Ao5, bestes Ao5, Reset mit Auswahl
  - Algorithmen (Anfänger, CFOP, Roux, 4x4-Parität, Gear-Würfel) mit 3D-Animation für jeden Würfel
  - 3D-Bild des gewählten Würfels, Gear-Würfel mit Zahnrad-Muster

## Als App aufs Handy (offline)
1. Webseite in Chrome auf dem Android-Handy öffnen.
2. Menü (⋮) → „App installieren" oder „Zum Startbildschirm hinzufügen".
3. Die App startet danach wie eine normale App, auch ohne Internet.

## Desktop-App starten
1. `pip install customtkinter`
2. `python main.py`

## Als .exe bauen (Windows)
1. `pip install pyinstaller`
2. `pyinstaller --onefile --windowed --collect-all customtkinter main.py`
3. Die App liegt danach in `dist/`.

## Mitwirkende
- Sabrina Preuß (@TheBrina91): Idee, fachliche Anforderungen, Umsetzung

## Lizenz
© 2026 Sabrina Preuß. Alle Rechte vorbehalten. Details in der Datei [LICENSE](LICENSE).
