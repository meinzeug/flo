import os
from pathlib import Path
from typing import Optional
from openrouter_client import OpenRouterClient
from claude_flow_cli import ClaudeFlowCLI

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
        """Überwacht eine Hive‑Mind‑Session und führt bei Bedarf
        Selbstheilungsmaßnahmen aus.

        Die Methode durchsucht den Memory nach dem Begriff ``error`` und
        startet einen Fix‑Swarm, wenn Treffer gefunden werden. Anschließend
        werden ``fault_tolerance_retry`` und ``bottleneck_auto_optimize``
        aufgerufen, um die Performance zu verbessern. Da in dieser Umgebung
        keine echte Claude‑Flow‑Session läuft, dient die Implementierung nur
        als Demonstration.
        """
        print(f"[ProjectManager] Überwache Session {session_id} auf Fehler …")
        result = self.cli._run_capture(["memory", "query", "error", "--limit", "3"])
        if result and "error" in result.lower():
            print("[Monitor] Fehler gefunden – starte Fix-Swarm …")
            self.cli.swarm("Fix detected errors", continue_session=True)
        else:
            print("[Monitor] Keine Fehler im Memory gefunden.")

        # Optimierungs- und Retry-Mechanismen ausführen
        self.cli.fault_tolerance_retry()
        self.cli.bottleneck_auto_optimize()
        print("[ProjectManager] Selbstheilung abgeschlossen.")

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


__all__ = ["ProjectManager"]
