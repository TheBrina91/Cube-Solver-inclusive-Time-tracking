# Speedcube-Timer

Timer für Zauberwürfel mit Mischalgorithmus, Zeiten-Speicher und Lösungsanleitungen.

## Was drin ist
- `main.py`: Desktop-App (Python, CustomTkinter, SQLite). Zeiten landen in `times.db`.
- `index.html`: Web-App. Läuft im Browser, ohne Installation.
  - Timer für 2x2, 3x3, Pyraminx, Skewb, Megaminx, Gear 3x3, Gear Zylinder, Gear Ball, Gear Pyraminx
  - Mischalgorithmus je Würfel
  - Letzte 5 Zeiten, Beste 10, Ao5, bestes Ao5, Reset mit Auswahl
  - Algorithmen (Anfänger, CFOP, Roux) mit 3D-Animation

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
