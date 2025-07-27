#!/usr/bin/env python3
"""
run_flo.py – Abstrakte Orchestrierung von Claude‑Flow v2.0.0 Alpha

Dieses Skript stellt eine theoretische Python‑Schnittstelle zur Verfügung, um die
umfangreichen Funktionen von Claude‑Flow v2.0.0 Alpha über das Kommandozeilenwerkzeug
``npx claude-flow@alpha`` anzusteuern. Es orientiert sich an der offiziellen
Dokumentation und kapselt zentrale Operationen wie Projektinitialisierung,
Hive‑Mind‑Management, Swarm‑Aufgaben, Speicherabfragen, neuronale Tools,
Workflow‑Automatisierung, GitHub‑Integrationen, DAA‑Agentensteuerung und
Sicherheitschecks.

Wichtig: Das Skript setzt voraus, dass ``@anthropic-ai/claude-code`` und
``claude-flow@alpha`` global (oder über npx) installiert und erreichbar sind.
Da diese Komponenten in der aktuellen Umgebung nicht verfügbar sind, dient
dieser Code als konzeptioneller Entwurf. Er kann in einer Umgebung mit
Netzwerkzugang und installiertem Claude‑Flow getestet und angepasst werden.
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path
from typing import List, Optional, Dict


class SetupManager:
    """
    Übernimmt die Einrichtung der Umgebung. Bei fehlenden Abhängigkeiten
    versucht der SetupManager, diese automatisch zu installieren. Dazu
    zählen Node.js, npm sowie die Pakete ``@anthropic-ai/claude-code`` und
    ``claude-flow@alpha``. Falls sudo erforderlich ist, werden die
    entsprechenden Befehle mit sudo ausgeführt. Da dieses Skript in einer
    theoretischen Umgebung ausgeführt wird, dienen die Installationsbefehle
    als Beispiel; in einer realen Umgebung muss der Benutzer ggf. sein
    Passwort eingeben oder alternative Paketmanager (z. B. brew, yum)
    verwenden.
    """

    @staticmethod
    def _command_exists(cmd: str) -> bool:
        return subprocess.call(["which", cmd], stdout=subprocess.PIPE, stderr=subprocess.PIPE) == 0

    @staticmethod
    def _run_command(command: List[str]) -> None:
        print(f"[Setup] Führe aus: {' '.join(command)}")
        try:
            subprocess.run(command, check=True)
        except Exception as e:
            print(f"[Setup] Fehler beim Ausführen von {' '.join(command)}: {e}")

    @classmethod
    def install_node_and_npm(cls) -> None:
        """Versucht, Node.js und npm über apt zu installieren."""
        print("[Setup] Node.js oder npm nicht gefunden. Versuche automatische Installation über apt.")
        # Aktualisiere Paketlisten und installiere Node.js und npm
        cls._run_command(["sudo", "apt-get", "update", "-y"])
        cls._run_command(["sudo", "apt-get", "install", "-y", "nodejs", "npm"])

    @classmethod
    def install_claude_code(cls) -> None:
        """Installiert @anthropic-ai/claude-code global via npm."""
        print("[Setup] Installiere @anthropic-ai/claude-code global …")
        cls._run_command(["sudo", "npm", "install", "-g", "@anthropic-ai/claude-code"])
        # Aktiviere mit gefährlichen Berechtigungen
        cls._run_command(["claude", "--dangerously-skip-permissions"])

    @classmethod
    def install_claude_flow(cls) -> None:
        """Installiert claude-flow@alpha global via npm."""
        print("[Setup] Installiere claude-flow@alpha global …")
        cls._run_command(["sudo", "npm", "install", "-g", "claude-flow@alpha"])

    @classmethod
    def setup_environment(cls) -> None:
        """
        Prüft die Verfügbarkeit von node, npm, claude und claude-flow. Fehlende Komponenten
        werden automatisch installiert. Dieser Prozess benötigt ggf. Root-Rechte.
        """
        # Prüfe Node.js und npm
        if not cls._command_exists("node") or not cls._command_exists("npm"):
            cls.install_node_and_npm()
        else:
            print("[Setup] Node.js und npm sind vorhanden.")

        # Prüfe claude (Teil von @anthropic-ai/claude-code)
        if cls._command_exists("claude"):
            print("[Setup] 'claude' ist vorhanden.")
        else:
            cls.install_claude_code()

        # Prüfe claude-flow
        try:
            subprocess.run(["npx", "claude-flow@alpha", "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print("[Setup] claude-flow@alpha ist bereits installiert.")
        except Exception:
            cls.install_claude_flow()

        # Letzter Check
        if not cls._command_exists("claude"):
            print(
                "[Setup] Warnung: Das Kommando 'claude' ist nach der Installation nicht auffindbar."
                " Bitte stellen Sie sicher, dass @anthropic-ai/claude-code korrekt installiert ist."
            )
        try:
            subprocess.run(["npx", "claude-flow@alpha", "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except Exception:
            print(
                "[Setup] Warnung: 'claude-flow@alpha' konnte trotz Installation nicht gefunden werden."
                " Prüfen Sie die Installation und Ihre PATH-Variable."
            )

        # Lade Umgebungsvariablen aus .env und setze Standardmodell
        cls.load_env_tokens()

    @classmethod
    def load_env_tokens(cls) -> None:
        """Lädt GitHub- und OpenRouter-Tokens aus einer .env-Datei oder aus vorhandenen Umgebungsvariablen.
        Zusätzlich wird ein Standard‑Modell für OpenRouter gesetzt.
        """
        env_path = Path(".env")
        if env_path.exists():
            print("[Setup] Lese .env‑Datei ein …")
            with env_path.open() as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    if "=" in line:
                        key, value = line.split("=", 1)
                        key = key.strip()
                        value = value.strip()
                        # Setze nur, wenn noch nicht in os.environ
                        if key and value and key not in os.environ:
                            os.environ[key] = value
                            print(f"[Setup] Setze Umgebungsvariable {key} aus .env")
        # Prüfe GitHub Token
        if "GIT_TOKEN" not in os.environ:
            print("[Setup] Warnung: GitHub‑Token nicht gesetzt. Bitte setzen Sie GIT_TOKEN in Ihrer .env oder als Umgebungsvariable.")
        # Prüfe OpenRouter Token
        if "OPENROUTER_TOKEN" not in os.environ:
            print("[Setup] Warnung: OpenRouter‑Token nicht gesetzt. Bitte setzen Sie OPENROUTER_TOKEN in Ihrer .env oder als Umgebungsvariable.")
        # Setze Standard‑Modell für OpenRouter, falls nicht vorhanden
        if "OPENROUTER_MODEL" not in os.environ:
            os.environ["OPENROUTER_MODEL"] = "qwen/qwen3-coder:free"
            print("[Setup] Setze OPENROUTER_MODEL=qwen/qwen3-coder:free")


class OpenRouterClient:
    """
    Einfacher HTTP‑Client für OpenRouter. Nutzt das API‑Token aus der
    Umgebung und erlaubt, über das Chat‑Completion‑Endpunkt Konzepte
    zu generieren. Dieses Modul ist optional und wird nur verwendet,
    wenn OPENROUTER_TOKEN gesetzt ist. Im Fehlerfall werden Ausnahmen
    gefangen und als Fehlermeldungen ausgegeben.
    """

    API_URL = "https://openrouter.ai/api/v1/chat/completions"

    def __init__(self, api_key: str, model: str) -> None:
        self.api_key = api_key
        self.model = model

    def generate_document(self, idea: str, doc_type: str = "concept") -> str:
        """
        Generiert verschiedene Arten von Dokumenten für die Softwareentwicklung:

        * ``concept`` – Ein umfassendes Konzept mit Anforderungen, Benutzerrollen,
          Funktionsumfang, Tech‑Stack und Projektplan.
        * ``requirements`` – Eine Liste detaillierter Anforderungen, User Stories
          und Akzeptanzkriterien.
        * ``design`` – Ein architektonischer Entwurf mit Komponenten, Datenflüssen
          und Schnittstellen.
        * ``testing`` – Ein Testplan mit Unit‑, Integrations‑, Leistungs‑ und
          Sicherheitstests sowie Testdaten.

        Das Ergebnis wird als Markdown zurückgegeben. Bei Fehlern wird eine
        Exception ausgelöst.
        """
        import requests
        import json

        # System‑Prompts je nach Dokumenttyp
        prompts = {
            "concept": (
                "Du bist eine technische Projektplanungs‑KI. Nimm die folgende "
                "App‑Beschreibung und erstelle ein detailliertes Konzept. Das "
                "Konzept sollte Anforderungen, Benutzerrollen, Funktionsumfang, "
                "empfohlene Programmiersprachen und Bibliotheken, Datenmodelle "
                "und einen groben Projektplan enthalten. Nutze Markdown‑Syntax "
                "und strukturiere das Ergebnis mit Überschriften und Listen."
            ),
            "requirements": (
                "Du bist ein Requirements‑Engineer. Verwandle die folgende App‑Idee "
                "in eine detaillierte Liste von Anforderungen. Formuliere klare User Stories, "
                "Edge Cases, Akzeptanzkriterien und technischen Einschränkungen. Nutze "
                "Markdown mit Überschriften, Listen und Tabellen, wo sinnvoll."
            ),
            "design": (
                "Du bist ein Softwarearchitekt. Erstelle auf Grundlage der folgenden Idee "
                "einen architektonischen Entwurf. Beschreibe die wichtigsten Komponenten, "
                "deren Schnittstellen, Datenflüsse und Speicherstrukturen. Verwende Markdown mit "
                "Diagrammen in ASCII oder PlantUML, wo hilfreich."
            ),
            "testing": (
                "Du bist ein QA‑Ingenieur. Erstelle einen Testplan für die folgende App. "
                "Liste Unit‑Tests, Integrations‑Tests, Performance‑Tests, Security‑Tests "
                "und Usability‑Tests auf. Gib außerdem Beispiel‑Testdaten und erwartete "
                "Ergebnisse an. Nutze Markdown zur Strukturierung."
            ),
        }
        system_prompt = prompts.get(doc_type, prompts["concept"])
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": idea},
        ]
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://example.com/",
            "X-Title": "FlowProjectPlanner",
        }
        body: Dict[str, object] = {
            "model": self.model,
            "messages": messages,
            "max_tokens": 1024,
            "temperature": 0.3,
        }
        print(f"[OpenRouter] Generiere {doc_type}-Dokument mit Modell {self.model} …")
        try:
            response = requests.post(self.API_URL, headers=headers, data=json.dumps(body), timeout=60)
            response.raise_for_status()
            data = response.json()
            content = data.get("choices", [{}])[0].get("message", {}).get("content")
            if not content:
                raise RuntimeError("Keine Antwort von OpenRouter erhalten.")
            return content.strip()
        except Exception as e:
            raise RuntimeError(f"Fehler beim Abruf des {doc_type}-Dokuments: {e}")

    # Backwards‑Kompatibilität
    def generate_concept(self, idea: str) -> str:
        return self.generate_document(idea, doc_type="concept")


class ProjectManager:
    """
    Verwaltet die Erstellung und Automatisierung von Projekten basierend auf
    einer einfachen Idee. Erstellt lokale Projektverzeichnisse, ruft
    optional OpenRouter auf, um ein Konzept zu generieren, legt dieses
    Konzept als Markdown ab und orchestriert anschließend einen kompletten
    SPARC‑Workflow via Claude‑Flow. Zudem kann der Manager den Verlauf
    überwachen und auf Fehler reagieren (theoretisch).
    """

    def __init__(self, base_dir: Path, cli: 'ClaudeFlowCLI') -> None:
        self.base_dir = base_dir
        self.cli = cli
        # Stelle sicher, dass das Basisverzeichnis existiert
        self.base_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def slugify(name: str) -> str:
        """Konvertiert einen Satz in einen slug‐ähnlichen Verzeichnisnamen."""
        import re
        slug = name.lower()
        slug = re.sub(r"[^a-z0-9-]+", "-", slug)
        slug = re.sub(r"-+", "-", slug).strip("-")
        return slug or "projekt"

    def create_project(self, idea: str, template: Optional[str] = None) -> Path:
        """
        Erstellt ein neues Projektverzeichnis, generiert Dokumente über OpenRouter
        (Konzept, Requirements, Design, Testing) und orchestriert anschließend
        einen vollständigen SPARC- und SDLC-Workflow. Optionale Templates
        bestimmen zusätzliche SPARC-Modi. Bei Abwesenheit eines OpenRouter-Tokens
        werden nur lokale Strukturen angelegt.
        """
        # Optimierte Idee: Versuche, die Eingabe zu verkürzen, um Tokens zu sparen
        optimized_idea = self.optimize_prompt(idea)
        slug = self.slugify(idea)
        project_path = self.base_dir / slug
        if project_path.exists():
            print(f"[ProjectManager] Projektordner {project_path} existiert bereits. Dateien können überschrieben werden.")
        else:
            project_path.mkdir(parents=True, exist_ok=True)
        print(f"[ProjectManager] Lege Projektordner {project_path} an …")

        # Instanziiere OpenRouterClient, wenn Token vorhanden
        client: Optional[OpenRouterClient] = None
        if os.environ.get("OPENROUTER_TOKEN"):
            client = OpenRouterClient(
                os.environ["OPENROUTER_TOKEN"],
                os.environ.get("OPENROUTER_MODEL", "qwen/qwen3-coder:free"),
            )
        else:
            print("[ProjectManager] Kein OpenRouter‑Token gefunden – Konzepte können nicht automatisch generiert werden.")

        # Konzept und weitere Dokumente generieren
        if client:
            try:
                concept_text = client.generate_document(optimized_idea, "concept")
                concept_file = project_path / "concept.md"
                concept_file.write_text(concept_text, encoding="utf-8")
                print(f"[ProjectManager] Konzept in {concept_file} gespeichert.")
                # Requirements
                req_doc = client.generate_document(optimized_idea, "requirements")
                req_file = project_path / "requirements.md"
                req_file.write_text(req_doc, encoding="utf-8")
                print(f"[ProjectManager] Requirements in {req_file} gespeichert.")
                # Design
                design_doc = client.generate_document(optimized_idea, "design")
                design_file = project_path / "design.md"
                design_file.write_text(design_doc, encoding="utf-8")
                print(f"[ProjectManager] Design in {design_file} gespeichert.")
                # Testing
                test_doc = client.generate_document(optimized_idea, "testing")
                test_file = project_path / "testing.md"
                test_file.write_text(test_doc, encoding="utf-8")
                print(f"[ProjectManager] Testplan in {test_file} gespeichert.")
            except Exception as e:
                print(f"[ProjectManager] OpenRouter‑Dokumente konnten nicht generiert werden: {e}")

        # Erstelle zusätzliche Verzeichnisstruktur je nach Template
        self._create_additional_dirs(project_path, template)

        # Generiere Beispiel‑Quellcode für bestimmte Templates
        self._generate_skeleton_code(project_path, template)

        # Initialisiere neues Claude‑Flow‑Projekt nur, wenn noch kein .hive-mind Verzeichnis existiert
        if not (project_path / ".hive-mind").exists():
            self.cli.init(project_name=slug, hive_mind=True, neural_enhanced=True)
        else:
            print(f"[ProjectManager] Hive‑Mind bereits initialisiert in {project_path} – init wird übersprungen.")

        # Starte SPARC‑Workflow (vereinfacht) und SDLC
        feature_desc = idea
        print(f"[ProjectManager] Starte SPARC‑Workflow für '{feature_desc}' …")
        self.cli.sparc_full_workflow(feature_desc)
        self.run_sdlc_workflow(feature_desc)

        # Zusätzliche Schritte je nach Template
        if template:
            tmpl = template.lower()
            print(f"[ProjectManager] Wende Template '{tmpl}' an …")
            if tmpl == "agile":
                self.cli.sparc_run("agile", f"plan and implement {feature_desc}", parallel=True, batch_optimize=True)
            elif tmpl == "ddd":
                self.cli.sparc_run("ddd", f"model domain for {feature_desc}", parallel=True)
                self.cli.sparc_run("architecture", f"refine architecture for {feature_desc}", parallel=True)
            elif tmpl == "highperformance":
                self.cli.sparc_run("performance", f"optimize performance for {feature_desc}", parallel=True)
                self.cli.sparc_run("testing", f"load test {feature_desc}", parallel=True)
            elif tmpl == "cicd":
                self.cli.sparc_run("ci-cd", f"build, test, and deploy {feature_desc}", parallel=True)
                print("[ProjectManager] Starte CI/CD‑Workflow: Erzeuge Release und verwalte Pull‑Requests …")
                version_tag = "0.1.0"
                self.cli.github_release_coord(version_tag, auto_changelog=True)
                self.cli.github_pr_manage(reviewers=None, ai_powered=True)
            elif tmpl == "webapp":
                # WebApp: API‑Design und Frontend/Backend Separation
                self.cli.sparc_run("api-design", f"design REST API for {feature_desc}", parallel=True)
                self.cli.sparc_run("frontend", f"create frontend for {feature_desc}", parallel=True)
                self.cli.sparc_run("backend", f"create backend for {feature_desc}", parallel=True)
            elif tmpl == "cli-tool":
                self.cli.sparc_run("cli-tool", f"implement CLI tool for {feature_desc}", parallel=True)
            elif tmpl == "datapipeline":
                self.cli.sparc_run("data-pipeline", f"build data pipeline for {feature_desc}", parallel=True)
            elif tmpl == "microservices":
                self.cli.sparc_run("microservices-split", f"split {feature_desc} into microservices", parallel=True)
            else:
                print(f"[ProjectManager] Unbekanntes Template '{template}'. Es werden keine zusätzlichen Schritte ausgeführt.")

        # Überwachung und Selbstheilung (theoretisch)
        try:
            dummy_session_id = "session-placeholder"
            self.monitor_and_self_heal(dummy_session_id)
        except Exception as e:
            print(f"[ProjectManager] Fehler bei der Überwachung des Projekts: {e}")
        return project_path

    def _create_additional_dirs(self, project_path: Path, template: Optional[str]) -> None:
        """
        Erstellt Beispielverzeichnisse für verschiedene Templates. Dadurch erhalten
        Projekte eine klare Struktur (z. B. src/, tests/) und erleichtern den
        Einstieg für Entwickler. Diese Methode ist rein lokal und hat keine
        Auswirkungen auf Claude‑Flow.
        """
        (project_path / "src").mkdir(exist_ok=True)
        (project_path / "tests").mkdir(exist_ok=True)
        if template:
            tmpl = template.lower()
            if tmpl == "webapp":
                (project_path / "src" / "frontend").mkdir(parents=True, exist_ok=True)
                (project_path / "src" / "backend").mkdir(parents=True, exist_ok=True)
            elif tmpl == "cli-tool":
                # CLI‑Tools: src main file placeholder
                (project_path / "src" / "cli_tool").mkdir(parents=True, exist_ok=True)
            elif tmpl == "datapipeline":
                (project_path / "src" / "pipeline").mkdir(parents=True, exist_ok=True)
            elif tmpl == "microservices":
                (project_path / "src" / "services").mkdir(parents=True, exist_ok=True)

    def _generate_skeleton_code(self, project_path: Path, template: Optional[str]) -> None:
        """
        Legt einfache Beispiel‑Dateien in den neu erstellten Verzeichnissen an, um
        den Start zu erleichtern. Je nach Template werden unterschiedliche
        Grundgerüste generiert (z. B. ein Flask‑Backend für WebApps oder ein
        argparse‑CLI). Die Dateien enthalten nur Minimalgerüste und sollen von
        Claude‑Flow später erweitert werden.
        """
        try:
            if not template:
                return
            tmpl = template.lower()
            # WebApp: Backend (Flask) und Frontend (HTML)
            if tmpl == "webapp":
                backend_dir = project_path / "src" / "backend"
                backend_dir.mkdir(parents=True, exist_ok=True)
                app_file = backend_dir / "app.py"
                if not app_file.exists():
                    app_file.write_text(
                        """from flask import Flask, jsonify\n\napp = Flask(__name__)\n\n@app.route('/')\ndef index():\n    return jsonify({'message': 'Hello from backend!'})\n\nif __name__ == '__main__':\n    app.run(debug=True)\n""",
                        encoding="utf-8",
                    )
                frontend_dir = project_path / "src" / "frontend"
                frontend_dir.mkdir(parents=True, exist_ok=True)
                index_html = frontend_dir / "index.html"
                if not index_html.exists():
                    index_html.write_text(
                        """<!DOCTYPE html>\n<html lang='en'>\n<head><meta charset='UTF-8'><title>WebApp</title></head>\n<body>\n<h1>Willkommen bei Ihrer neuen WebApp</h1>\n<div id='app'></div>\n<script>// Hier könnte Ihr Frontend-Code stehen</script>\n</body>\n</html>""",
                        encoding="utf-8",
                    )
            # CLI‑Tool: Einfacher argparse‑Stub
            elif tmpl == "cli-tool":
                cli_dir = project_path / "src" / "cli_tool"
                cli_dir.mkdir(parents=True, exist_ok=True)
                main_py = cli_dir / "main.py"
                if not main_py.exists():
                    main_py.write_text(
                        """#!/usr/bin/env python3\nimport argparse\n\ndef main():\n    parser = argparse.ArgumentParser(description='CLI Tool')\n    parser.add_argument('--name', help='Ihr Name')\n    args = parser.parse_args()\n    if args.name:\n        print(f'Hallo {args.name}!')\n    else:\n        print('Hallo Welt!')\n\nif __name__ == '__main__':\n    main()\n""",
                        encoding="utf-8",
                    )
            # DataPipeline: Pipeline‑Stub
            elif tmpl == "datapipeline":
                pipeline_dir = project_path / "src" / "pipeline"
                pipeline_dir.mkdir(parents=True, exist_ok=True)
                pipeline_main = pipeline_dir / "main.py"
                if not pipeline_main.exists():
                    pipeline_main.write_text(
                        """#!/usr/bin/env python3\n\ndef extract():\n    # Daten extrahieren\n    return []\n\ndef transform(data):\n    # Daten transformieren\n    return data\n\ndef load(data):\n    # Daten laden\n    pass\n\ndef main():\n    data = extract()\n    transformed = transform(data)\n    load(transformed)\n\nif __name__ == '__main__':\n    main()\n""",
                        encoding="utf-8",
                    )
            # Microservices: Platzhalter‑Service
            elif tmpl == "microservices":
                services_dir = project_path / "src" / "services"
                services_dir.mkdir(parents=True, exist_ok=True)
                service1 = services_dir / "service1.py"
                if not service1.exists():
                    service1.write_text(
                        """#!/usr/bin/env python3\n\n# Dies ist ein Platzhalter für Ihren ersten Microservice.\n# Verwenden Sie Flask, FastAPI oder ein anderes Framework zur Implementierung.\n\n""",
                        encoding="utf-8",
                    )
        except Exception as e:
            print(f"[ProjectManager] Fehler beim Generieren des Skelettcodes: {e}")

    def optimize_prompt(self, idea: str) -> str:
        """
        Vereinfacht die Projektbeschreibung, um die Zahl der Tokens zu reduzieren.
        Nutzt einfache Heuristiken: entfernt Füllwörter und stellt eine
        Aufforderung zur kurzen Zusammenfassung in fünf Stichpunkten. Diese
        optimierte Beschreibung wird an OpenRouter gesendet, wenn verfügbar.
        """
        # Hier könnten komplexere Algorithmen stehen; aktuell nur heuristische Kürzung
        short = idea.strip()
        # Entferne deutsche Füllwörter (beispielhaft)
        for filler in ["einfach", "bitte", "erstelle", "baue", "erstellt", "erstellt", "erstellen"]:
            short = short.replace(filler, "")
        short = short.strip()
        # Formuliere neue Anweisung
        return f"Beschreibe diese Idee in 5 Stichpunkten: {short}"

    def monitor_and_self_heal(self, session_id: str) -> None:
        """
        Überwacht den Verlauf einer Hive‑Mind‑Sitzung und startet bei Fehlern
        automatische Korrekturaufgaben. Diese Implementierung ist theoretisch,
        da in dieser Umgebung kein Zugriff auf laufende Sitzungen besteht.
        """
        print(f"[ProjectManager] Überwache Session {session_id} auf Fehler … (theoretisch)")
        # Beispiel: Fehler erkennen, indem wir im Speicher nach dem Begriff 'error' suchen
        self.cli.memory_query("error", limit=3)
        # Annahme: Wenn Fehler gefunden werden, starte korrigierende Swarm‑Aufgabe
        # self.cli.swarm("Fix detected errors", continue_session=True)
        print("[ProjectManager] Selbstheilung abgeschlossen (theoretisch).")

    def run_sdlc_workflow(self, feature_desc: str) -> None:
        """
        Führt einen theoretischen SDLC‑Workflow aus, der die Phasen Anforderungen,
        Design, Implementierung, Test und Deployment abbildet. Jede Phase
        löst entsprechende SPARC‑Runs oder CLI‑Befehle aus, um die Queen und
        ihre Agenten zu koordinieren. Diese Implementierung dient als Vorlage
        und basiert auf den gängigen SDLC‑Phasen【456026676161703†L164-L326】.
        """
        # Requirements‑Phase: Verwende das generierte Requirements‑Dokument als Kontext
        print("[SDLC] Starte Requirements‑Analyse …")
        self.cli.sparc_run("spec-pseudocode", f"Analyse requirements for {feature_desc}", parallel=True)
        self.auto_correct()
        # Design‑Phase: Erstelle Architektur und Komponenten
        print("[SDLC] Starte Designphase …")
        self.cli.sparc_run("architect", f"Design architecture for {feature_desc}", parallel=True)
        self.auto_correct()
        # Development‑Phase: Implementiere das Feature (TDD)
        print("[SDLC] Starte Implementierungsphase …")
        self.cli.sparc_tdd(f"implement {feature_desc}", batch_tdd=True)
        self.auto_correct()
        # Testing‑Phase: Führe zusätzliche Tests durch
        print("[SDLC] Starte Testphase …")
        self.cli.sparc_run("testing", f"Run tests for {feature_desc}", parallel=True)
        self.auto_correct()
        # Deployment‑Phase: Automatisiere Deployment/Release
        print("[SDLC] Starte Deploymentphase …")
        # Release mit Versionsnummer 0.1.0 (kann angepasst werden)
        self.cli.github_release_coord("0.1.0", auto_changelog=True)
        # Optional: Trigger CI/CD Workflow
        self.cli.sparc_run("ci-cd", f"deploy {feature_desc}", parallel=True)
        self.auto_correct()

    def infer_template(self, idea: str) -> Optional[str]:
        """
        Versucht, aus der Projektidee ein passendes Template abzuleiten. Wenn das
        Wort 'web' vorkommt, wird 'WebApp' vorgeschlagen; bei 'cli' oder
        'konsole' das 'CLI‑Tool', bei 'data' oder 'pipeline' 'DataPipeline',
        bei 'microservice' 'Microservices'. Ansonsten wird None zurückgegeben.
        """
        text = idea.lower()
        if any(x in text for x in ["web", "frontend", "backend"]):
            return "WebApp"
        if any(x in text for x in ["cli", "konsole", "terminal"]):
            return "CLI-Tool"
        if any(x in text for x in ["data", "pipeline"]):
            return "DataPipeline"
        if "microservice" in text or "microservices" in text:
            return "Microservices"
        return None

    def auto_correct(self) -> None:
        """
        Automatischer Korrekturmechanismus: Sucht nach Fehlern im Speicher und
        startet bei Bedarf eine Swarm‑Aufgabe zur Fehlerbehebung. Verwendet
        --continue-session, sodass der aktuelle Kontext erhalten bleibt.
        """
        try:
            result = self.cli._run_capture(["memory", "query", "error", "--limit", "1"])
            if result and "error" in result.lower():
                print("[AutoCorrect] Fehler im Speicher gefunden – starte Fix‑Swarm …")
                self.cli.swarm("Fix detected errors", continue_session=True)
        except Exception as e:
            print(f"[AutoCorrect] Fehler bei der automatischen Korrektur: {e}")


class ProjectManagerMenu:
    """
    Ein einfaches interaktives Menü zur Steuerung des Project Managers. Dies
    erleichtert die Bedienung für Anwender, die nicht alle CLI‑Befehle
    auswendig kennen. Das Menü erlaubt das Erstellen neuer Projekte, das
    Auflisten vorhandener Projekte und die Überwachung von Sessions.
    """

    def __init__(self, pm: ProjectManager) -> None:
        self.pm = pm
        # Speichert benutzerdefinierte Schnellbefehle. Schlüssel = Name, Wert = Liste von Argumenten für Claude‑Flow.
        self.quick_commands: Dict[str, List[str]] = {}

    def list_projects(self) -> None:
        print("\nVerfügbare Projekte:")
        for p in sorted(self.pm.base_dir.glob("*")):
            if p.is_dir():
                print(f"- {p.name}")
        print()

    def manage_quick_commands(self) -> None:
        """
        Verwaltet Schnellbefehle und zeigt die Befehls‑Historie an. Der Benutzer kann
        neue Quick Commands anlegen, vorhandene ausführen, löschen oder die
        History ansehen bzw. löschen.
        """
        while True:
            print("\n[Schnellbefehle & Historie] Optionen:")
            print("1. Historie anzeigen")
            print("2. Historie löschen")
            print("3. Quick Command hinzufügen")
            print("4. Quick Command ausführen")
            print("5. Quick Commands auflisten")
            print("6. Quick Command löschen")
            print("7. Zurück zum Hauptmenü")
            sel = input("Ihre Wahl (1-7): ").strip()
            if sel == "1":
                self.pm.cli.history_show()
            elif sel == "2":
                self.pm.cli.history_clear()
            elif sel == "3":
                name = input("Name des Quick Commands: ").strip()
                cmd = input("Geben Sie die Claude‑Flow‑Argumente ein (z. B. hive-mind status): ").strip()
                if name and cmd:
                    self.quick_commands[name] = cmd.split()
                    print(f"[Quick] Befehl '{name}' wurde gespeichert.")
            elif sel == "4":
                if not self.quick_commands:
                    print("[Quick] Keine Quick Commands verfügbar.")
                    continue
                print("Verfügbare Quick Commands:")
                for idx, qname in enumerate(self.quick_commands.keys(), start=1):
                    print(f"{idx}. {qname}")
                q_sel = input("Wählen Sie den Namen oder die Nummer eines Quick Commands: ").strip()
                # Erlaubt Auswahl per Index
                cmd_key = None
                if q_sel.isdigit():
                    qi = int(q_sel) - 1
                    if 0 <= qi < len(self.quick_commands):
                        cmd_key = list(self.quick_commands.keys())[qi]
                else:
                    cmd_key = q_sel
                if cmd_key and cmd_key in self.quick_commands:
                    args = self.quick_commands[cmd_key]
                    print(f"[Quick] Führe Quick Command '{cmd_key}' aus …")
                    self.pm.cli._run(args)
                else:
                    print("[Quick] Unbekannter Quick Command.")
            elif sel == "5":
                if not self.quick_commands:
                    print("[Quick] Keine Quick Commands gespeichert.")
                else:
                    print("\n[Quick] Gespeicherte Quick Commands:")
                    for name, args in self.quick_commands.items():
                        print(f"- {name}: {' '.join(args)}")
            elif sel == "6":
                if not self.quick_commands:
                    print("[Quick] Keine Quick Commands vorhanden.")
                else:
                    key = input("Name des zu löschenden Quick Commands: ").strip()
                    if key in self.quick_commands:
                        del self.quick_commands[key]
                        print(f"[Quick] Quick Command '{key}' wurde gelöscht.")
                    else:
                        print("[Quick] Quick Command nicht gefunden.")
            elif sel == "7":
                break
            else:
                print("Ungültige Auswahl.")

    def rollback_recovery_menu(self) -> None:
        """
        Menü zur Durchführung von Rollback- und Wiederherstellungsoperationen.
        """
        while True:
            print("\n[Rollback & Recovery] Optionen:")
            print("1. Init Rollback durchführen")
            print("2. Recovery auf letzten sicheren Zustand")
            print("3. Recovery auf benannten Wiederherstellungspunkt")
            print("4. Zurück zum Hauptmenü")
            choice = input("Ihre Wahl (1-4): ").strip()
            if choice == "1":
                self.pm.cli.init_rollback()
            elif choice == "2":
                self.pm.cli.recovery()
            elif choice == "3":
                point = input("Name des Wiederherstellungspunkts: ").strip() or "last-safe-state"
                self.pm.cli.recovery(point)
            elif choice == "4":
                break
            else:
                print("Ungültige Auswahl.")

    def command_palette(self) -> None:
        """
        Eine einfache Befehls‑Palette, die natürliche Spracheingaben in passende
        Claude‑Flow‑Befehle übersetzt. Die Zuordnung erfolgt über heuristische
        Schlüsselwörter. Bei komplexeren Eingaben wird der Benutzer um
        zusätzliche Informationen gebeten.
        """
        print("\n[Befehls‑Palette] Geben Sie eine Aktion in natürlicher Sprache ein (z. B. 'Status anzeigen', 'Swarm starten', 'Memory Stats'): ")
        user_input = input("> ").lower().strip()
        if not user_input:
            return
        # Einfache Schlüsselwort‑Zuordnung
        if "status" in user_input:
            # Zeigt Hive‑Status
            self.pm.cli.hive_status()
        elif "session" in user_input and "list" in user_input:
            self.pm.cli.hive_sessions()
        elif "memory" in user_input and ("stats" in user_input or "statistik" in user_input):
            self.pm.cli.memory_stats()
        elif "init" in user_input:
            proj = input("Projektname (leer lassen für Standard): ").strip() or None
            self.pm.cli.init(project_name=proj)
        elif "spawn" in user_input and "hive" in user_input:
            desc = input("Beschreibung des neuen Hives: ").strip()
            ns = input("Namespace (optional): ").strip() or None
            agents = input("Agenten (Zahl oder kommagetrennt): ").strip() or None
            self.pm.cli.hive_spawn(desc, namespace=ns, agents=agents)
        elif "swarm" in user_input and "start" in user_input:
            desc = input("Aufgabenbeschreibung für den Swarm: ").strip()
            self.pm.cli.swarm(desc)
        elif "performance" in user_input:
            self.pm.cli.performance_report()
        elif "health" in user_input or "gesund" in user_input:
            self.pm.cli.health_auto_heal()
            self.pm.cli.health_check(None)
        else:
            print("[Palette] Kein passender Befehl gefunden. Bitte nutzen Sie das Menü für detaillierte Optionen.")

    def run(self) -> None:
        """
        Startet die interaktive Schleife des Projektmanagers. Zu Beginn kann
        zwischen einem **Einfachen Modus** (nur grundlegende Funktionen) und
        einem **Expertenmodus** (alle Funktionen) gewählt werden. Dadurch wird
        die Bedienoberfläche für Einsteiger übersichtlicher.
        """
        # Modusauswahl
        mode = None
        while mode not in {"1", "2"}:
            print("\n--- Modus auswählen ---")
            print("1. Einfacher Modus (nur Kernfunktionen)")
            print("2. Expertenmodus (alle Funktionen)")
            mode = input("Bitte wählen Sie (1-2): ").strip()
        simple_mode = (mode == "1")
        if simple_mode:
            self.run_simple_menu()
            return
        # Expertenmodus: komplettes Menü
        while True:
            print("\n--- Project Manager Menü ---")
            print("1. Neues Projekt erstellen")
            print("2. Projekte auflisten")
            print("3. Session überwachen & selbst heilen")
            print("4. Monitoring anzeigen")
            print("5. Mit der Queen chatten")
            print("6. Logs anzeigen")
            print("7. Konfiguration (API‑Tokens & Modell)")
            print("8. Wizard für Einsteiger")
            print("9. Selbstheilung & Optimierung")
            print("10. Erweiterte SPARC & Neural‑Features")
            print("11. Metriken & Speicher anzeigen")
            print("12. Sicherheits‑Audit durchführen")
            print("13. Vollständigen Entwicklungs‑Swarm starten")
            print("14. Forschungs- & Analyse‑Swarm starten")
            print("15. Hooks & Variablen korrigieren")
            print("16. Backup & Restore")
            print("17. DAA-Agent erstellen")
            print("18. Hive‑Mind Wizard & Spezial‑Spawn")
            print("19. Agent Lifecycle & Capability‑Match")
            print("20. Neural & Cognitive Tools")
            print("21. Workflow & Automation Tools")
            print("22. Speicher‑Operationen (Compress/Sync/Analytics)")
            print("23. Security & Compliance Tools")
            print("24. Performance & Benchmark Tools")
            print("25. GitHub Tools")
            print("26. System‑Tools")
            print("27. Concurrency‑Richtlinien anzeigen")
            print("28. Swarm‑Orchestrierungswerkzeuge")
            print("29. SPARC Batch & Concurrent Tools")
            print("30. Spezialisierte Swarm‑Muster")
            print("31. Schnellbefehle & Historie")
            print("32. Rollback & Recovery")
            print("33. Befehls‑Palette (Natürliche Sprache)")
            print("34. Beenden")
            choice = input("Bitte wählen Sie eine Option (1-33): ").strip()
            if choice == "1":
                idea = input("Bitte beschreiben Sie das Programm, das Sie entwickeln möchten: ").strip()
                tmpl = input("Optionales Template (Agile, DDD, HighPerformance, CICD, WebApp, CLI-Tool, DataPipeline, Microservices) oder leer: ").strip() or None
                self.pm.create_project(idea, template=tmpl)
            elif choice == "2":
                self.list_projects()
            elif choice == "3":
                session_id = input("Bitte geben Sie die Session‑ID ein, die überwacht werden soll: ").strip()
                self.pm.monitor_and_self_heal(session_id)
            elif choice == "4":
                monitor = MonitoringDashboard(self.pm.cli)
                monitor.show()
            elif choice == "5":
                session_id = input("Bitte geben Sie die Session‑ID für den Chat ein: ").strip()
                chat = QueenChat(self.pm.cli)
                chat.start_chat(session_id)
            elif choice == "6":
                self.show_logs()
            elif choice == "7":
                self.configure_tokens()
            elif choice == "8":
                self.start_wizard()
            elif choice == "9":
                # Selbstheilung & Optimierung
                print("\n[Self-Healing] Starte automatische Heilung und Optimierung …")
                self.pm.cli.health_auto_heal()
                self.pm.cli.fault_tolerance_retry()
                self.pm.cli.bottleneck_auto_optimize()
            elif choice == "10":
                # Erweiterte SPARC- und Neural‑Funktionen
                print("\n[SPARC] Führe Neural‑TDD und vollständigen SPARC‑Workflow mit AI- und Memory‑Optimierungen aus …")
                self.pm.cli.sparc_mode("neural-tdd", auto_learn=True)
                self.pm.cli.sparc_workflow_all(ai_guided=True, memory_enhanced=True)
            elif choice == "11":
                # Metriken & Speicher
                print("\n[Metrics] Sammle Speicher‑ und Leistungsstatistiken …")
                self.pm.cli.metrics_collect_full()
            elif choice == "12":
                # Sicherheits‑Audit
                print("\n[Security] Führe Sicherheitscheck, Audit und Compliance durch …")
                self.pm.cli.security_scan_full()
            elif choice == "13":
                # Vollständiger Entwicklungs‑Swarm
                description = input("Beschreibung des Projekts für den Entwicklungs‑Swarm: ").strip()
                try:
                    agents = int(input("Anzahl der Agenten (Standard 10): ").strip() or "10")
                except Exception:
                    agents = 10
                self.pm.cli.deploy_full_development_swarm(description or "Full development swarm", agents=agents)
            elif choice == "14":
                # Forschungs- & Analyse‑Swarm starten
                description = input("Beschreibung des Forschungsthemas: ").strip() or "Research topic"
                # Standardmäßig zwei Agents: researcher und analyst
                self.pm.cli.hive_spawn(f"Research {description}", namespace=None, agents="researcher,analyst", temp=False)
                print("[Research] Forschungs‑Hive gestartet.")
            elif choice == "15":
                # Hooks & Fix Hook Variables
                print("\n[Hooks] Verfügbare Optionen:\n1. pre-task\n2. pre-search\n3. pre-edit\n4. pre-command\n5. post-edit\n6. post-task\n7. post-command\n8. notification\n9. session-start\n10. session-end\n11. session-restore\n12. Fix Hook Variables")
                sub = input("Bitte wählen Sie: ").strip()
                try:
                    idx = int(sub)
                except Exception:
                    idx = 0
                hook_names = [
                    "pre-task", "pre-search", "pre-edit", "pre-command",
                    "post-edit", "post-task", "post-command", "notification",
                    "session-start", "session-end", "session-restore"
                ]
                if 1 <= idx <= len(hook_names):
                    hook_name = hook_names[idx - 1]
                    params_input = input("Zusätzliche Parameter (leer lassen, wenn keine): ").strip()
                    params = params_input.split() if params_input else []
                    self.pm.cli.hook(hook_name, params)
                elif idx == 12:
                    target_file = input("Dateipfad für fix-hook-variables (leer für automatische Suche): ").strip() or None
                    test_flag = input("Testlauf durchführen? (j/n): ").strip().lower() == "j"
                    self.pm.cli.fix_hook_variables(target=target_file, test=test_flag)
                else:
                    print("Ungültige Auswahl.")
            elif choice == "16":
                # Backup & Restore
                print("\n[Backup/Restore] 1. Backup erstellen  2. Restore durchführen")
                br_choice = input("Ihre Wahl: ").strip()
                if br_choice == "1":
                    outfile = input("Name der Backup-Datei: ").strip() or "backup.json"
                    self.pm.cli.backup_create(outfile)
                elif br_choice == "2":
                    infile = input("Name der Restore-Datei: ").strip() or "backup.json"
                    self.pm.cli.restore_system(infile)
                else:
                    print("Ungültige Auswahl.")
            elif choice == "17":
                # DAA-Agent erstellen
                agent_type = input("Agententyp (z. B. specialized-researcher): ").strip()
                capabilities = input("Fähigkeiten als JSON-Liste (z. B. ['analysis','pattern-recognition']): ").strip() or "[]"
                resources = input("Ressourcen als JSON (z. B. {'memory': 2048,'compute': 'high'}): ").strip() or "{}"
                security_level = input("Sicherheitsstufe (z. B. high) oder leer: ").strip() or None
                sandbox = input("Sandbox aktivieren? (j/n): ").strip().lower() == "j"
                self.pm.cli.daa_agent_create(agent_type, capabilities, resources, security_level if security_level else None, sandbox=sandbox)
            elif choice == "18":
                # Hive-Mind Wizard & spezialisiertes Spawn
                print("\n[Hive-Mind Wizard] Starte interaktiven Claude-Flow Wizard …")
                self.pm.cli._run(["hive-mind", "wizard"])
                # Optional: spezialisiertes Spawn
                if input("Möchten Sie einen weiteren Hive spawnen? (j/n): ").strip().lower() == "j":
                    desc = input("Beschreibung für den Hive: ").strip()
                    ns = input("Namespace (leer lassen für keinen): ").strip() or None
                    agent_input = input("Agenten (Zahl oder kommagetrennte Liste): ").strip() or None
                    agents_param = None
                    if agent_input:
                        agents_param = agent_input
                    self.pm.cli.hive_spawn(desc, namespace=ns, agents=agents_param, temp=False)
            elif choice == "19":
                # Agent Lifecycle & Capability Match sowie weitere DAA‑Funktionen
                print("\n[DAA] Optionen:\n1. Capability Match\n2. Lifecycle Manage\n3. Resource Allocation\n4. Communication\n5. Consensus")
                sub = input("Wählen Sie (1-5): ").strip()
                if sub == "1":
                    req = input("Geben Sie die Task‑Anforderungen als JSON‑Liste ein (z. B. ['security-analysis','performance-optimization']): ").strip() or "[]"
                    self.pm.cli.daa_capability_match(req)
                elif sub == "2":
                    agent_id = input("Agent‑ID: ").strip()
                    action = input("Aktion (z. B. scale-up, scale-down, pause): ").strip()
                    self.pm.cli.daa_lifecycle_manage(agent_id, action)
                elif sub == "3":
                    agent_id = input("Agent‑ID: ").strip()
                    cpu = input("CPU‑Limit (z. B. 50%): ").strip()
                    memory = input("Memory‑Limit (z. B. 2GB): ").strip()
                    self.pm.cli.daa_resource_alloc(agent_id, cpu, memory)
                elif sub == "4":
                    src = input("Quelle (Agent‑ID oder Name): ").strip()
                    tgt = input("Ziel (Agent‑ID oder Name): ").strip()
                    msg = input("Nachricht: ").strip()
                    self.pm.cli.daa_communication(src, tgt, msg)
                elif sub == "5":
                    proposal = input("Consensus‑Vorschlag: ").strip()
                    self.pm.cli.daa_consensus(proposal)
                else:
                    print("Ungültige Auswahl.")
            elif choice == "20":
                # Neural & Cognitive Tools
                print("\n[Neural/Cognitive] Optionen:\n1. Pattern Recognize\n2. Learning Adapt\n3. Compress Model\n4. Ensemble Create\n5. Transfer Learn\n6. Explain Model\n7. Train Model\n8. Predict with Model\n9. Cognitive Analyze")
                sub = input("Wählen Sie (1-9): ").strip()
                if sub == "1":
                    pattern = input("Mustername: ").strip()
                    input_file = input("Eingabedatei (optional): ").strip() or None
                    self.pm.cli.pattern_recognize(pattern, input_file)
                elif sub == "2":
                    model = input("Modellname: ").strip()
                    data_file = input("Datenquelle (optional): ").strip() or None
                    self.pm.cli.learning_adapt(model, data_file)
                elif sub == "3":
                    model = input("Modellname: ").strip()
                    output = input("Ausgabedatei (optional): ").strip() or None
                    self.pm.cli.neural_compress(model, output)
                elif sub == "4":
                    models = input("Modelle (kommagetrennt): ").strip()
                    output_model = input("Name des Ensemble‑Modells: ").strip()
                    self.pm.cli.ensemble_create(models, output_model)
                elif sub == "5":
                    base = input("Basismodell: ").strip()
                    new_data = input("Neue Daten: ").strip()
                    self.pm.cli.transfer_learn(base, new_data)
                elif sub == "6":
                    model = input("Modellname: ").strip()
                    input_file = input("Eingabedatei: ").strip()
                    self.pm.cli.neural_explain(model, input_file)
                elif sub == "7":
                    pattern = input("Trainingsmuster/Name: ").strip()
                    try:
                        epochs = int(input("Anzahl der Epochen (Standard 50): ").strip() or "50")
                    except Exception:
                        epochs = 50
                    data_file = input("Datenquelle (optional): ").strip() or None
                    self.pm.cli.neural_train(pattern, epochs, data_file)
                elif sub == "8":
                    model = input("Modellname: ").strip()
                    input_file = input("Eingabedatei: ").strip()
                    self.pm.cli.neural_predict(model, input_file)
                elif sub == "9":
                    behaviour = input("Verhalten/Beschreibung für die Analyse: ").strip()
                    self.pm.cli.cognitive_analyze(behaviour)
                else:
                    print("Ungültige Auswahl.")
            elif choice == "21":
                # Workflow & Automation Tools
                print("\n[Workflow] Optionen:\n1. Workflow erstellen\n2. Workflow ausführen\n3. Workflow exportieren\n4. Pipeline erstellen\n5. Scheduler verwalten\n6. Trigger einrichten\n7. Batch Process\n8. Parallel Execute")
                sub = input("Wählen Sie (1-8): ").strip()
                if sub == "1":
                    name = input("Workflow‑Name: ").strip()
                    parallel = input("Parallele Ausführung? (j/n): ").strip().lower() == "j"
                    self.pm.cli.workflow_create(name, parallel)
                elif sub == "2":
                    name = input("Workflow‑Name: ").strip()
                    self.pm.cli.workflow_execute(name)
                elif sub == "3":
                    name = input("Workflow‑Name: ").strip()
                    out = input("Ausgabedatei: ").strip() or "workflow.json"
                    self.pm.cli.workflow_export(name, out)
                elif sub == "4":
                    config = input("Konfigurationsdatei: ").strip()
                    self.pm.cli.pipeline_create(config)
                elif sub == "5":
                    schedule = input("Schedulername: ").strip()
                    action = input("Aktion (start, stop, status): ").strip()
                    self.pm.cli.scheduler_manage(schedule, action)
                elif sub == "6":
                    trig_name = input("Triggername: ").strip()
                    target = input("Zielname oder Datei: ").strip()
                    self.pm.cli.trigger_setup(trig_name, target)
                elif sub == "7":
                    items = input("Items (kommagetrennt): ").strip()
                    concurrent = input("Parallel? (j/n): ").strip().lower() == "j"
                    self.pm.cli.batch_process(items, concurrent)
                elif sub == "8":
                    tasks = input("Tasks (kommagetrennt): ").strip()
                    self.pm.cli.parallel_execute(tasks)
                else:
                    print("Ungültige Auswahl.")
            elif choice == "22":
                # Speicher-Operationen
                print("\n[Memory] Optionen:\n1. Compress\n2. Sync\n3. Analytics\n4. Usage\n5. Persist\n6. Namespace wechseln\n7. Search\n8. Export\n9. Import\n10. Store")
                sub = input("Wählen Sie (1-10): ").strip()
                if sub == "1":
                    self.pm.cli.memory_compress()
                elif sub == "2":
                    self.pm.cli.memory_sync()
                elif sub == "3":
                    self.pm.cli.memory_analytics()
                elif sub == "4":
                    self.pm.cli.memory_usage()
                elif sub == "5":
                    self.pm.cli.memory_persist()
                elif sub == "6":
                    ns = input("Neuer Namespace: ").strip()
                    self.pm.cli.memory_namespace(ns)
                elif sub == "7":
                    term = input("Suchbegriff: ").strip()
                    ns = input("Namespace (optional): ").strip() or None
                    self.pm.cli.memory_search(term, ns)
                elif sub == "8":
                    outfile = input("Name der Exportdatei: ").strip() or "memory_export.json"
                    ns = input("Namespace (optional): ").strip() or None
                    self.pm.cli.memory_export(outfile, ns)
                elif sub == "9":
                    infile = input("Datei für Import: ").strip() or "memory_export.json"
                    ns = input("Namespace (optional): ").strip() or None
                    self.pm.cli.memory_import(infile, ns)
                elif sub == "10":
                    key = input("Schlüssel: ").strip()
                    value = input("Wert: ").strip()
                    ns = input("Namespace (optional): ").strip() or None
                    self.pm.cli.memory_store(key, value, ns)
                else:
                    print("Ungültige Auswahl.")
            elif choice == "23":
                # Security & Compliance Tools
                print("\n[Security/Compliance] Optionen:\n1. GitHub Security Analyse\n2. Repo Architect Optimize\n3. Security Audit Hive\n4. Sicherheitsmetriken & Audit")
                sub = input("Wählen Sie (1-4): ").strip()
                if sub == "1":
                    # Analysiert den Code auf Sicherheitsprobleme
                    target = input("Zielverzeichnis für Sicherheitsanalyse (z. B. ./src): ").strip() or "./src"
                    self.pm.cli.github_repo_analyze(analysis_type="security", target=target)
                elif sub == "2":
                    # Optimiert die Repo‑Struktur mit Fokus auf Sicherheit und Compliance
                    security_focus = input("Sicherheitsfokus aktivieren? (j/n): ").strip().lower() == "j"
                    compliance = input("Compliance‑Standard (z. B. SOC2) oder leer: ").strip() or None
                    self.pm.cli.github_repo_architect_optimize(security_focus, compliance)
                elif sub == "3":
                    # Spawn security audit hive
                    self.pm.cli.hive_spawn("security audit and compliance review", namespace=None, agents=None, temp=False)
                elif sub == "4":
                    # Führt Sicherheitsmetriken und Audit aus
                    last = input("Zeitraum für Metriken (z. B. last-24h) oder leer: ").strip() or None
                    self.pm.cli.security_metrics(last)
                    full_trace = input("Vollständigen Audit‑Trace ausgeben? (j/n): ").strip().lower() == "j"
                    self.pm.cli.security_audit(full_trace)
                else:
                    print("Ungültige Auswahl.")
            elif choice == "24":
                # Performance & Benchmark Tools
                print("\n[Performance] Optionen:\n1. Performance Report\n2. Bottleneck Analyze\n3. Token Usage\n4. Benchmark Run\n5. Metrics Collect\n6. Trend Analysis\n7. Usage Stats\n8. Health Check\n9. Diagnostic Run")
                sub = input("Wählen Sie (1-9): ").strip()
                if sub == "1":
                    self.pm.cli.performance_report()
                elif sub == "2":
                    self.pm.cli.bottleneck_analyze()
                elif sub == "3":
                    self.pm.cli.token_usage()
                elif sub == "4":
                    name = input("Benchmark-Name: ").strip()
                    self.pm.cli.benchmark_run(name)
                elif sub == "5":
                    self.pm.cli.metrics_collect()
                elif sub == "6":
                    self.pm.cli.trend_analysis()
                elif sub == "7":
                    self.pm.cli.usage_stats()
                elif sub == "8":
                    components = input("Komponenten (optional, kommagetrennt) oder leer für alle: ").strip() or None
                    self.pm.cli.health_check(components)
                elif sub == "9":
                    self.pm.cli.diagnostic_run()
                else:
                    print("Ungültige Auswahl.")
            elif choice == "25":
                # GitHub Tools
                print("\n[GitHub] Optionen:\n1. Repo Analyze\n2. PR Manage\n3. Issue Track\n4. Release Coord\n5. Workflow Auto\n6. Code Review\n7. Sync Coordinator")
                sub = input("Wählen Sie (1-7): ").strip()
                if sub == "1":
                    analysis = input("Analyseart (z. B. security, performance) oder leer: ").strip() or None
                    target = input("Ziel (Dateipfad oder Repo) oder leer: ").strip() or None
                    self.pm.cli.github_repo_analyze(analysis, target)
                elif sub == "2":
                    reviewers = input("Reviewer (kommagetrennt) oder leer: ").strip() or None
                    ai_pow = input("AI-unterstützt? (j/n): ").strip().lower() == "j"
                    self.pm.cli.github_pr_manage(reviewers, ai_pow)
                elif sub == "3":
                    proj = input("Projektname für Issue-Tracking: ").strip() or None
                    self.pm.cli.github_issue_track(proj)
                elif sub == "4":
                    version = input("Versionsnummer (z. B. 1.0.0): ").strip() or "1.0.0"
                    auto_changelog = input("Auto-Changelog erstellen? (j/n): ").strip().lower() == "j"
                    self.pm.cli.github_release_coord(version, auto_changelog)
                elif sub == "5":
                    file = input("Workflow-Datei: ").strip()
                    self.pm.cli.github_workflow_auto(file)
                elif sub == "6":
                    multi = input("Mehrere Reviewer? (j/n): ").strip().lower() == "j"
                    ai_pow = input("AI-unterstützt? (j/n): ").strip().lower() == "j"
                    self.pm.cli.github_code_review(multi, ai_pow)
                elif sub == "7":
                    multi_pkg = input("Multi-Package sync? (j/n): ").strip().lower() == "j"
                    self.pm.cli.github_sync_coordinator(multi_pkg)
                else:
                    print("Ungültige Auswahl.")
            elif choice == "26":
                # System Tools
                print("\n[System] Optionen:\n1. Config Manage\n2. Features Detect\n3. Log Analysis")
                sub = input("Wählen Sie (1-3): ").strip()
                if sub == "1":
                    operation = input("Operation (read, write, delete): ").strip()
                    file = input("Datei (optional): ").strip() or None
                    self.pm.cli.config_manage(operation, file)
                elif sub == "2":
                    self.pm.cli.features_detect()
                elif sub == "3":
                    log_file = input("Log-Dateipfad: ").strip()
                    self.pm.cli.log_analysis(log_file)
                else:
                    print("Ungültige Auswahl.")
            elif choice == "27":
                # Concurrency guidelines
                self.show_concurrency_guidelines()
            elif choice == "28":
                # Swarm‑Orchestrierungswerkzeuge
                self.swarm_tools_menu()
            elif choice == "29":
                # SPARC Batch & Concurrent Tools
                self.sparc_batch_menu()
            elif choice == "30":
                # Spezialisierte Swarm‑Muster
                self.specialized_patterns_menu()
            elif choice == "31":
                # Schnellbefehle & Historie
                self.manage_quick_commands()
            elif choice == "32":
                # Rollback & Recovery
                self.rollback_recovery_menu()
            elif choice == "33":
                # Befehls-Palette
                self.command_palette()
            elif choice == "34":
                print("Beende Project Manager Menü.")
                break
            else:
                print("Ungültige Auswahl. Bitte erneut versuchen.")

    def show_concurrency_guidelines(self) -> None:
        """
        Gibt Hinweise zur "Goldenen Regel" der Concurrency aus dem Dokument
        ``CLAUDE.md`` aus. In Claude‑Flow sollten alle zusammengehörigen
        Operationen (Schreiben von Todos, Dateioperationen, Speicheraufrufe
        und Bash‑Kommandos) möglichst in einer einzigen Nachricht gebündelt
        werden, um optimale Performance zu erzielen【942476186100460†L0-L17】.
        Diese Methode zeigt dem Benutzer eine kurze Zusammenfassung der
        wichtigsten Regeln und Beispiele, wie Aufgaben in einem Schritt
        kombiniert werden können. Sie dient lediglich der Information
        und führt keine Befehle aus.
        """
        print("\n[Concurrency] Goldene Regel der SPARC‑Entwicklung:")
        print("- Fasse alle zusammengehörigen Operationen in einer einzigen Nachricht zusammen.")
        print("  Dazu zählen TodoWrite‑Aufgaben, File‑Operations, Memory‑Calls und Shell‑Kommandos.")
        print("- Vermeide es, einzelne Schritte über mehrere Nachrichten zu verteilen, da dies die\n  Performance reduziert.")
        print("- Beispiel (korrekt): Erstelle mehrere Dateien und pushe sie in einem einzigen SPARC‑Run.")
        print("- Beispiel (falsch): Sende erst eine Datei, warte auf Antwort, sende dann die nächste.")
        print("Diese Guidelines sind im offiziellen Claude‑Flow‑Handbuch dokumentiert【942476186100460†L0-L17】.\n")

    def configure_tokens(self) -> None:
        """
        Interaktive Konfiguration der API‑Schlüssel. Der Benutzer kann
        GitHub‑Token, OpenRouter‑Token und das OpenRouter‑Modell eingeben. Die Werte
        werden in os.environ gesetzt und in einer .env‑Datei gespeichert.
        """
        print("\n[Konfiguration] Bitte geben Sie die folgenden Werte ein (leer lassen zum Überspringen):")
        git_token = input("GitHub‑Token (GIT_TOKEN): ").strip()
        openrouter_token = input("OpenRouter‑Token (OPENROUTER_TOKEN): ").strip()
        openrouter_model = input(f"OpenRouter‑Modell (OPENROUTER_MODEL) [aktuell {os.environ.get('OPENROUTER_MODEL', 'qwen/qwen3-coder:free')}]: ").strip()
        # Setze Umgebungsvariablen, wenn Werte angegeben wurden
        if git_token:
            os.environ["GIT_TOKEN"] = git_token
        if openrouter_token:
            os.environ["OPENROUTER_TOKEN"] = openrouter_token
        if openrouter_model:
            os.environ["OPENROUTER_MODEL"] = openrouter_model
        # Schreibe in .env
        with open(".env", "w", encoding="utf-8") as f:
            if os.environ.get("GIT_TOKEN"):
                f.write(f"GIT_TOKEN={os.environ['GIT_TOKEN']}\n")
            if os.environ.get("OPENROUTER_TOKEN"):
                f.write(f"OPENROUTER_TOKEN={os.environ['OPENROUTER_TOKEN']}\n")
            if os.environ.get("OPENROUTER_MODEL"):
                f.write(f"OPENROUTER_MODEL={os.environ['OPENROUTER_MODEL']}\n")
        print("[Konfiguration] Tokens und Modell wurden gespeichert.")

    def show_logs(self) -> None:
        """
        Zeigt die letzten Zeilen der wichtigsten Logdatei an. Standardmäßig wird
        flow_autogen.log im aktuellen Arbeitsverzeichnis verwendet, falls vorhanden.
        """
        log_file = Path("flow_autogen.log")
        if not log_file.exists():
            print("[Logs] Keine Logdatei 'flow_autogen.log' gefunden.")
            return
        try:
            with log_file.open("r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()
                tail = lines[-20:] if len(lines) > 20 else lines
                print("\n[Logs] Letzte Zeilen von flow_autogen.log:\n")
                for line in tail:
                    print(line.rstrip())
        except Exception as e:
            print(f"[Logs] Fehler beim Lesen der Logdatei: {e}")

    def start_wizard(self) -> None:
        """
        Geführter Assistent für Einsteiger. Fragt schrittweise die wichtigsten
        Informationen ab (Projektidee, Template, Modellwahl) und startet
        anschließend die Projekterstellung.
        """
        print("\n[Wizard] Willkommen zum Projekt‑Assistenten! Beantworten Sie die folgenden Fragen.")
        idea = input("1) Was soll die Anwendung machen? Beschreiben Sie die Idee in einem Satz: ").strip()
        print("2) Wählen Sie ein Template:")
        templates = ["Agile", "DDD", "HighPerformance", "CICD", "WebApp", "CLI-Tool", "DataPipeline", "Microservices", "Keines"]
        for idx, t in enumerate(templates, 1):
            print(f"  {idx}. {t}")
        tmpl_choice = input("Bitte Auswahl (1-{len(templates)}): ").strip()
        selected_template = None
        try:
            idx = int(tmpl_choice)
            if 1 <= idx <= len(templates) and templates[idx - 1].lower() != "keines":
                selected_template = templates[idx - 1]
        except Exception:
            pass
        model = input(f"3) Welches OpenRouter‑Modell möchten Sie verwenden? [Aktuell {os.environ.get('OPENROUTER_MODEL', 'qwen/qwen3-coder:free')}]: ").strip()
        if model:
            os.environ["OPENROUTER_MODEL"] = model
        self.pm.create_project(idea, template=selected_template)

    def run_simple_menu(self) -> None:
        """
        Führt einen vereinfachten Menümodus aus, der nur die wichtigsten
        Funktionen anbietet: Projekt erstellen, Projektliste, Session
        überwachen & heilen, Logs anzeigen, Konfiguration und Beenden. Dies
        richtet sich an unerfahrene Anwender, die nicht das komplette
        Funktionsspektrum benötigen.
        """
        while True:
            print("\n--- Einfaches Menü ---")
            print("1. Neues Projekt erstellen")
            print("2. Projekte auflisten")
            print("3. Session überwachen & selbst heilen")
            print("4. Logs anzeigen")
            print("5. Konfiguration (API‑Tokens & Modell)")
            print("6. Wizard für Einsteiger")
            print("7. Beenden")
            choice = input("Bitte wählen Sie eine Option (1-7): ").strip()
            if choice == "1":
                idea = input("Bitte beschreiben Sie das Programm, das Sie entwickeln möchten: ").strip()
                tmpl_input = input("Optionales Template (Agile, DDD, HighPerformance, CICD, WebApp, CLI-Tool, DataPipeline, Microservices) oder leer: ").strip() or None
                # Wenn kein Template angegeben wurde, versuche, eines anhand der Idee abzuleiten
                if not tmpl_input:
                    suggestion = self.pm.infer_template(idea)
                    if suggestion:
                        use_sugg = input(f"Soll das vorgeschlagene Template '{suggestion}' verwendet werden? (j/n): ").strip().lower() == "j"
                        if use_sugg:
                            tmpl_input = suggestion
                self.pm.create_project(idea, template=tmpl_input)
            elif choice == "2":
                self.list_projects()
            elif choice == "3":
                session_id = input("Bitte geben Sie die Session‑ID ein, die überwacht werden soll: ").strip()
                self.pm.monitor_and_self_heal(session_id)
            elif choice == "4":
                self.show_logs()
            elif choice == "5":
                self.configure_tokens()
            elif choice == "6":
                self.start_wizard()
            elif choice == "7":
                print("Beende Einfaches Menü.")
                break
            else:
                print("Ungültige Auswahl.")

    # Neue Hilfsmenüs für Swarm‑Orchestrierung, SPARC Batch/Concurrent und spezialisierte Muster

    def swarm_tools_menu(self) -> None:
        """
        Interaktives Menü für fortgeschrittene Swarm‑Orchestrierungsbefehle.
        Hier können Benutzer einen Swarm initialisieren, Agenten spawnen,
        Aufgaben orchestrieren, Monitoring aktivieren, Topologien optimieren
        und Schwärme skalieren oder zerstören.
        """
        while True:
            print("\n[Swarm Tools] Optionen:\n1. Swarm init\n2. Agent spawn\n3. Task orchestrate\n4. Swarm monitor\n5. Topology optimize\n6. Load balance\n7. Coordination sync\n8. Swarm scale\n9. Swarm destroy\n0. Zurück")
            sub = input("Wählen Sie (0-9): ").strip()
            if sub == "1":
                desc = input("Beschreibung für den Swarm (optional): ").strip() or None
                self.pm.cli.swarm_init(desc)
            elif sub == "2":
                agent_type = input("Agententyp: ").strip()
                capabilities = input("Fähigkeiten als JSON-Liste oder Komma‑Liste: ").strip()
                resources = input("Ressourcen als JSON (z. B. {'memory': 1024,'compute':'medium'}): ").strip()
                self.pm.cli.agent_spawn(agent_type, capabilities, resources)
            elif sub == "3":
                task_desc = input("Aufgabenbeschreibung: ").strip()
                self.pm.cli.task_orchestrate(task_desc)
            elif sub == "4":
                dashboard = input("Dashboard anzeigen? (j/n): ").strip().lower() == "j"
                realtime = input("Echtzeit-Monitoring? (j/n): ").strip().lower() == "j"
                self.pm.cli.swarm_monitor(dashboard, realtime)
            elif sub == "5":
                self.pm.cli.topology_optimize()
            elif sub == "6":
                self.pm.cli.load_balance()
            elif sub == "7":
                self.pm.cli.coordination_sync()
            elif sub == "8":
                scale = input("Skalierung (z. B. up, down, 2x): ").strip()
                self.pm.cli.swarm_scale(scale)
            elif sub == "9":
                self.pm.cli.swarm_destroy()
            elif sub == "0":
                break
            else:
                print("Ungültige Auswahl.")

    def sparc_batch_menu(self) -> None:
        """
        Menü für parallele SPARC‑Ausführungen: Batch‑Runs, Pipelines und Concurrent‑Tasks.
        """
        while True:
            print("\n[SPARC Batch/Concurrent] Optionen:\n1. SPARC Batch\n2. SPARC Pipeline\n3. SPARC Concurrent\n0. Zurück")
            sub = input("Wählen Sie (0-3): ").strip()
            if sub == "1":
                modes = input("Modi (kommagetrennt): ").strip()
                task = input("Aufgabe: ").strip()
                self.pm.cli.sparc_batch(modes, task)
            elif sub == "2":
                task = input("Aufgabe für Pipeline: ").strip()
                self.pm.cli.sparc_pipeline(task)
            elif sub == "3":
                mode = input("Modus: ").strip()
                tasks_file = input("Pfad zur Datei mit Aufgaben (z. B. tasks.txt): ").strip()
                self.pm.cli.sparc_concurrent(mode, tasks_file)
            elif sub == "0":
                break
            else:
                print("Ungültige Auswahl.")

    def specialized_patterns_menu(self) -> None:
        """
        Bietet vordefinierte Agentenmuster für die schnelle Erstellung
        spezialisierter Swarms. Benutzer können zwischen Full‑Stack,
        Front‑End, Back‑End, Distributed System oder einem benutzerdefinierten
        Muster wählen. Für benutzerdefinierte Muster können Beschreibung,
        Namespace und Agentenliste frei eingegeben werden.
        """
        patterns = {
            "1": ("full-stack-development", "full-stack swarm", "architect,coder,tester,devops,planner"),
            "2": ("frontend-development", "front-end swarm", "frontend-developer,designer,tester"),
            "3": ("backend-development", "back-end swarm", "backend-developer,db-admin,security"),
            "4": ("distributed-system", "distributed system swarm", "architect,backend-developer,network-engineer,security,devops,tester"),
        }
        print("\n[Spezialisierte Muster] Optionen:\n1. Full‑Stack Development\n2. Front‑End Development\n3. Back‑End Development\n4. Distributed System\n5. Benutzerdefiniertes Muster\n0. Zurück")
        sub = input("Wählen Sie (0-5): ").strip()
        if sub in patterns:
            desc, ns, agents = patterns[sub]
            self.pm.cli.hive_spawn(desc, namespace=ns, agents=agents, temp=False)
        elif sub == "5":
            desc = input("Beschreibung des benutzerdefinierten Swarms: ").strip()
            namespace = input("Namespace (optional): ").strip() or None
            agents = input("Agentenliste (kommagetrennt) oder Zahl: ").strip() or None
            self.pm.cli.hive_spawn(desc, namespace=namespace, agents=agents, temp=False)
        elif sub == "0":
            return
        else:
            print("Ungültige Auswahl.")


class MonitoringDashboard:
    """
    Stellt einen einfachen Monitor zur Verfügung, der den Status der aktuellen
    Hive‑Mind‑Sessions und Swarm‑Aktivitäten abruft und ausgibt. Dabei
    werden die vorhandenen CLI‑Methoden genutzt, um Informationen über
    Sessions, aktive Hives, Swarm‑Topologien und die Queen‑Koordination
    auszugeben. Diese Ausgaben basieren auf den Claude‑Flow‑Befehlen und
    dienen als theoretischer Ansatz zur Visualisierung.
    """

    def __init__(self, cli: 'ClaudeFlowCLI') -> None:
        self.cli = cli

    def show(self) -> None:
        """
        Zeigt eine strukturierte Übersicht über alle Hive‑Sessions, den aktuellen
        Hive‑Status, Swarm‑Überwachung sowie Topologie‑Optimierung und Lastverteilung.
        Anstelle der reinen CLI‑Ausgabe werden die Ergebnisse erfasst und als
        Klartext oder einfache Tabellen ausgegeben. Diese Darstellung ist
        theoretisch, da das Parsing der realen Ausgabe vom Format abhängt.
        """
        print("\n[Monitoring] Aktive Hive‑Mind‑Sessions:")
        sessions_out = self.cli._run_capture(["hive-mind", "sessions"])
        print(sessions_out or "(Keine Sessions oder Ausgabe nicht verfügbar)")
        print("\n[Monitoring] Status des aktuellen Hive:")
        status_out = self.cli._run_capture(["hive-mind", "status"])
        print(status_out or "(Kein Status verfügbar)")
        print("\n[Monitoring] Swarm‑Überwachung (Dashboard & Echtzeit):")
        swarm_out = self.cli._run_capture(["swarm", "monitor", "--dashboard", "--real-time"])
        print(swarm_out or "(Keine Swarm‑Daten verfügbar)")
        print("\n[Monitoring] Topologie & Lastverteilung:")
        topo = self.cli._run_capture(["swarm", "topology-optimize"])
        lb = self.cli._run_capture(["swarm", "load-balance"])
        print(topo)
        print(lb)
        print("\n[Monitoring] Queen‑Aktivitäten werden über den Hive‑Status angezeigt.")


class QueenChat:
    """
    Bietet eine Chat‑Schnittstelle zur Projektleitenden Queen. Der Benutzer
    kann Nachrichten senden, die als Swarm‑Aufgaben in der aktuellen
    Session interpretiert werden. Jede Nachricht wird mit --continue-session
    gesendet, sodass die Queen den Kontext beibehält. Der Chat kann
    genutzt werden, um Fragen zu stellen, Anforderungen zu spezifizieren
    oder neue Milestones zu definieren.
    """

    def __init__(self, cli: 'ClaudeFlowCLI') -> None:
        self.cli = cli

    def start_chat(self, session_id: str) -> None:
        print(f"[Chat] Starte Chat mit Queen für Session {session_id}. Tippen Sie 'exit', um den Chat zu beenden.")
        while True:
            user_input = input("Sie: ").strip()
            if user_input.lower() in {"exit", "quit", "bye"}:
                print("[Chat] Chat beendet.")
                break
            if not user_input:
                continue
            print(f"[Chat] Sende Nachricht an Queen: '{user_input}'")
            self.cli.swarm(user_input, continue_session=True)
            key = f"chat-{session_id}"
            self.cli.memory_store(key, user_input)
            print("[Chat] Nachricht gesendet. Antwort wird in der Claude‑Flow‑Session verarbeitet.")




class ClaudeFlowCLI:
    """Kapselt Aufrufe an ``npx claude-flow@alpha`` für verschiedene Funktionen."""

    def __init__(self, working_dir: Optional[Path] = None) -> None:
        self.working_dir = working_dir or Path.cwd()
        # Halte eine Historie aller ausgeführten Befehle fest. Diese Liste
        # enthält ausschließlich die Argumente nach ``npx claude-flow@alpha``
        # und dient später der Anzeige im Menü. Sie wird nicht persistiert.
        self.command_history: List[str] = []

    def _run(self, args: List[str]) -> None:
        """
        Führt den Befehl ``npx claude-flow@alpha`` mit den angegebenen Argumenten aus.
        Alle aktuellen Umgebungsvariablen (einschließlich geladener API‑Tokens) werden
        an den Subprozess vererbt.
        """
        cmd = ["npx", "claude-flow@alpha"] + args
        print(f"Ausführen: {' '.join(cmd)}")
        # Übergibt die aktuellen Umgebungsvariablen an den Subprozess
        env = os.environ.copy()
        try:
            # Führe den Befehl aus und speichere die Argumentliste in der Historie
            subprocess.run(cmd, cwd=self.working_dir, env=env)
            try:
                # Speichere nur das Argumentsegment (ohne npx) für die Anzeige
                self.command_history.append(' '.join(args))
            except Exception:
                # Wenn das Anhängen fehlschlägt, ignoriere den Fehler
                pass
        except Exception as e:
            print(f"[CLI] Fehler beim Ausführen von {' '.join(cmd)}: {e}")

    def _run_capture(self, args: List[str]) -> str:
        """
        Führt den Befehl ``npx claude-flow@alpha`` aus und gibt stdout als
        Zeichenkette zurück. Diese Methode wird für Monitoring genutzt, um
        Informationen über Sessions, Status oder Swarm zu parsen. Bei einem
        Fehler wird der Fehlertext zurückgegeben.
        """
        cmd = ["npx", "claude-flow@alpha"] + args
        env = os.environ.copy()
        try:
            result = subprocess.run(cmd, cwd=self.working_dir, env=env, capture_output=True, text=True)
            # Füge das Kommando zur Historie hinzu
            try:
                self.command_history.append(' '.join(args))
            except Exception:
                pass
            return result.stdout.strip()
        except Exception as e:
            return f"[CLI] Fehler beim Ausführen von {' '.join(cmd)}: {e}"

    # Setup / Init
    def init(self, project_name: Optional[str] = None, hive_mind: bool = False, neural_enhanced: bool = False) -> None:
        args = ["init", "--force"]
        if project_name:
            args += ["--project-name", project_name]
        if hive_mind:
            args.append("--hive-mind")
        if neural_enhanced:
            args.append("--neural-enhanced")
        self._run(args)

    # Hive‑Mind Operations
    def hive_spawn(self, description: str, namespace: Optional[str] = None, agents: Optional[int] = None, temp: bool = False) -> None:
        args = ["hive-mind", "spawn", description, "--claude"]
        if namespace:
            args += ["--namespace", namespace]
        if agents:
            args += ["--agents", str(agents)]
        if temp:
            args.append("--temp")
        self._run(args)

    def hive_resume(self, session_id: str) -> None:
        args = ["hive-mind", "resume", session_id]
        self._run(args)

    def hive_status(self) -> None:
        args = ["hive-mind", "status"]
        self._run(args)

    def hive_sessions(self) -> None:
        args = ["hive-mind", "sessions"]
        self._run(args)

    # Swarm Operations
    def swarm(self, task: str, continue_session: bool = False, strategy: Optional[str] = None) -> None:
        args = ["swarm", task, "--claude"]
        if continue_session:
            args.append("--continue-session")
        if strategy:
            args += ["--strategy", strategy]
        self._run(args)

    # Memory Operations
    def memory_stats(self) -> None:
        self._run(["memory", "stats"])

    def memory_query(self, term: str, namespace: Optional[str] = None, limit: Optional[int] = None) -> None:
        args = ["memory", "query", term]
        if namespace:
            args += ["--namespace", namespace]
        if limit:
            args += ["--limit", str(limit)]
        self._run(args)

    def memory_store(self, key: str, value: str, namespace: Optional[str] = None) -> None:
        args = ["memory", "store", key, value]
        if namespace:
            args += ["--namespace", namespace]
        self._run(args)

    def memory_export(self, output_file: str, namespace: Optional[str] = None) -> None:
        args = ["memory", "export", output_file]
        if namespace:
            args += ["--namespace", namespace]
        self._run(args)

    def memory_import(self, input_file: str, namespace: Optional[str] = None) -> None:
        args = ["memory", "import", input_file]
        if namespace:
            args += ["--namespace", namespace]
        self._run(args)

    # Neural & Cognitive
    def neural_train(self, pattern: str, epochs: int = 50, data_file: Optional[str] = None) -> None:
        args = ["neural", "train", "--pattern", pattern, "--epochs", str(epochs)]
        if data_file:
            args += ["--data", data_file]
        self._run(args)

    def neural_predict(self, model: str, input_file: str) -> None:
        args = ["neural", "predict", "--model", model, "--input", input_file]
        self._run(args)

    def cognitive_analyze(self, behaviour: str) -> None:
        args = ["cognitive", "analyze", "--behavior", behaviour]
        self._run(args)

    # Workflow Automation
    def workflow_create(self, name: str, parallel: bool = False) -> None:
        args = ["workflow", "create", "--name", name]
        if parallel:
            args.append("--parallel")
        self._run(args)

    def batch_process(self, items: str, concurrent: bool = False) -> None:
        args = ["batch", "process", "--items", items]
        if concurrent:
            args.append("--concurrent")
        self._run(args)

    def pipeline_create(self, config_file: str) -> None:
        args = ["pipeline", "create", "--config", config_file]
        self._run(args)

    # GitHub Integration
    def github_mode(self, mode: str, additional_args: List[str]) -> None:
        args = ["github", mode] + additional_args
        self._run(args)

    # DAA (Dynamic Agent Architecture)
    def daa_agent_create(self, agent_type: str, capabilities: str, resources: str, security_level: Optional[str] = None, sandbox: bool = False) -> None:
        args = ["daa", "agent-create", "--type", agent_type, "--capabilities", capabilities, "--resources", resources]
        if security_level:
            args += ["--security-level", security_level]
        if sandbox:
            args.append("--sandbox")
        self._run(args)

    def daa_capability_match(self, task_requirements: str) -> None:
        args = ["daa", "capability-match", "--task-requirements", task_requirements]
        self._run(args)

    def daa_lifecycle_manage(self, agent_id: str, action: str) -> None:
        args = ["daa", "lifecycle-manage", "--agentId", agent_id, "--action", action]
        self._run(args)

    # Security & System
    def security_scan(self, deep: bool = False, report: bool = False) -> None:
        args = ["security", "scan"]
        if deep:
            args.append("--deep")
        if report:
            args.append("--report")
        self._run(args)

    # ------------------------------------------------------------------
    # Erweiterte Swarm‑Orchestrierung
    # Diese Methoden spiegeln die vielfältigen Swarm‑Werkzeuge wider, die in
    # der Dokumentation als MCP‑Tools aufgeführt sind. Sie erlauben die
    # Initialisierung, Überwachung, Skalierung und Zerstörung von Schwärmen
    # sowie die Optimierung von Topologien und Lastverteilungen.
    def swarm_init(self, description: Optional[str] = None) -> None:
        args = ["swarm", "init"]
        if description:
            args.append(description)
        self._run(args)

    def agent_spawn(self, agent_type: str, capabilities: str, resources: str) -> None:
        args = ["swarm", "agent-spawn", "--type", agent_type, "--capabilities", capabilities, "--resources", resources]
        self._run(args)

    def task_orchestrate(self, task_description: str) -> None:
        args = ["swarm", "task-orchestrate", task_description]
        self._run(args)

    def swarm_monitor(self, dashboard: bool = False, real_time: bool = False) -> None:
        args = ["swarm", "monitor"]
        if dashboard:
            args.append("--dashboard")
        if real_time:
            args.append("--real-time")
        self._run(args)

    def topology_optimize(self) -> None:
        self._run(["swarm", "topology-optimize"])

    def load_balance(self) -> None:
        self._run(["swarm", "load-balance"])

    def coordination_sync(self) -> None:
        self._run(["swarm", "coordination-sync"])

    def swarm_scale(self, scale: str) -> None:
        args = ["swarm", "scale", scale]
        self._run(args)

    def swarm_destroy(self) -> None:
        self._run(["swarm", "destroy"])

    # ------------------------------------------------------------------
    # Erweiterte Neural‑ & Cognitive‑Funktionen
    # Neben Training und Vorhersage stehen weitere Werkzeuge zur Verfügung,
    # etwa Mustererkennung, adaptives Lernen, Kompression und Ensemble‑Methoden.
    def pattern_recognize(self, pattern: str, input_file: Optional[str] = None) -> None:
        args = ["neural", "pattern-recognize", "--pattern", pattern]
        if input_file:
            args += ["--input", input_file]
        self._run(args)

    def learning_adapt(self, model: str, data_file: Optional[str] = None) -> None:
        args = ["neural", "learning-adapt", "--model", model]
        if data_file:
            args += ["--data", data_file]
        self._run(args)

    def neural_compress(self, model: str, output_file: Optional[str] = None) -> None:
        args = ["neural", "compress", "--model", model]
        if output_file:
            args += ["--output", output_file]
        self._run(args)

    def ensemble_create(self, models: str, output_model: str) -> None:
        args = ["neural", "ensemble-create", "--models", models, "--output", output_model]
        self._run(args)

    def transfer_learn(self, base_model: str, new_data: str) -> None:
        args = ["neural", "transfer-learn", "--base", base_model, "--data", new_data]
        self._run(args)

    def neural_explain(self, model: str, input_file: str) -> None:
        args = ["neural", "explain", "--model", model, "--input", input_file]
        self._run(args)

    # ------------------------------------------------------------------
    # Erweiterte Speicherverwaltung
    # Zusätzliche Operationen für Nutzung, Suche, Persistenz und Analysen.
    def memory_usage(self) -> None:
        self._run(["memory", "usage"])

    def memory_search(self, term: str, namespace: Optional[str] = None) -> None:
        args = ["memory", "search", term]
        if namespace:
            args += ["--namespace", namespace]
        self._run(args)

    def memory_persist(self) -> None:
        self._run(["memory", "persist"])

    def memory_namespace(self, namespace: str) -> None:
        args = ["memory", "namespace", namespace]
        self._run(args)

    def memory_backup(self, output_file: str) -> None:
        args = ["memory", "backup", output_file]
        self._run(args)

    def memory_restore(self, input_file: str) -> None:
        args = ["memory", "restore", input_file]
        self._run(args)

    def memory_compress(self) -> None:
        self._run(["memory", "compress"])

    def memory_sync(self) -> None:
        self._run(["memory", "sync"])

    def memory_analytics(self) -> None:
        self._run(["memory", "analytics"])

    # ------------------------------------------------------------------
    # Performance‑ und Monitoring‑Werkzeuge
    # Ermöglicht detaillierte Auswertungen, Benchmarks und Gesundheitschecks.
    def performance_report(self) -> None:
        self._run(["performance", "report"])

    def bottleneck_analyze(self) -> None:
        self._run(["performance", "bottleneck-analyze"])

    def token_usage(self) -> None:
        self._run(["performance", "token-usage"])

    def benchmark_run(self, benchmark_name: str) -> None:
        args = ["performance", "benchmark-run", "--name", benchmark_name]
        self._run(args)

    def metrics_collect(self) -> None:
        self._run(["performance", "metrics-collect"])

    def trend_analysis(self) -> None:
        self._run(["performance", "trend-analysis"])

    def health_check(self, components: Optional[str] = None) -> None:
        args = ["performance", "health-check"]
        if components:
            args += ["--components", components]
        self._run(args)

    def diagnostic_run(self) -> None:
        self._run(["performance", "diagnostic-run"])

    def usage_stats(self) -> None:
        self._run(["performance", "usage-stats"])

    # ------------------------------------------------------------------
    # Erweiterte Workflow‑Automatisierung
    # Neben der Erstellung können Workflows ausgeführt, exportiert und geplant werden.
    def workflow_execute(self, name: str) -> None:
        args = ["workflow", "execute", "--name", name]
        self._run(args)

    def workflow_export(self, name: str, output_file: str) -> None:
        args = ["workflow", "export", "--name", name, "--output", output_file]
        self._run(args)

    def automation_setup(self, config_file: str) -> None:
        args = ["workflow", "automation-setup", "--config", config_file]
        self._run(args)

    def scheduler_manage(self, schedule_name: str, action: str) -> None:
        args = ["workflow", "scheduler-manage", "--schedule", schedule_name, "--action", action]
        self._run(args)

    def trigger_setup(self, trigger_name: str, target: str) -> None:
        args = ["workflow", "trigger-setup", "--name", trigger_name, "--target", target]
        self._run(args)

    def parallel_execute(self, tasks: str) -> None:
        args = ["workflow", "parallel-execute", "--tasks", tasks]
        self._run(args)

    # ------------------------------------------------------------------
    # Spezialisierte GitHub‑Integrationen
    # Einzelne Methoden für häufig verwendete GitHub‑Funktionen.
    def github_repo_analyze(self, analysis_type: Optional[str] = None, target: Optional[str] = None) -> None:
        args = ["github", "repo-analyze"]
        if analysis_type:
            args += ["--analysis-type", analysis_type]
        if target:
            args += ["--target", target]
        self._run(args)

    def github_pr_manage(self, reviewers: Optional[str] = None, ai_powered: bool = False) -> None:
        args = ["github", "pr-manager"]
        if reviewers:
            args += ["--reviewers", reviewers]
        if ai_powered:
            args.append("--ai-powered")
        self._run(args)

    def github_issue_track(self, project: Optional[str] = None) -> None:
        args = ["github", "issue-tracker"]
        if project:
            args += ["--project", project]
        self._run(args)

    def github_release_coord(self, version: str, auto_changelog: bool = False) -> None:
        args = ["github", "release-manager", "--version", version]
        if auto_changelog:
            args.append("--auto-changelog")
        self._run(args)

    def github_workflow_auto(self, file: str) -> None:
        args = ["github", "workflow-auto", "--file", file]
        self._run(args)

    def github_code_review(self, multi_reviewer: bool = False, ai_powered: bool = False) -> None:
        args = ["github", "code-review"]
        if multi_reviewer:
            args.append("--multi-reviewer")
        if ai_powered:
            args.append("--ai-powered")
        self._run(args)

    def github_sync_coordinator(self, multi_package: bool = False) -> None:
        args = ["github", "sync-coordinator"]
        if multi_package:
            args.append("--multi-package")
        self._run(args)

    # Repo Architect Optimize
    def github_repo_architect_optimize(self, security_focused: bool = False, compliance: Optional[str] = None) -> None:
        """
        Optimiert die Struktur eines Repositories. Bei aktivierter Sicherheitsoption
        wird ein security‑focused Refactoring vorgenommen und optional ein
        Compliance‑Standard berücksichtigt.
        """
        args = ["github", "repo-architect", "optimize"]
        if security_focused:
            args.append("--security-focused")
        if compliance:
            args += ["--compliance", compliance]
        self._run(args)

    # ------------------------------------------------------------------
    # Erweiterte Dynamische Agentensteuerung (DAA)
    def daa_resource_alloc(self, agent_id: str, cpu: str, memory: str) -> None:
        args = ["daa", "resource-alloc", "--agentId", agent_id, "--cpu", cpu, "--memory", memory]
        self._run(args)

    def daa_communication(self, source: str, target: str, message: str) -> None:
        args = ["daa", "communication", "--source", source, "--target", target, "--message", message]
        self._run(args)

    def daa_consensus(self, proposal: str) -> None:
        args = ["daa", "consensus", "--proposal", proposal]
        self._run(args)

    # ------------------------------------------------------------------
    # System & Sicherheitsbezogene Befehle
    def backup_create(self, output_file: str) -> None:
        args = ["backup", "create", output_file]
        self._run(args)

    def restore_system(self, backup_file: str) -> None:
        args = ["restore", "system", backup_file]
        self._run(args)

    def config_manage(self, operation: str, file: Optional[str] = None) -> None:
        args = ["config", "manage", operation]
        if file:
            args.append(file)
        self._run(args)

    def features_detect(self) -> None:
        self._run(["config", "features-detect"])

    def log_analysis(self, log_file: str) -> None:
        args = ["log", "analysis", log_file]
        self._run(args)

    # ------------------------------------------------------------------
    # Kommando-Historie und Schnellbefehle
    def history_show(self) -> None:
        """
        Gibt die Liste der bisher mit ``_run`` ausgeführten Befehle aus. Die
        Historie wird nicht persistiert und gilt nur für die laufende Sitzung.
        """
        if not self.command_history:
            print("[History] Keine Befehle wurden bisher ausgeführt.")
            return
        print("\n[History] Ausgeführte Befehle:")
        for idx, cmd in enumerate(self.command_history, start=1):
            print(f"{idx}. {cmd}")

    def history_clear(self) -> None:
        """Löscht die gespeicherte Befehls-Historie."""
        self.command_history.clear()
        print("[History] Historie wurde geleert.")

    # ------------------------------------------------------------------
    # Rollback und Wiederherstellungsfunktionen
    def init_rollback(self) -> None:
        """
        Stellt den Zustand vor dem letzten ``init`` wieder her. Dieser Befehl
        entspricht ``claude-flow init --rollback`` aus der Dokumentation.
        """
        self._run(["init", "--rollback"])

    def recovery(self, point: str = "last-safe-state") -> None:
        """
        Startet eine Wiederherstellung an einem definierten Punkt. Standardmäßig
        wird der letzte sichere Zustand verwendet. Siehe Dokumentation.

        :param point: Name oder Schlüssel des Wiederherstellungspunkts
        """
        args = ["recovery", "--point", point]
        self._run(args)

    # ------------------------------------------------------------------
    # Selbstheilung & Optimierung
    def health_auto_heal(self) -> None:
        """
        Führt einen vollständigen Gesundheitscheck durch und versucht automatische
        Heilung. Dies entspricht dem Dokumentationsbeispiel `health check --components all --auto-heal`
        【528891845064954†L519-L525】.
        """
        args = ["health", "check", "--components", "all", "--auto-heal"]
        self._run(args)

    def fault_tolerance_retry(self) -> None:
        """
        Aktiviert eine Fehlertoleranz mit der Strategie "retry-with-learning", wie
        in der offiziellen README beschrieben【528891845064954†L519-L525】.
        """
        args = ["fault", "tolerance", "--strategy", "retry-with-learning"]
        self._run(args)

    def bottleneck_auto_optimize(self) -> None:
        """
        Analysiert systemische Engpässe und optimiert sie automatisch. Dieser
        Befehl entspricht `bottleneck analyze --auto-optimize` aus der Self‑Healing‑Sektion der
        Dokumentation【528891845064954†L519-L525】.
        """
        args = ["bottleneck", "analyze", "--auto-optimize"]
        self._run(args)

    # ------------------------------------------------------------------
    # Erweiterte SPARC‑Modi und Workflows
    def sparc_mode(self, mode_type: str, auto_learn: bool = False) -> None:
        """
        Führt einen speziellen SPARC‑Modus aus. Mit `auto_learn` wird der Modus
        automatisch trainiert, wie im Beispiel `sparc mode --type "neural-tdd" --auto-learn`【528891845064954†L501-L507】.
        """
        args = ["sparc", "mode", "--type", mode_type]
        if auto_learn:
            args.append("--auto-learn")
        self._run(args)

    def sparc_workflow_all(self, ai_guided: bool = False, memory_enhanced: bool = False) -> None:
        """
        Startet einen vollständigen SPARC‑Workflow über alle Phasen hinweg. Die
        Optionen `ai_guided` und `memory_enhanced` entsprechen dem Beispiel
        `sparc workflow --phases "all" --ai-guided --memory-enhanced`【528891845064954†L501-L507】.
        """
        args = ["sparc", "workflow", "--phases", "all"]
        if ai_guided:
            args.append("--ai-guided")
        if memory_enhanced:
            args.append("--memory-enhanced")
        self._run(args)

    # ------------------------------------------------------------------
    # Erweiterte Speicher- und Performancefunktionen
    def memory_list(self) -> None:
        """Listet alle verfügbaren Speichernamespaces auf."""
        self._run(["memory", "list"])

    def metrics_collect_full(self) -> None:
        """
        Sammelt detaillierte Metriken und erstellt einen Performancebericht. Die
        Methode kombiniert `memory stats`, `memory list`, `performance report` und
        `metrics collect` zu einer einzigen Kennzahlübersicht, um den Nutzer
        schnelle Einblicke zu geben.
        """
        self.memory_stats()
        self.memory_list()
        self.performance_report()
        self.metrics_collect()

    # ------------------------------------------------------------------
    # Sicherheit & Compliance
    def security_scan_full(self) -> None:
        """
        Führt einen umfassenden Sicherheitscheck durch, inklusive tiefem Scan und
        Berichtserstellung, wie in der Dokumentation für Sicherheitsfeatures
        beschrieben【528891845064954†L785-L866】.
        """
        self.security_scan(deep=True, report=True)
        self.security_audit(full_trace=True)

    # ------------------------------------------------------------------
    # Komplette Entwicklungs‑Swarm
    def deploy_full_development_swarm(self, description: str, agents: int = 10) -> None:
        """
        Spawnt einen Hive‑Mind mit einer großen Anzahl spezialisierter Agenten, um
        ein komplettes Projekt zu entwickeln. Dies orientiert sich an den
        fortgeschrittenen Nutzungsbeispielen der README【528891845064954†L571-L583】.
        """
        self.hive_spawn(description, namespace="full-dev", agents=agents, temp=False)

    # ------------------------------------------------------------------
    # Hooks & Konfigurationswerkzeuge
    def hook(self, hook_name: str, params: List[str]) -> None:
        # Allgemeiner Aufruf für hooks. "hook_name" entspricht z. B. pre-task, post-edit usw.
        args = ["hooks", hook_name] + params
        self._run(args)

    def fix_hook_variables(self, target: Optional[str] = None, test: bool = False) -> None:
        args = ["fix-hook-variables"]
        if target:
            args.append(target)
        if test:
            args.append("--test")
        self._run(args)

    # ------------------------------------------------------------------
    # SPARC‑Workflow und Batchtools
    def sparc_modes(self) -> None:
        """Listet alle verfügbaren SPARC‑Entwicklungsmodi auf."""
        self._run(["sparc", "modes"])

    def sparc_run(self, mode: str, task: str, parallel: bool = False, batch_optimize: bool = False) -> None:
        """Führt einen SPARC‑Modus für eine bestimmte Aufgabe aus."""
        args = ["sparc", "run", mode, task]
        if parallel:
            args.append("--parallel")
        if batch_optimize:
            args.append("--batch-optimize")
        self._run(args)

    def sparc_tdd(self, feature: str, batch_tdd: bool = False) -> None:
        """Startet einen vollständigen Test‑Driven‑Development‑Workflow mittels SPARC."""
        args = ["sparc", "tdd", feature]
        if batch_tdd:
            args.append("--batch-tdd")
        self._run(args)

    def sparc_info(self, mode: str) -> None:
        """Zeigt Details zu einem SPARC‑Modus an."""
        self._run(["sparc", "info", mode])

    def sparc_batch(self, modes: str, task: str) -> None:
        """Führt mehrere SPARC‑Modi parallel aus."""
        self._run(["sparc", "batch", modes, task])

    def sparc_pipeline(self, task: str) -> None:
        """Startet eine komplette SPARC‑Pipeline für eine Aufgabe."""
        self._run(["sparc", "pipeline", task])

    def sparc_concurrent(self, mode: str, tasks_file: str) -> None:
        """Verarbeitet mehrere Aufgaben parallel in einem SPARC‑Modus."""
        self._run(["sparc", "concurrent", mode, tasks_file])

    # ------------------------------------------------------------------
    # Hintergrundausführung
    def run_background(self, cli_args: List[str]) -> None:
        """
        Startet einen beliebigen claude‑flow‑Befehl im Hintergrund mittels screen.
        Erzeugt einen eindeutigen Sitzungsnamen und gibt ihn zur späteren
        Überwachung aus. Diese Funktion setzt voraus, dass 'screen' installiert ist.
        """
        # Generiere einen eindeutigen Sitzungsnamen
        import time
        session_name = f"claude_flow_{int(time.time())}"
        command = ["screen", "-dmS", session_name, "npx", "claude-flow@alpha"] + cli_args
        print(f"[Background] Starte Hintergrundprozess in Screen-Session {session_name}: {' '.join(command)}")
        env = os.environ.copy()
        try:
            subprocess.run(command, cwd=self.working_dir, env=env)
        except Exception as e:
            print(f"[Background] Fehler beim Start des Hintergrundprozesses: {e}")

    # ------------------------------------------------------------------
    # Komplettes SPARC‑Workflow‑Skript
    def sparc_full_workflow(self, feature: str) -> None:
        """
        Führt einen vollständigen SPARC‑Entwicklungsworkflow für das angegebene Feature aus.
        Dieser Ablauf kombiniert Spezifikation, Architektur, TDD und Integration.
        """
        # Spezifikation und Pseudocode
        spec_task = f"Define {feature} requirements"
        self.sparc_run("spec-pseudocode", spec_task, parallel=True)
        # Architekturphase
        arch_task = f"Design {feature} architecture"
        self.sparc_run("architect", arch_task, parallel=True)
        # TDD‑Phase
        tdd_task = f"implement {feature}"
        self.sparc_tdd(tdd_task, batch_tdd=True)
        # Integrationsphase
        integration_task = f"integrate {feature}"
        self.sparc_run("integration", integration_task, parallel=True)

    def security_metrics(self, last: Optional[str] = None) -> None:
        args = ["security", "metrics"]
        if last:
            args += ["--last", last]
        self._run(args)

    def security_audit(self, full_trace: bool = False) -> None:
        args = ["security", "audit"]
        if full_trace:
            args.append("--full-trace")
        self._run(args)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Python‑Wrapper für Claude‑Flow v2.0.0 Alpha. Voraussetzung: npx claude-flow@alpha ist installiert."
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # init
    init_p = sub.add_parser("init", help="Initialisiert ein neues Claude‑Flow‑Projekt")
    init_p.add_argument("--project-name", help="Name des Projekts")
    init_p.add_argument("--hive-mind", action="store_true", help="Hive‑Mind initialisieren")
    init_p.add_argument("--neural-enhanced", action="store_true", help="Neural‑Features aktivieren")

    # hive spawn
    spawn_p = sub.add_parser("spawn", help="Erzeugt einen neuen Hive für ein Feature oder Experiment")
    spawn_p.add_argument("description", help="Beschreibung der Mission / Feature")
    spawn_p.add_argument("--namespace", help="Namespace des Hives")
    spawn_p.add_argument("--agents", type=int, help="Anzahl der Agenten im Hive")
    spawn_p.add_argument("--temp", action="store_true", help="Temporären Hive erstellen")

    # hive resume
    resume_p = sub.add_parser("resume", help="Setzt die Arbeit in einem bestehenden Hive fort")
    resume_p.add_argument("session_id", help="Sitzungs‑ID des Hives")

    # hive status, sessions
    sub.add_parser("status", help="Zeigt den Status des aktuellen Hives an")
    sub.add_parser("sessions", help="Listet alle Hives/Sessions auf")

    # swarm
    swarm_p = sub.add_parser("swarm", help="Startet eine Swarm‑Aufgabe für eine Teilaufgabe")
    swarm_p.add_argument("task", help="Beschreibung der Aufgabe")
    swarm_p.add_argument("--continue-session", action="store_true", help="Auf bestehender Sitzung fortsetzen")
    swarm_p.add_argument("--strategy", help="Koordinationsstrategie, z. B. development, research")

    # memory
    sub.add_parser("memory-stats", help="Zeigt Statistiken über den Speicher an")
    query_p = sub.add_parser("memory-query", help="Durchsucht den Speicher nach einem Begriff")
    query_p.add_argument("term", help="Suchbegriff")
    query_p.add_argument("--namespace", help="Namespace einschränken")
    query_p.add_argument("--limit", type=int, help="Anzahl der Ergebnisse begrenzen")

    store_p = sub.add_parser("memory-store", help="Speichert einen Schlüssel/Wert im Speicher")
    store_p.add_argument("key")
    store_p.add_argument("value")
    store_p.add_argument("--namespace")

    export_p = sub.add_parser("memory-export", help="Exportiert den Speicher in eine Datei")
    export_p.add_argument("output_file")
    export_p.add_argument("--namespace")

    import_p = sub.add_parser("memory-import", help="Importiert eine Speicherdatei")
    import_p.add_argument("input_file")
    import_p.add_argument("--namespace")

    # neural
    neural_train_p = sub.add_parser("neural-train", help="Trainiert ein neuronales Muster")
    neural_train_p.add_argument("pattern", help="Name des Musters")
    neural_train_p.add_argument("--epochs", type=int, default=50)
    neural_train_p.add_argument("--data")

    neural_predict_p = sub.add_parser("neural-predict", help="Führt eine Vorhersage durch")
    neural_predict_p.add_argument("model", help="Name des Modells")
    neural_predict_p.add_argument("input_file", help="Eingabedatei")

    cognitive_p = sub.add_parser("cognitive-analyze", help="Analysiert ein Verhalten")
    cognitive_p.add_argument("behavior", help="Verhaltensbeschreibung")

    # workflow
    workflow_p = sub.add_parser("workflow-create", help="Erstellt einen neuen Workflow")
    workflow_p.add_argument("name")
    workflow_p.add_argument("--parallel", action="store_true")

    batch_p = sub.add_parser("batch-process", help="Verarbeitet eine Liste von Items im Batch")
    batch_p.add_argument("items", help="Kommagetrennte Liste von Items")
    batch_p.add_argument("--concurrent", action="store_true")

    pipeline_p = sub.add_parser("pipeline-create", help="Erstellt eine Pipeline aus einer Konfigurationsdatei")
    pipeline_p.add_argument("config_file")

    # github (generischer Aufruf)
    github_p = sub.add_parser("github", help="Ruft einen GitHub‑Modus von Claude‑Flow auf")
    github_p.add_argument("mode", help="Name des GitHub‑Modus (z. B. pr-manager, repo-architect)")
    github_p.add_argument("args", nargs=argparse.REMAINDER, help="Weitere Argumente für den Modus")

    # DAA
    daa_create_p = sub.add_parser("daa-create", help="Erstellt einen Agenten")
    daa_create_p.add_argument("agent_type")
    daa_create_p.add_argument("capabilities", help="JSON‑Liste der Fähigkeiten")
    daa_create_p.add_argument("resources", help="Ressourcenbeschreibung als JSON")
    daa_create_p.add_argument("--security-level")
    daa_create_p.add_argument("--sandbox", action="store_true")

    daa_match_p = sub.add_parser("daa-match", help="Ordnet Fähigkeiten Anforderungen zu")
    daa_match_p.add_argument("task_requirements", help="JSON‑Liste der Anforderungen")

    daa_lifecycle_p = sub.add_parser("daa-lifecycle", help="Verwaltet den Lebenszyklus eines Agenten")
    daa_lifecycle_p.add_argument("agent_id")
    daa_lifecycle_p.add_argument("action", help="Aktion, z. B. scale-up")

    # security
    sec_scan_p = sub.add_parser("security-scan", help="Führt einen Sicherheitscheck durch")
    sec_scan_p.add_argument("--deep", action="store_true")
    sec_scan_p.add_argument("--report", action="store_true")

    sec_metrics_p = sub.add_parser("security-metrics", help="Zeigt Sicherheitsmetriken an")
    sec_metrics_p.add_argument("--last")

    sec_audit_p = sub.add_parser("security-audit", help="Führt ein Sicherheitsaudit durch")
    sec_audit_p.add_argument("--full-trace", action="store_true")

    # ------------------------------------------------------------------
    # Zusätzliche Swarm‑Befehle
    swarm_init_p = sub.add_parser("swarm-init", help="Initialisiert einen neuen Swarm")
    swarm_init_p.add_argument("--description", help="Optionale Beschreibung für den Swarm")
    agent_spawn_p = sub.add_parser("agent-spawn", help="Startet einen Agenten im Swarm")
    agent_spawn_p.add_argument("agent_type", help="Typ des Agenten")
    agent_spawn_p.add_argument("capabilities", help="JSON‑Liste der Fähigkeiten")
    agent_spawn_p.add_argument("resources", help="JSON‑Beschreibung der Ressourcen")
    task_orchestrate_p = sub.add_parser("task-orchestrate", help="Orchestriert eine Aufgabe im Swarm")
    task_orchestrate_p.add_argument("task_description", help="Beschreibung der Aufgabe")
    swarm_monitor_p = sub.add_parser("swarm-monitor", help="Überwacht einen Swarm")
    swarm_monitor_p.add_argument("--dashboard", action="store_true", help="Dashboard anzeigen")
    swarm_monitor_p.add_argument("--real-time", action="store_true", help="Echtzeitüberwachung aktivieren")
    sub.add_parser("topology-optimize", help="Optimiert die Topologie eines Swarms")
    sub.add_parser("load-balance", help="Führt Lastverteilung im Swarm durch")
    sub.add_parser("coordination-sync", help="Synchronisiert die Koordination eines Swarms")
    swarm_scale_p = sub.add_parser("swarm-scale", help="Skaliert die Größe eines Swarms")
    swarm_scale_p.add_argument("scale", help="Skalierungsangabe, z. B. 'up', 'down' oder konkrete Zahl")
    sub.add_parser("swarm-destroy", help="Zerstört den aktuellen Swarm")

    # ------------------------------------------------------------------
    # Zusätzliche Neural & Cognitive Befehle
    pattern_p = sub.add_parser("pattern-recognize", help="Führt eine Mustererkennung durch")
    pattern_p.add_argument("pattern", help="Name oder ID des Musters")
    pattern_p.add_argument("--input-file", help="Optionale Eingabedatei")
    learn_p = sub.add_parser("learning-adapt", help="Passt ein Modell an neue Daten an")
    learn_p.add_argument("model", help="Modellname")
    learn_p.add_argument("--data", help="Datenquelle")
    compress_p = sub.add_parser("neural-compress", help="Komprimiert ein bestehendes Modell")
    compress_p.add_argument("model", help="Modellname")
    compress_p.add_argument("--output", help="Zieldatei für das komprimierte Modell")
    ensemble_p = sub.add_parser("ensemble-create", help="Erstellt ein Ensemble aus mehreren Modellen")
    ensemble_p.add_argument("models", help="Kommagetrennte Liste von Modellen")
    ensemble_p.add_argument("output_model", help="Name des Ergebnis‑Modells")
    transfer_p = sub.add_parser("transfer-learn", help="Führt Transfer Learning durch")
    transfer_p.add_argument("base_model", help="Basismodell")
    transfer_p.add_argument("new_data", help="Neue Daten für das Training")
    explain_p = sub.add_parser("neural-explain", help="Erklärt ein Modell")
    explain_p.add_argument("model", help="Modellname")
    explain_p.add_argument("input_file", help="Eingabedatei")

    # ------------------------------------------------------------------
    # Zusätzliche Speicherbefehle
    sub.add_parser("memory-usage", help="Zeigt die aktuelle Speichernutzung an")
    mem_search_p = sub.add_parser("memory-search", help="Sucht im Speicher nach einem Begriff")
    mem_search_p.add_argument("term", help="Suchbegriff")
    mem_search_p.add_argument("--namespace", help="Optionales Namespace")
    sub.add_parser("memory-persist", help="Persistiert den aktuellen Speicherzustand")
    mem_ns_p = sub.add_parser("memory-namespace", help="Legt ein Namespace fest")
    mem_ns_p.add_argument("namespace", help="Namespace-Name")
    mem_backup_p = sub.add_parser("memory-backup", help="Erstellt ein Speicher‑Backup")
    mem_backup_p.add_argument("output_file", help="Zieldatei für das Backup")
    mem_restore_p = sub.add_parser("memory-restore", help="Stellt Speicher aus einem Backup wieder her")
    mem_restore_p.add_argument("input_file", help="Backupdatei")
    sub.add_parser("memory-compress", help="Komprimiert den Speicher")
    sub.add_parser("memory-sync", help="Synchronisiert Speicher zwischen Instanzen")
    sub.add_parser("memory-analytics", help="Führt Analyse auf dem Speicher durch")

    # ------------------------------------------------------------------
    # Zusätzliche Performance‑Befehle
    sub.add_parser("performance-report", help="Erstellt einen detaillierten Leistungsbericht")
    sub.add_parser("bottleneck-analyze", help="Analysiert systemische Engpässe")
    sub.add_parser("token-usage", help="Zeigt Tokenverbrauch an")
    bench_p2 = sub.add_parser("benchmark-run", help="Führt einen Benchmark aus")
    bench_p2.add_argument("benchmark_name", help="Name des Benchmarks")
    sub.add_parser("metrics-collect", help="Sammelt aktuelle Metriken")
    sub.add_parser("trend-analysis", help="Führt eine Trendanalyse aus")
    health2_p = sub.add_parser("health-check", help="Überprüft den Gesundheitszustand des Systems")
    health2_p.add_argument("--components", help="Zu überprüfende Komponenten")
    sub.add_parser("diagnostic-run", help="Führt einen Diagnoselauf durch")
    sub.add_parser("usage-stats", help="Gibt Nutzungsstatistiken aus")

    # ------------------------------------------------------------------
    # Zusätzliche Workflow‑Befehle
    wf_exec2_p = sub.add_parser("workflow-execute", help="Führt einen bestehenden Workflow aus")
    wf_exec2_p.add_argument("name", help="Name des Workflows")
    wf_export2_p = sub.add_parser("workflow-export", help="Exportiert einen Workflow in eine Datei")
    wf_export2_p.add_argument("name", help="Name des Workflows")
    wf_export2_p.add_argument("output_file", help="Zieldatei")
    auto_setup2_p = sub.add_parser("automation-setup", help="Richtet Automatisierungsoptionen ein")
    auto_setup2_p.add_argument("config_file", help="Konfigurationsdatei")
    sched_manage2_p = sub.add_parser("scheduler-manage", help="Verwaltet einen Scheduler")
    sched_manage2_p.add_argument("schedule_name", help="Schedulername")
    sched_manage2_p.add_argument("action", help="Aktion (start, stop, status)")
    trigger2_p = sub.add_parser("trigger-setup", help="Richtet einen Trigger ein")
    trigger2_p.add_argument("trigger_name", help="Triggername")
    trigger2_p.add_argument("target", help="Zielname oder Datei")
    parallel2_p = sub.add_parser("parallel-execute", help="Führt mehrere Tasks parallel aus")
    parallel2_p.add_argument("tasks", help="Kommagetrennte Liste von Tasks")

    # ------------------------------------------------------------------
    # Zusätzliche GitHub‑Befehle
    gha2_p = sub.add_parser("github-repo-analyze", help="Analysiert ein Repository")
    gha2_p.add_argument("--analysis-type", help="Analyseart")
    gha2_p.add_argument("--target", help="Zielpfad")
    gpr2_p = sub.add_parser("github-pr-manage", help="Verwaltet Pull‑Requests")
    gpr2_p.add_argument("--reviewers", help="Reviewerliste")
    gpr2_p.add_argument("--ai-powered", action="store_true")
    gitrack_p = sub.add_parser("github-issue-track", help="Issue‑Tracker ansprechen")
    gitrack_p.add_argument("--project", help="Projektname")
    grelease_p = sub.add_parser("github-release-coord", help="Koordiniert ein Release")
    grelease_p.add_argument("version", help="Versionsnummer")
    grelease_p.add_argument("--auto-changelog", action="store_true")
    gwa2_p = sub.add_parser("github-workflow-auto", help="Automatisiert einen Workflow")
    gwa2_p.add_argument("file", help="Workflowdatei")
    gcr2_p = sub.add_parser("github-code-review", help="Führt Code‑Reviews durch")
    gcr2_p.add_argument("--multi-reviewer", action="store_true")
    gcr2_p.add_argument("--ai-powered", action="store_true")
    gsync_p = sub.add_parser("github-sync-coordinator", help="Synchronisiert mehrere Pakete")
    gsync_p.add_argument("--multi-package", action="store_true")

    # ------------------------------------------------------------------
    # Zusätzliche DAA‑Befehle
    dra2_p = sub.add_parser("daa-resource-alloc", help="Weist Ressourcen zu")
    dra2_p.add_argument("agent_id")
    dra2_p.add_argument("cpu")
    dra2_p.add_argument("memory")
    dcomm2_p = sub.add_parser("daa-communication", help="Kommunikation zwischen Agenten")
    dcomm2_p.add_argument("source")
    dcomm2_p.add_argument("target")
    dcomm2_p.add_argument("message")
    dcon2_p = sub.add_parser("daa-consensus", help="Startet einen Konsensprozess")
    dcon2_p.add_argument("proposal")

    # ------------------------------------------------------------------
    # Zusätzliche Systembefehle
    backup2_p = sub.add_parser("backup-create", help="Erstellt ein Backup")
    backup2_p.add_argument("output_file")
    restore2_p = sub.add_parser("restore-system", help="Stellt das System wieder her")
    restore2_p.add_argument("backup_file")
    config2_p = sub.add_parser("config-manage", help="Verwaltet die Konfiguration")
    config2_p.add_argument("operation")
    config2_p.add_argument("file", nargs="?")
    sub.add_parser("features-detect", help="Erkennt verfügbare Features")
    log2_p = sub.add_parser("log-analysis", help="Analysiert Logdateien")
    log2_p.add_argument("log_file")

    # ------------------------------------------------------------------
    # Hook‑Befehle
    hook2_p = sub.add_parser("hook", help="Führt einen Hook aus")
    hook2_p.add_argument("hook_name", help="Name des Hooks")
    hook2_p.add_argument("params", nargs=argparse.REMAINDER, help="Zusätzliche Parameter")
    fhv2_p = sub.add_parser("fix-hook-variables", help="Repariert Hook‑Variablen")
    fhv2_p.add_argument("target", nargs="?")
    fhv2_p.add_argument("--test", action="store_true")

    # ------------------------------------------------------------------
    # SPARC‑Befehle nach CLAUDE.md
    sub.add_parser("sparc-modes", help="Listet alle verfügbaren SPARC‑Modi auf")
    sparc_run_p = sub.add_parser("sparc-run", help="Führt einen SPARC‑Modus für eine Aufgabe aus")
    sparc_run_p.add_argument("mode", help="Name des SPARC‑Modus")
    sparc_run_p.add_argument("task", help="Beschreibung der Aufgabe in Anführungszeichen")
    sparc_run_p.add_argument("--parallel", action="store_true", help="Aktiviere parallele Verarbeitung")
    sparc_run_p.add_argument("--batch-optimize", action="store_true", help="Aktiviere Batchtools‑Optimierung")
    sparc_tdd_p = sub.add_parser("sparc-tdd", help="Führt einen vollständigen TDD‑Workflow aus")
    sparc_tdd_p.add_argument("feature", help="Beschreibung des Features")
    sparc_tdd_p.add_argument("--batch-tdd", action="store_true", help="Aktiviere parallele TDD‑Tests")
    sparc_info_p = sub.add_parser("sparc-info", help="Zeigt Details zu einem SPARC‑Modus")
    sparc_info_p.add_argument("mode", help="Name des Modus")
    sparc_batch_p = sub.add_parser("sparc-batch", help="Führt mehrere SPARC‑Modi parallel aus")
    sparc_batch_p.add_argument("modes", help="Kommagetrennte Liste von Modi")
    sparc_batch_p.add_argument("task", help="Aufgabenbeschreibung")
    sparc_pipeline_p = sub.add_parser("sparc-pipeline", help="Startet eine SPARC‑Pipeline für eine Aufgabe")
    sparc_pipeline_p.add_argument("task", help="Aufgabenbeschreibung")
    sparc_concurrent_p = sub.add_parser("sparc-concurrent", help="Verarbeitet mehrere Aufgaben parallel in einem Modus")
    sparc_concurrent_p.add_argument("mode", help="Name des Modus")
    sparc_concurrent_p.add_argument("tasks_file", help="Datei mit Aufgabenliste")

    # SPARC Full Workflow
    sparc_full_p = sub.add_parser("sparc-full", help="Führt einen vollständigen SPARC‑Workflow für ein Feature aus")
    sparc_full_p.add_argument("feature", help="Bezeichnung des Features, z. B. 'user authentication'")

    # ------------------------------------------------------------------
    # Automatisierter Projekt‑Workflow
    new_proj_p = sub.add_parser("new-project", help="Erstellt ein neues Projekt aus einer Idee und startet den gesamten Claude‑Flow‑Workflow")
    new_proj_p.add_argument("idea", help="Kurze Beschreibung der App oder des Features")
    new_proj_p.add_argument("--base-dir", dest="base_dir", default="projects", help="Basisverzeichnis für Projekte (Default: ./projects)")
    new_proj_p.add_argument("--template", dest="template", help="Optionales Template (Agile, DDD, HighPerformance, CICD)")

    # ------------------------------------------------------------------
    # Hintergrundausführung
    runbg_p = sub.add_parser("run-bg", help="Führt einen beliebigen claude-flow Befehl im Hintergrund aus")
    runbg_p.add_argument("cli_args", nargs=argparse.REMAINDER, help="Der Befehl und seine Parameter für claude-flow")

    # ------------------------------------------------------------------
    # Interaktiver Projektmanager
    sub.add_parser("manager", help="Startet das interaktive Projektmanager-Menü")

    return parser


def main(argv: Optional[List[str]] = None) -> None:
        # Initialisiere Umgebung und installiere fehlende Abhängigkeiten
        SetupManager.setup_environment()
        parser = build_parser()
        args = parser.parse_args(argv)
        cli = ClaudeFlowCLI(Path.cwd())

        cmd = args.command
        if cmd == "init":
            cli.init(args.project_name, args.hive_mind, args.neural_enhanced)
        elif cmd == "spawn":
            cli.hive_spawn(args.description, args.namespace, args.agents, args.temp)
        elif cmd == "resume":
            cli.hive_resume(args.session_id)
        elif cmd == "status":
            cli.hive_status()
        elif cmd == "sessions":
            cli.hive_sessions()
        elif cmd == "swarm":
            cli.swarm(args.task, args.continue_session, args.strategy)
        elif cmd == "memory-stats":
            cli.memory_stats()
        elif cmd == "memory-query":
            cli.memory_query(args.term, args.namespace, args.limit)
        elif cmd == "memory-store":
            cli.memory_store(args.key, args.value, args.namespace)
        elif cmd == "memory-export":
            cli.memory_export(args.output_file, args.namespace)
        elif cmd == "memory-import":
            cli.memory_import(args.input_file, args.namespace)
        elif cmd == "neural-train":
            cli.neural_train(args.pattern, args.epochs, args.data)
        elif cmd == "neural-predict":
            cli.neural_predict(args.model, args.input_file)
        elif cmd == "cognitive-analyze":
            cli.cognitive_analyze(args.behavior)
        elif cmd == "workflow-create":
            cli.workflow_create(args.name, args.parallel)
        elif cmd == "batch-process":
            cli.batch_process(args.items, args.concurrent)
        elif cmd == "pipeline-create":
            cli.pipeline_create(args.config_file)
        elif cmd == "github":
            cli.github_mode(args.mode, args.args)
        elif cmd == "daa-create":
            cli.daa_agent_create(args.agent_type, args.capabilities, args.resources, args.security_level, args.sandbox)
        elif cmd == "daa-match":
            cli.daa_capability_match(args.task_requirements)
        elif cmd == "daa-lifecycle":
            cli.daa_lifecycle_manage(args.agent_id, args.action)
        elif cmd == "security-scan":
            cli.security_scan(args.deep, args.report)
        elif cmd == "security-metrics":
            cli.security_metrics(args.last)
        elif cmd == "security-audit":
            cli.security_audit(args.full_trace)
        elif cmd == "swarm-init":
            cli.swarm_init(args.description)
        elif cmd == "agent-spawn":
            cli.agent_spawn(args.agent_type, args.capabilities, args.resources)
        elif cmd == "task-orchestrate":
            cli.task_orchestrate(args.task_description)
        elif cmd == "swarm-monitor":
            cli.swarm_monitor(args.dashboard, args.real_time)
        elif cmd == "topology-optimize":
            cli.topology_optimize()
        elif cmd == "load-balance":
            cli.load_balance()
        elif cmd == "coordination-sync":
            cli.coordination_sync()
        elif cmd == "swarm-scale":
            cli.swarm_scale(args.scale)
        elif cmd == "swarm-destroy":
            cli.swarm_destroy()
        elif cmd == "pattern-recognize":
            cli.pattern_recognize(args.pattern, args.input_file)
        elif cmd == "learning-adapt":
            cli.learning_adapt(args.model, args.data)
        elif cmd == "neural-compress":
            cli.neural_compress(args.model, args.output)
        elif cmd == "ensemble-create":
            cli.ensemble_create(args.models, args.output_model)
        elif cmd == "transfer-learn":
            cli.transfer_learn(args.base_model, args.new_data)
        elif cmd == "neural-explain":
            cli.neural_explain(args.model, args.input_file)
        elif cmd == "memory-usage":
            cli.memory_usage()
        elif cmd == "memory-search":
            cli.memory_search(args.term, args.namespace)
        elif cmd == "memory-persist":
            cli.memory_persist()
        elif cmd == "memory-namespace":
            cli.memory_namespace(args.namespace)
        elif cmd == "memory-backup":
            cli.memory_backup(args.output_file)
        elif cmd == "memory-restore":
            cli.memory_restore(args.input_file)
        elif cmd == "memory-compress":
            cli.memory_compress()
        elif cmd == "memory-sync":
            cli.memory_sync()
        elif cmd == "memory-analytics":
            cli.memory_analytics()
        elif cmd == "performance-report":
            cli.performance_report()
        elif cmd == "bottleneck-analyze":
            cli.bottleneck_analyze()
        elif cmd == "token-usage":
            cli.token_usage()
        elif cmd == "benchmark-run":
            cli.benchmark_run(args.benchmark_name)
        elif cmd == "metrics-collect":
            cli.metrics_collect()
        elif cmd == "trend-analysis":
            cli.trend_analysis()
        elif cmd == "health-check":
            cli.health_check(args.components)
        elif cmd == "diagnostic-run":
            cli.diagnostic_run()
        elif cmd == "usage-stats":
            cli.usage_stats()
        elif cmd == "workflow-execute":
            cli.workflow_execute(args.name)
        elif cmd == "workflow-export":
            cli.workflow_export(args.name, args.output_file)
        elif cmd == "automation-setup":
            cli.automation_setup(args.config_file)
        elif cmd == "scheduler-manage":
            cli.scheduler_manage(args.schedule_name, args.action)
        elif cmd == "trigger-setup":
            cli.trigger_setup(args.trigger_name, args.target)
        elif cmd == "parallel-execute":
            cli.parallel_execute(args.tasks)
        elif cmd == "github-repo-analyze":
            cli.github_repo_analyze(args.analysis_type, args.target)
        elif cmd == "github-pr-manage":
            cli.github_pr_manage(args.reviewers, args.ai_powered)
        elif cmd == "github-issue-track":
            cli.github_issue_track(args.project)
        elif cmd == "github-release-coord":
            cli.github_release_coord(args.version, args.auto_changelog)
        elif cmd == "github-workflow-auto":
            cli.github_workflow_auto(args.file)
        elif cmd == "github-code-review":
            cli.github_code_review(args.multi_reviewer, args.ai_powered)
        elif cmd == "github-sync-coordinator":
            cli.github_sync_coordinator(args.multi_package)
        elif cmd == "daa-resource-alloc":
            cli.daa_resource_alloc(args.agent_id, args.cpu, args.memory)
        elif cmd == "daa-communication":
            cli.daa_communication(args.source, args.target, args.message)
        elif cmd == "daa-consensus":
            cli.daa_consensus(args.proposal)
        elif cmd == "backup-create":
            cli.backup_create(args.output_file)
        elif cmd == "restore-system":
            cli.restore_system(args.backup_file)
        elif cmd == "config-manage":
            cli.config_manage(args.operation, args.file)
        elif cmd == "features-detect":
            cli.features_detect()
        elif cmd == "log-analysis":
            cli.log_analysis(args.log_file)
        elif cmd == "hook":
            cli.hook(args.hook_name, args.params)
        elif cmd == "fix-hook-variables":
            cli.fix_hook_variables(args.target, args.test)
        elif cmd == "sparc-modes":
            cli.sparc_modes()
        elif cmd == "sparc-run":
            cli.sparc_run(args.mode, args.task, args.parallel, args.batch_optimize)
        elif cmd == "sparc-tdd":
            cli.sparc_tdd(args.feature, args.batch_tdd)
        elif cmd == "sparc-info":
            cli.sparc_info(args.mode)
        elif cmd == "sparc-batch":
            cli.sparc_batch(args.modes, args.task)
        elif cmd == "sparc-pipeline":
            cli.sparc_pipeline(args.task)
        elif cmd == "sparc-concurrent":
            cli.sparc_concurrent(args.mode, args.tasks_file)
        elif cmd == "run-bg":
            # Die restlichen Argumente bilden den CLI‑Befehl für claude-flow
            cli.run_background(args.cli_args)
        elif cmd == "sparc-full":
            cli.sparc_full_workflow(args.feature)
        elif cmd == "new-project":
            # Starte die automatisierte Projektgenerierung
            base_dir = Path(args.base_dir).expanduser().resolve()
            pm = ProjectManager(base_dir, cli)
            pm.create_project(args.idea, template=args.template)
        elif cmd == "manager":
            # Interaktives Menü
            base_dir = Path("projects").expanduser().resolve()
            pm = ProjectManager(base_dir, cli)
            menu = ProjectManagerMenu(pm)
            menu.run()
        else:
            parser.print_help()


if __name__ == "__main__":
    main()