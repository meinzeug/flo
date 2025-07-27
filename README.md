# 🤖 meinzeug/flo – Autonomer KI-Codextest

> Dieses Repository dient als autonomes Testfeld für die **OpenAI Codex**-Instanz in Debug-Modus. Ziel: Vollautomatisierte Fehlerdiagnose, ‑behebung und Systemvervollständigung – **gesteuert allein durch KI**.

---

## 🎯 Ziel

Das Python-Projekt `flo` wurde entwickelt, um die Fähigkeiten des Codex-Agents von OpenAI im **vollautonomen Debugging und Software-Ausbau** zu testen.  
Codex agiert hier als Entwickler*in, Tester*in und Projektmanager*in – mit Zugriff auf Codebasis, Konzepte, Dokumentation und GitHub-APIs.

---

## 🧠 Ablauf: Der Codex-Prompt

Bei jeder Ausführung erhält Codex folgenden festen Prompt:

> **[Codex Debug-Modus aktiviert]**  
> Du bist eine autonome KI-Coding-Instanz im Projekt `meinzeug/flo`.  
> Deine Mission: **Führe `run_flo.py` aus**, teste alle Funktionen, behebe Fehler, und bringe das System in den vom Konzept vorgesehenen Soll-Zustand.  
> Dokumentiere Denkprozesse in `brain.md`. Nutze GitHub-Issues für Updates.

🔁 **Verhalten in jeder Ausführung:**

1. Lese `konzept.md` (Zieldefinition) und `docs.md` (technische Spezifikation).
2. Starte das Hauptprogramm `run_flo.py`.
3. Teste alle Menüfunktionen (CLI/TUI).
4. Bei Fehlern:
   - Fehleranalyse → `brain.md`
   - Fehlerbehebung → gezielte Modulanpassung
5. Wiederhole, bis **alle Tests fehlerfrei** durchlaufen.
6. Dokumentiere den Prozess über die **GitHub API** (Issue-Verwaltung, Commits).

---

## 🗂️ Projektstruktur

meinzeug/flo/
├── run_flo.py # Hauptprogramm (Startpunkt)
├── claude_flow_cli.py # Claude-Flow Steuerung
├── menu.py # CLI/TUI Menüsystem
├── openrouter_client.py # OpenRouter API-Anbindung
├── parser_builder.py # Parser- und Formatierungslogik
├── project_manager.py # Datei- und Projektverwaltung
├── setup_manager.py # Konfiguration & Initialisierung
├── konzept.md # 📘 Projektziel (nur lesen)
├── docs.md # 📘 Technische Dokumentation (nur lesen)
└── brain.md # 🧠 KI-Arbeitsgedächtnis (lesen & schreiben)


---

## 🔐 Umgebungsvariablen

| Variable              | Beschreibung                                         |
|-----------------------|------------------------------------------------------|
| `GITHUB_TOKEN`        | GitHub API Token für Commits & Issues               |
| `OPENROUTER_API_KEY`  | API-Schlüssel für OpenRouter / LLM-Anfragen         |
| `GITHUB_USERNAME`     | (Optional) Benutzername für Authentifizierung       |
| `CLAUDE_FLOW_API_KEY` | (Optional) Zugriff auf Claude-Flow-Komponenten      |
| `ZAPIER_HOOK_URL`     | (Optional) Automatisierung via Zapier               |

---

## 🧾 Regeln für Codex

- Nur gezielte Korrekturen – keine Simplifizierungen oder Löschungen ohne Konzeptgrundlage.
- `brain.md` dient als offenes Logbuch (Gedanken, Diagnosen, Testläufe).
- Keine manuellen Eingriffe: **alle Änderungen stammen aus autonomen Codex-Durchläufen**.

---

## 📝 Beispielhafte Codex-Iteration (gekürzt)

```text
# 🧠 brain.md – Codex Session 4

❌ Fehler beim Parsen in parser_builder.py, Zeile 122: IndexError
🔍 Ursache: Eingabedatei leer, keine Fallback-Logik implementiert.
🔧 Fix: try/except-Block hinzugefügt, leeres Eingabehandling.
✅ Test erfolgreich – Fehler behoben.
📬 GitHub-Issue #12 aktualisiert, Commit gepusht.
