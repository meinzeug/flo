#!/usr/bin/env python3
"""
gui_flo.py – Grafische Benutzeroberfläche für die Flow‑Automatisierung

Dieses Modul nutzt Tkinter, um eine GUI‑Version des Kommandozeilen‑Tools
``run_flo.py`` bereitzustellen. Es greift auf dieselben Klassen
(SetupManager, ProjectManager, ClaudeFlowCLI) zurück und bietet Buttons,
Eingabefelder und Tabs, um die Funktionen von Claude‑Flow v2.0.0 Alpha
interaktiv auszuführen. Die GUI deckt die wichtigsten Abläufe ab:
Projekterstellung, Projektübersicht, Session‑Monitoring, Konfiguration,
Chat mit der Queen, Schnellbefehle, Befehls‑Palette sowie Rollback und
Recovery. Weitere Funktionen wie Self‑Healing und Performance‑Reports
können über zusätzliche Buttons integriert werden.

Hinweis: Diese GUI ist als theoretisches Beispiel gedacht. Da `npx
claude-flow@alpha` in der aktuellen Umgebung nicht installiert ist,
werden die Befehle lediglich angezeigt. In einer Umgebung mit
installiertem Claude‑Flow und den entsprechenden API‑Tokens können die
Befehle ausgeführt werden.
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
from pathlib import Path
from typing import Optional, Dict, List
import os

# Importiere die Klassen aus run_flo.py
from run_flo import SetupManager, ProjectManager, ClaudeFlowCLI


class GUIFlowApp:
    def __init__(self) -> None:
        # Stelle sicher, dass die Umgebung eingerichtet ist (theoretisch)
        try:
            SetupManager.setup_environment()
        except Exception:
            # Fehler werden ignoriert, da installation in dieser Umgebung nicht möglich ist
            pass
        # CLI und Projektmanager initialisieren
        self.cli = ClaudeFlowCLI()
        self.project_manager = ProjectManager(Path("projects"), self.cli)
        # Schnellbefehle verwalten
        self.quick_commands: Dict[str, List[str]] = {}
        # GUI erstellen
        self.root = tk.Tk()
        self.root.title("Flow GUI – Claude‑Flow Automation")
        self.root.geometry("900x600")

        # Notebook mit Tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill="both")

        # Tabs erstellen
        self.create_projects_tab()
        self.create_monitor_tab()
        self.create_chat_tab()
        self.create_config_tab()
        self.create_utilities_tab()
        self.create_advanced_tab()
        # Hilfe‑ und Report‑Tabs für bessere Benutzerfreundlichkeit
        self.create_help_tab()
        self.create_reports_tab()

    def run(self) -> None:
        self.root.mainloop()

    # ------------------------------------------------------------------
    # Tab: Projects
    def create_projects_tab(self) -> None:
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Projekte")

        # Projektidee
        idea_label = ttk.Label(frame, text="Projektidee:")
        idea_label.grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.idea_entry = ttk.Entry(frame, width=50)
        self.idea_entry.grid(row=0, column=1, padx=5, pady=5)

        # Template Auswahl
        tmpl_label = ttk.Label(frame, text="Template (optional):")
        tmpl_label.grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.template_var = tk.StringVar()
        tmpl_options = ["", "Agile", "DDD", "HighPerformance", "CICD", "WebApp", "CLI-Tool", "DataPipeline", "Microservices"]
        self.tmpl_combo = ttk.Combobox(frame, textvariable=self.template_var, values=tmpl_options)
        self.tmpl_combo.grid(row=1, column=1, padx=5, pady=5)

        # Button zur Projekterstellung
        create_btn = ttk.Button(frame, text="Projekt erstellen", command=self.create_project)
        create_btn.grid(row=2, column=0, pady=10)
        # Button für vollständigen Workflow (End‑to‑End) – erstellt ein Projekt und stößt alle Phasen an
        full_btn = ttk.Button(frame, text="Kompletten Workflow", command=self.full_workflow)
        full_btn.grid(row=2, column=1, pady=10)

        # Projektliste
        list_label = ttk.Label(frame, text="Vorhandene Projekte:")
        list_label.grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.projects_listbox = tk.Listbox(frame, height=10, width=50)
        self.projects_listbox.grid(row=4, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")
        list_btn = ttk.Button(frame, text="Liste aktualisieren", command=self.update_project_list)
        list_btn.grid(row=5, column=0, columnspan=2, pady=5)
        # Fülle initiale Liste
        self.update_project_list()

    def create_project(self) -> None:
        idea = self.idea_entry.get().strip()
        if not idea:
            messagebox.showwarning("Eingabefehler", "Bitte geben Sie eine Projektidee ein.")
            return
        template = self.template_var.get().strip() or None
        # Wenn kein Template angegeben, versuche eines zu inferieren
        if not template:
            suggestion = self.project_manager.infer_template(idea)
            if suggestion:
                if messagebox.askyesno("Template vorschlagen", f"Soll das Template '{suggestion}' verwendet werden?"):
                    template = suggestion
        # Starte Projekterstellung in separatem Thread, um die GUI nicht zu blockieren
        threading.Thread(target=self._create_project_thread, args=(idea, template), daemon=True).start()

    def full_workflow(self) -> None:
        """
        Erstellt ein neues Projekt und führt anschließend einen vollständigen
        Automatisierungsworkflow aus: Konzeptgenerierung, SPARC‑Workflow,
        neuronales TDD (optional), Self‑Healing, Performance‑Reporting und
        abschließende Release‑Koordination. Die Schritte laufen in einem
        separaten Thread, damit die GUI responsiv bleibt. Nach Abschluss
        wird der Benutzer informiert.
        """
        idea = self.idea_entry.get().strip()
        if not idea:
            messagebox.showwarning("Eingabefehler", "Bitte geben Sie eine Projektidee ein.")
            return
        template = self.template_var.get().strip() or None
        # Template vorschlagen, falls nicht angegeben
        if not template:
            suggestion = self.project_manager.infer_template(idea)
            if suggestion and messagebox.askyesno("Template vorschlagen", f"Soll das Template '{suggestion}' verwendet werden?"):
                template = suggestion
        threading.Thread(target=self._full_workflow_thread, args=(idea, template), daemon=True).start()

    def _full_workflow_thread(self, idea: str, template: Optional[str]) -> None:
        """
        Führt den End‑to‑End‑Workflow aus. Diese Methode wird im Hintergrund
        ausgeführt und ruft nacheinander Projektgenerierung, SPARC‑ und
        SDLC‑Workflows sowie Self‑Healing und Release‑Koordination auf.
        """
        # 1. Projekt erstellen
        self.project_manager.create_project(idea, template)
        # 2. SPARC Full Workflow (inkl. Spec, Architecture, TDD, Completion)
        self.cli.sparc_workflow_all(ai_guided=True, memory_enhanced=True)
        # 3. Optional neuronaler TDD‑Lauf
        self.cli.sparc_mode("neural-tdd", auto_learn=True)
        # 4. Self‑Healing und Performance‑Optimierung
        self.cli.health_auto_heal()
        self.cli.bottleneck_auto_optimize()
        # 5. Performance‑Reporting
        self.cli.performance_report()
        # 6. Release vorbereiten und koordinieren
        # Beispielversion 1.0.0; dies könnte dynamisch bestimmt werden
        self.cli.github_release_coord("1.0.0", auto_changelog=True)
        messagebox.showinfo("Workflow abgeschlossen", f"Projekt '{idea}' wurde vollständig verarbeitet.")

    def _create_project_thread(self, idea: str, template: Optional[str]) -> None:
        self.project_manager.create_project(idea, template)
        self.update_project_list()
        messagebox.showinfo("Fertig", f"Projekt '{idea}' wurde erstellt.")

    def update_project_list(self) -> None:
        self.projects_listbox.delete(0, tk.END)
        for p in sorted(self.project_manager.base_dir.glob("*")):
            if p.is_dir():
                self.projects_listbox.insert(tk.END, p.name)

    # ------------------------------------------------------------------
    # Tab: Monitoring & Healing
    def create_monitor_tab(self) -> None:
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Monitoring")
        ttk.Label(frame, text="Session‑ID für Monitoring:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.monitor_session_entry = ttk.Entry(frame, width=40)
        self.monitor_session_entry.grid(row=0, column=1, padx=5, pady=5)
        mon_btn = ttk.Button(frame, text="Überwachen & Heilen", command=self.monitor_and_heal)
        mon_btn.grid(row=0, column=2, padx=5, pady=5)
        # Monitoring-Ausgabe
        self.monitor_output = scrolledtext.ScrolledText(frame, width=80, height=20)
        self.monitor_output.grid(row=1, column=0, columnspan=3, padx=5, pady=5)
        # Buttons für Status
        ttk.Button(frame, text="Hive Status", command=self.hive_status).grid(row=2, column=0, padx=5, pady=5)
        ttk.Button(frame, text="Hive Sessions", command=self.hive_sessions).grid(row=2, column=1, padx=5, pady=5)
        ttk.Button(frame, text="Memory Stats", command=self.memory_stats).grid(row=2, column=2, padx=5, pady=5)

    def monitor_and_heal(self) -> None:
        session = self.monitor_session_entry.get().strip()
        if not session:
            messagebox.showwarning("Eingabefehler", "Bitte geben Sie eine Session‑ID ein.")
            return
        self.monitor_output.insert(tk.END, f"\nÜberwache Session {session} …\n")
        # theoretische Überwachung
        self.project_manager.monitor_and_self_heal(session)
        self.monitor_output.insert(tk.END, "Selbstheilung abgeschlossen.\n")

    def hive_status(self) -> None:
        self.monitor_output.insert(tk.END, "\nAktueller Hive‑Status:\n")
        result = self.cli._run_capture(["hive-mind", "status"])
        self.monitor_output.insert(tk.END, result + "\n")

    def hive_sessions(self) -> None:
        self.monitor_output.insert(tk.END, "\nAktive Sessions:\n")
        result = self.cli._run_capture(["hive-mind", "sessions"])
        self.monitor_output.insert(tk.END, result + "\n")

    def memory_stats(self) -> None:
        self.monitor_output.insert(tk.END, "\nSpeicherstatistiken:\n")
        result = self.cli._run_capture(["memory", "stats"])
        self.monitor_output.insert(tk.END, result + "\n")

    # ------------------------------------------------------------------
    # Tab: Chat
    def create_chat_tab(self) -> None:
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Chat")
        # Session ID
        ttk.Label(frame, text="Session‑ID:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.chat_session_entry = ttk.Entry(frame, width=40)
        self.chat_session_entry.grid(row=0, column=1, padx=5, pady=5)
        # Chat History
        self.chat_history = scrolledtext.ScrolledText(frame, width=80, height=20, state="disabled")
        self.chat_history.grid(row=1, column=0, columnspan=3, padx=5, pady=5)
        # Eingabefeld
        ttk.Label(frame, text="Nachricht:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.chat_entry = ttk.Entry(frame, width=60)
        self.chat_entry.grid(row=2, column=1, padx=5, pady=5)
        ttk.Button(frame, text="Senden", command=self.send_chat_message).grid(row=2, column=2, padx=5, pady=5)

    def send_chat_message(self) -> None:
        session_id = self.chat_session_entry.get().strip()
        message = self.chat_entry.get().strip()
        if not session_id or not message:
            messagebox.showwarning("Eingabefehler", "Bitte Session‑ID und Nachricht eingeben.")
            return
        # Zeige Nachricht im Chat History
        self.chat_history.configure(state="normal")
        self.chat_history.insert(tk.END, f"Sie: {message}\n")
        self.chat_history.configure(state="disabled")
        self.chat_entry.delete(0, tk.END)
        # Theoretische Übergabe an Queen (via Swarm)
        self.cli.swarm(message, continue_session=True)
        # In dieser Umgebung können wir keine Antwort empfangen
        self.chat_history.configure(state="normal")
        self.chat_history.insert(tk.END, "(Antwort der Queen folgt …)\n")
        self.chat_history.configure(state="disabled")

    # ------------------------------------------------------------------
    # Tab: Konfiguration
    def create_config_tab(self) -> None:
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Konfiguration")
        # GitHub Token
        ttk.Label(frame, text="GitHub Token:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.git_token_entry = ttk.Entry(frame, width=50)
        self.git_token_entry.grid(row=0, column=1, padx=5, pady=5)
        # OpenRouter Token
        ttk.Label(frame, text="OpenRouter Token:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.openrouter_token_entry = ttk.Entry(frame, width=50)
        self.openrouter_token_entry.grid(row=1, column=1, padx=5, pady=5)
        # Modell
        ttk.Label(frame, text="OpenRouter Modell:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.model_entry = ttk.Entry(frame, width=50)
        self.model_entry.grid(row=2, column=1, padx=5, pady=5)
        # Buttons
        save_btn = ttk.Button(frame, text="Speichern", command=self.save_config)
        save_btn.grid(row=3, column=0, columnspan=2, pady=10)
        # Spracheinstellung
        ttk.Label(frame, text="Sprache (de/en):").grid(row=4, column=0, padx=5, pady=5, sticky="e")
        self.lang_var = tk.StringVar(value=os.environ.get("FLO_LANG", "de"))
        lang_entry = ttk.Entry(frame, textvariable=self.lang_var, width=10)
        lang_entry.grid(row=4, column=1, padx=5, pady=5, sticky="w")
        # Lade vorhandene Werte
        self.load_config()

    def load_config(self) -> None:
        # Lade aus Umgebungsvariablen, falls vorhanden
        self.git_token_entry.delete(0, tk.END)
        self.git_token_entry.insert(0, os.environ.get("GIT_TOKEN", ""))
        self.openrouter_token_entry.delete(0, tk.END)
        self.openrouter_token_entry.insert(0, os.environ.get("OPENROUTER_TOKEN", ""))
        self.model_entry.delete(0, tk.END)
        self.model_entry.insert(0, os.environ.get("OPENROUTER_MODEL", ""))

    def save_config(self) -> None:
        git = self.git_token_entry.get().strip()
        openr = self.openrouter_token_entry.get().strip()
        model = self.model_entry.get().strip()
        if git:
            os.environ["GIT_TOKEN"] = git
        if openr:
            os.environ["OPENROUTER_TOKEN"] = openr
        if model:
            os.environ["OPENROUTER_MODEL"] = model
        # Sprache
        lang = self.lang_var.get().strip().lower() or "de"
        os.environ["FLO_LANG"] = lang
        # Aktualisiere .env
        with open(".env", "w") as f:
            if git:
                f.write(f"GIT_TOKEN={git}\n")
            if openr:
                f.write(f"OPENROUTER_TOKEN={openr}\n")
            if model:
                f.write(f"OPENROUTER_MODEL={model}\n")
            if lang:
                f.write(f"FLO_LANG={lang}\n")
        messagebox.showinfo("Gespeichert", ".env und Umgebungsvariablen wurden aktualisiert.")

    # ------------------------------------------------------------------
    # Tab: Utilities (Quick Commands, History, Command Palette, Rollback)
    def create_utilities_tab(self) -> None:
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Utilities")
        # Quick Commands
        quick_frame = ttk.LabelFrame(frame, text="Quick Commands")
        quick_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        ttk.Button(quick_frame, text="Quick Command hinzufügen", command=self.add_quick_command).grid(row=0, column=0, padx=5, pady=5)
        ttk.Button(quick_frame, text="Quick Commands ausführen", command=self.run_quick_command).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(quick_frame, text="Liste anzeigen", command=self.list_quick_commands).grid(row=0, column=2, padx=5, pady=5)
        ttk.Button(quick_frame, text="Quick Command löschen", command=self.delete_quick_command).grid(row=0, column=3, padx=5, pady=5)
        # History
        history_frame = ttk.LabelFrame(frame, text="Historie")
        history_frame.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        ttk.Button(history_frame, text="Historie anzeigen", command=self.show_history).grid(row=0, column=0, padx=5, pady=5)
        ttk.Button(history_frame, text="Historie löschen", command=self.clear_history).grid(row=0, column=1, padx=5, pady=5)
        # Command Palette
        palette_frame = ttk.LabelFrame(frame, text="Befehls‑Palette")
        palette_frame.grid(row=2, column=0, padx=5, pady=5, sticky="nsew")
        ttk.Button(palette_frame, text="Palette starten", command=self.command_palette_gui).grid(row=0, column=0, padx=5, pady=5)
        # Rollback/Recovery
        rr_frame = ttk.LabelFrame(frame, text="Rollback & Recovery")
        rr_frame.grid(row=3, column=0, padx=5, pady=5, sticky="nsew")
        ttk.Button(rr_frame, text="Init Rollback", command=self.cli.init_rollback).grid(row=0, column=0, padx=5, pady=5)
        ttk.Button(rr_frame, text="Recovery (last-safe-state)", command=self.cli.recovery).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(rr_frame, text="Recovery Punkt", command=self.recovery_point).grid(row=0, column=2, padx=5, pady=5)

    # Quick Command Funktionen
    def add_quick_command(self) -> None:
        name = simple_input(self.root, "Quick Command Name", "Name:")
        if not name:
            return
        cmd = simple_input(self.root, "Claude‑Flow Args", "Argumente für Claude‑Flow (z. B. hive-mind status):")
        if not cmd:
            return
        self.quick_commands[name] = cmd.split()
        messagebox.showinfo("Quick Command", f"Quick Command '{name}' gespeichert.")

    def run_quick_command(self) -> None:
        if not self.quick_commands:
            messagebox.showinfo("Quick Commands", "Keine Quick Commands definiert.")
            return
        # Auswahl
        names = list(self.quick_commands.keys())
        selection = simple_choice(self.root, "Quick Commands", "Wählen Sie einen Command:", names)
        if not selection:
            return
        args = self.quick_commands.get(selection)
        if args:
            self.cli._run(args)
            messagebox.showinfo("Ausgeführt", f"Quick Command '{selection}' ausgeführt.")

    def list_quick_commands(self) -> None:
        if not self.quick_commands:
            messagebox.showinfo("Quick Commands", "Keine Quick Commands definiert.")
            return
        info = "\n".join([f"{name}: {' '.join(args)}" for name, args in self.quick_commands.items()])
        messagebox.showinfo("Quick Commands", info)

    def delete_quick_command(self) -> None:
        if not self.quick_commands:
            messagebox.showinfo("Quick Commands", "Keine Quick Commands definiert.")
            return
        names = list(self.quick_commands.keys())
        selection = simple_choice(self.root, "Quick Commands", "Wählen Sie einen zu löschenden Command:", names)
        if selection and selection in self.quick_commands:
            del self.quick_commands[selection]
            messagebox.showinfo("Gelöscht", f"Quick Command '{selection}' wurde gelöscht.")

    # History Funktionen
    def show_history(self) -> None:
        # Zeige CLI-Historie an
        if not self.cli.command_history:
            messagebox.showinfo("Historie", "Keine Befehle in der Historie.")
            return
        info = "\n".join([f"{idx+1}. {cmd}" for idx, cmd in enumerate(self.cli.command_history)])
        messagebox.showinfo("Historie", info)

    def clear_history(self) -> None:
        self.cli.history_clear()
        messagebox.showinfo("Historie", "Die Historie wurde gelöscht.")

    # Befehls‑Palette als GUI
    def command_palette_gui(self) -> None:
        user_input = simple_input(self.root, "Befehls‑Palette", "Geben Sie einen Befehl ein:")
        if not user_input:
            return
        # Verwende dieselbe Logik wie im CLI-Menü
        text = user_input.lower().strip()
        if "status" in text:
            self.cli.hive_status()
        elif "session" in text and "list" in text:
            self.cli.hive_sessions()
        elif "memory" in text and ("stats" in text or "statistik" in text):
            self.cli.memory_stats()
        elif "init" in text:
            proj = simple_input(self.root, "Projektname", "Projektname (leer lassen für Standard):") or None
            self.cli.init(project_name=proj)
        elif "spawn" in text and "hive" in text:
            desc = simple_input(self.root, "Hive Spawn", "Beschreibung des neuen Hives:") or ""
            ns = simple_input(self.root, "Namespace", "Namespace (optional):") or None
            agents = simple_input(self.root, "Agents", "Agenten (Zahl oder Liste):") or None
            self.cli.hive_spawn(desc, namespace=ns, agents=agents)
        elif "swarm" in text and "start" in text:
            desc = simple_input(self.root, "Swarm", "Aufgabenbeschreibung für den Swarm:") or ""
            self.cli.swarm(desc)
        elif "performance" in text:
            self.cli.performance_report()
        elif "health" in text or "gesund" in text:
            self.cli.health_auto_heal()
            self.cli.health_check(None)
        else:
            messagebox.showinfo("Palette", "Kein passender Befehl erkannt.")

    # Recovery Punkt
    def recovery_point(self) -> None:
        point = simple_input(self.root, "Recovery Punkt", "Name des Wiederherstellungspunkts:") or "last-safe-state"
        self.cli.recovery(point)

    # ------------------------------------------------------------------
    # Tab: Advanced – bündelt weiterführende Funktionen aus run_flo.py
    def create_advanced_tab(self) -> None:
        """
        Erstellt einen Tab mit einem eigenen Notebook, das die fortgeschrittenen
        Funktionen von Claude‑Flow gruppiert. Jede Kategorie erhält einen
        eigenen Untertab.
        """
        adv_frame = ttk.Frame(self.notebook)
        self.notebook.add(adv_frame, text="Advanced")
        adv_nb = ttk.Notebook(adv_frame)
        adv_nb.pack(fill='both', expand=True)
        # Self-Healing & Optimierung
        self.create_self_heal_tab(adv_nb)
        # SPARC & Neural
        self.create_sparc_neural_tab(adv_nb)
        # Metrics & Memory
        self.create_metrics_memory_tab(adv_nb)
        # Security & Compliance
        self.create_security_tab(adv_nb)
        # GitHub
        self.create_github_tab(adv_nb)
        # Workflow & Automation
        self.create_workflow_tab(adv_nb)
        # DAA Agents
        self.create_daa_tab(adv_nb)
        # System Tools
        self.create_system_tab(adv_nb)
        # Swarm Tools
        self.create_swarm_tools_tab(adv_nb)
        # SPARC Batch
        self.create_sparc_batch_tab(adv_nb)
        # Specialized Patterns
        self.create_patterns_tab(adv_nb)

    # ------------------------------------------------------------------
    # Tab: Help – Zeigt wichtige Hinweise und Richtlinien
    def create_help_tab(self) -> None:
        """
        Erstellt einen Hilfe‑Tab, der die wichtigsten Regeln aus den
        offiziellen Claude‑Flow‑Dokumenten zusammenfasst. Dieser Tab
        informiert Anwender über die goldene Regel der SPARC‑Entwicklung,
        beschreibt kurz die SPARC‑Phasen und listet gängige Agententypen
        auf. Dadurch können auch Einsteiger verstehen, wie die KI‑
        Orchestrierung arbeitet und welche Best Practices gelten.
        """
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Hilfe")
        text = (
            "Goldene Regel (Concurrency):\n"
            "Alle zusammenhängenden Operationen – wie TodoWrite, Dateizugriffe, "
            "Speicheraktionen und Shell‑Kommandos – sollten in einer einzigen "
            "Nachricht gebündelt werden, um maximale Effizienz zu erzielen.\n\n"
            "SPARC‑Phasen:\n"
            "1. Spezifikation & Pseudocode: Definieren Sie die Anforderungen und "
            "übersetzen Sie diese in eine pseudocodeartige Form.\n"
            "2. Architektur: Legen Sie das Systemdesign fest (Schichten, Module).\n"
            "3. Refinement/TDD: Implementieren Sie testgetrieben und modular.\n"
            "4. Fertigstellung: Führen Sie Integrationstests durch und bereiten "
            "die Auslieferung vor.\n\n"
            "Agententypen:\n"
            "- Queen: Koordiniert alle anderen Agenten.\n"
            "- Architect, Coder, Tester, Researcher, Security, DevOps: Spezialisierte "
            "Worker, die von der Queen orchestriert werden.\n"
            "- Consensus & Performance Agents: Treffen Entscheidungen und überwachen "
            "das System.\n\n"
            "Weitere Informationen finden Sie im README und in der CLAUDE.md "
            "auf GitHub."
        )
        help_text = scrolledtext.ScrolledText(frame, width=80, height=25, wrap=tk.WORD)
        help_text.insert(tk.END, text)
        help_text.configure(state="disabled")
        help_text.pack(padx=10, pady=10, fill="both", expand=True)

    # ------------------------------------------------------------------
    # Tab: Reports – Automatische Zusammenfassungen und Protokolle
    def create_reports_tab(self) -> None:
        """
        Erstellt einen Tab, der das Generieren von Berichten erleichtert. Hier
        können Nutzer mit einem Klick eine Zusammenfassung des aktuellen
        Projektstatus erzeugen, die Speicherstatistiken, Metriken und eine
        Liste der aktiven Hives kombiniert. Die generierten Berichte werden
        als Text angezeigt und könnten bei Bedarf in Dateien gespeichert
        werden.
        """
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Berichte")
        ttk.Label(frame, text="Berichte & Zusammenfassungen").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        ttk.Button(frame, text="Bericht erstellen", command=self.generate_report).grid(row=0, column=1, padx=5, pady=5)
        self.report_text = scrolledtext.ScrolledText(frame, width=90, height=25, wrap=tk.WORD)
        self.report_text.grid(row=1, column=0, columnspan=2, padx=5, pady=5)

    def generate_report(self) -> None:
        """
        Kombiniert verschiedene CLI‑Aufrufe, um eine Zusammenfassung des
        aktuellen Projektstatus zu erzeugen: Hive‑Sessions, Hive‑Status,
        Speicherstatistiken und Metriken. Die Ergebnisse werden im
        Berichtsfeld ausgegeben.
        """
        lines = []
        lines.append("==== Hive Sessions ====")
        lines.append(self.cli._run_capture(["hive-mind", "sessions"]))
        lines.append("\n==== Hive Status ====")
        lines.append(self.cli._run_capture(["hive-mind", "status"]))
        lines.append("\n==== Memory Stats ====")
        lines.append(self.cli._run_capture(["memory", "stats"]))
        lines.append("\n==== Performance Report ====")
        lines.append(self.cli._run_capture(["performance", "report"]))
        report = "\n".join(lines)
        self.report_text.delete("1.0", tk.END)
        self.report_text.insert(tk.END, report)

    # Self-Healing Tab
    def create_self_heal_tab(self, notebook: ttk.Notebook) -> None:
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Self‑Healing")
        ttk.Label(frame, text="Automatische Heilung & Optimierung").grid(row=0, column=0, padx=5, pady=5, columnspan=3)
        ttk.Button(frame, text="Health Auto Heal", command=self.cli.health_auto_heal).grid(row=1, column=0, padx=5, pady=5)
        ttk.Button(frame, text="Fault Tolerance Retry", command=self.cli.fault_tolerance_retry).grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(frame, text="Bottleneck Auto Optimize", command=self.cli.bottleneck_auto_optimize).grid(row=1, column=2, padx=5, pady=5)

    # SPARC & Neural Tab
    def create_sparc_neural_tab(self, notebook: ttk.Notebook) -> None:
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="SPARC/Neural")
        # SPARC Workflows
        ttk.Label(frame, text="SPARC Workflows").grid(row=0, column=0, columnspan=3, padx=5, pady=5)
        ttk.Button(frame, text="Neural TDD", command=lambda: self.cli.sparc_mode("neural-tdd", auto_learn=True)).grid(row=1, column=0, padx=5, pady=5)
        ttk.Button(frame, text="Full SPARC Workflow", command=lambda: self.cli.sparc_workflow_all(ai_guided=True, memory_enhanced=True)).grid(row=1, column=1, padx=5, pady=5)
        # Neural Tools
        ttk.Label(frame, text="Neural Tools").grid(row=2, column=0, columnspan=3, padx=5, pady=5)
        ttk.Button(frame, text="Train Model", command=lambda: self.neural_train_prompt()).grid(row=3, column=0, padx=5, pady=5)
        ttk.Button(frame, text="Predict", command=lambda: self.neural_predict_prompt()).grid(row=3, column=1, padx=5, pady=5)
        ttk.Button(frame, text="Pattern Recognize", command=lambda: self.pattern_recognize_prompt()).grid(row=3, column=2, padx=5, pady=5)
        ttk.Button(frame, text="Learning Adapt", command=lambda: self.learning_adapt_prompt()).grid(row=4, column=0, padx=5, pady=5)
        ttk.Button(frame, text="Compress Model", command=lambda: self.compress_model_prompt()).grid(row=4, column=1, padx=5, pady=5)
        ttk.Button(frame, text="Ensemble Create", command=lambda: self.ensemble_create_prompt()).grid(row=4, column=2, padx=5, pady=5)
        ttk.Button(frame, text="Transfer Learn", command=lambda: self.transfer_learn_prompt()).grid(row=5, column=0, padx=5, pady=5)
        ttk.Button(frame, text="Explain Model", command=lambda: self.explain_model_prompt()).grid(row=5, column=1, padx=5, pady=5)
        ttk.Button(frame, text="Cognitive Analyze", command=lambda: self.cognitive_analyze_prompt()).grid(row=5, column=2, padx=5, pady=5)

    # Metrics & Memory Tab
    def create_metrics_memory_tab(self, notebook: ttk.Notebook) -> None:
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Metrics/Memory")
        # Memory Operations
        mem_label = ttk.Label(frame, text="Memory Operations")
        mem_label.grid(row=0, column=0, columnspan=5, pady=5)
        ttk.Button(frame, text="Stats", command=self.cli.memory_stats).grid(row=1, column=0, padx=5, pady=5)
        ttk.Button(frame, text="Compress", command=self.cli.memory_compress).grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(frame, text="Sync", command=self.cli.memory_sync).grid(row=1, column=2, padx=5, pady=5)
        ttk.Button(frame, text="Analytics", command=self.cli.memory_analytics).grid(row=1, column=3, padx=5, pady=5)
        ttk.Button(frame, text="Usage", command=self.cli.memory_usage).grid(row=1, column=4, padx=5, pady=5)
        ttk.Button(frame, text="Persist", command=self.cli.memory_persist).grid(row=2, column=0, padx=5, pady=5)
        ttk.Button(frame, text="Namespace", command=lambda: self.memory_namespace_prompt()).grid(row=2, column=1, padx=5, pady=5)
        ttk.Button(frame, text="Search", command=lambda: self.memory_search_prompt()).grid(row=2, column=2, padx=5, pady=5)
        ttk.Button(frame, text="Export", command=lambda: self.memory_export_prompt()).grid(row=2, column=3, padx=5, pady=5)
        ttk.Button(frame, text="Import", command=lambda: self.memory_import_prompt()).grid(row=2, column=4, padx=5, pady=5)
        ttk.Button(frame, text="Store", command=lambda: self.memory_store_prompt()).grid(row=3, column=0, padx=5, pady=5)
        # Performance / Metrics
        perf_label = ttk.Label(frame, text="Performance Tools")
        perf_label.grid(row=4, column=0, columnspan=5, pady=5)
        ttk.Button(frame, text="Report", command=self.cli.performance_report).grid(row=5, column=0, padx=5, pady=5)
        ttk.Button(frame, text="Bottleneck", command=self.cli.bottleneck_analyze).grid(row=5, column=1, padx=5, pady=5)
        ttk.Button(frame, text="Token Usage", command=self.cli.token_usage).grid(row=5, column=2, padx=5, pady=5)
        ttk.Button(frame, text="Metrics Collect", command=self.cli.metrics_collect).grid(row=5, column=3, padx=5, pady=5)
        ttk.Button(frame, text="Trend Analysis", command=self.cli.trend_analysis).grid(row=5, column=4, padx=5, pady=5)
        ttk.Button(frame, text="Usage Stats", command=self.cli.usage_stats).grid(row=6, column=0, padx=5, pady=5)
        ttk.Button(frame, text="Health Check", command=lambda: self.cli.health_check(None)).grid(row=6, column=1, padx=5, pady=5)
        ttk.Button(frame, text="Diagnostic Run", command=self.cli.diagnostic_run).grid(row=6, column=2, padx=5, pady=5)

    # Security & Compliance Tab
    def create_security_tab(self, notebook: ttk.Notebook) -> None:
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Security")
        ttk.Label(frame, text="Security & Compliance").grid(row=0, column=0, columnspan=3, pady=5)
        ttk.Button(frame, text="Security Scan", command=lambda: self.cli.security_scan(deep=True, report=True)).grid(row=1, column=0, padx=5, pady=5)
        ttk.Button(frame, text="Security Metrics", command=lambda: self.security_metrics_prompt()).grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(frame, text="Security Audit", command=lambda: self.security_audit_prompt()).grid(row=1, column=2, padx=5, pady=5)
        # Repo Architect Optimize
        ttk.Button(frame, text="Repo Architect Optimize", command=lambda: self.repo_architect_prompt()).grid(row=2, column=0, padx=5, pady=5)

    # GitHub Tab
    def create_github_tab(self, notebook: ttk.Notebook) -> None:
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="GitHub")
        ttk.Label(frame, text="GitHub Tools").grid(row=0, column=0, columnspan=3, pady=5)
        ttk.Button(frame, text="Repo Analyze", command=lambda: self.github_repo_analyze_prompt()).grid(row=1, column=0, padx=5, pady=5)
        ttk.Button(frame, text="PR Manage", command=lambda: self.github_pr_manage_prompt()).grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(frame, text="Issue Track", command=lambda: self.github_issue_prompt()).grid(row=1, column=2, padx=5, pady=5)
        ttk.Button(frame, text="Release Coord", command=lambda: self.github_release_prompt()).grid(row=2, column=0, padx=5, pady=5)
        ttk.Button(frame, text="Workflow Auto", command=lambda: self.github_workflow_prompt()).grid(row=2, column=1, padx=5, pady=5)
        ttk.Button(frame, text="Code Review", command=lambda: self.github_code_review_prompt()).grid(row=2, column=2, padx=5, pady=5)
        ttk.Button(frame, text="Sync Coordinator", command=lambda: self.github_sync_coord_prompt()).grid(row=3, column=0, padx=5, pady=5)

    # Workflow Tab
    def create_workflow_tab(self, notebook: ttk.Notebook) -> None:
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Workflow")
        ttk.Label(frame, text="Workflow & Automation").grid(row=0, column=0, columnspan=2, pady=5)
        ttk.Button(frame, text="Workflow Create", command=lambda: self.workflow_create_prompt()).grid(row=1, column=0, padx=5, pady=5)
        ttk.Button(frame, text="Workflow Execute", command=lambda: self.workflow_execute_prompt()).grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(frame, text="Workflow Export", command=lambda: self.workflow_export_prompt()).grid(row=2, column=0, padx=5, pady=5)
        ttk.Button(frame, text="Pipeline Create", command=lambda: self.pipeline_create_prompt()).grid(row=2, column=1, padx=5, pady=5)
        ttk.Button(frame, text="Scheduler Manage", command=lambda: self.scheduler_manage_prompt()).grid(row=3, column=0, padx=5, pady=5)
        ttk.Button(frame, text="Trigger Setup", command=lambda: self.trigger_setup_prompt()).grid(row=3, column=1, padx=5, pady=5)
        ttk.Button(frame, text="Batch Process", command=lambda: self.batch_process_prompt()).grid(row=4, column=0, padx=5, pady=5)
        ttk.Button(frame, text="Parallel Execute", command=lambda: self.parallel_execute_prompt()).grid(row=4, column=1, padx=5, pady=5)

    # DAA Tab
    def create_daa_tab(self, notebook: ttk.Notebook) -> None:
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="DAA")
        ttk.Label(frame, text="Dynamic Agent Architecture").grid(row=0, column=0, columnspan=3, pady=5)
        ttk.Button(frame, text="Agent Create", command=lambda: self.daa_agent_create_prompt()).grid(row=1, column=0, padx=5, pady=5)
        ttk.Button(frame, text="Capability Match", command=lambda: self.daa_capability_prompt()).grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(frame, text="Lifecycle Manage", command=lambda: self.daa_lifecycle_prompt()).grid(row=1, column=2, padx=5, pady=5)
        ttk.Button(frame, text="Resource Alloc", command=lambda: self.daa_resource_prompt()).grid(row=2, column=0, padx=5, pady=5)
        ttk.Button(frame, text="Communication", command=lambda: self.daa_communication_prompt()).grid(row=2, column=1, padx=5, pady=5)
        ttk.Button(frame, text="Consensus", command=lambda: self.daa_consensus_prompt()).grid(row=2, column=2, padx=5, pady=5)

    # System Tab
    def create_system_tab(self, notebook: ttk.Notebook) -> None:
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="System")
        ttk.Label(frame, text="System Tools").grid(row=0, column=0, columnspan=3, pady=5)
        ttk.Button(frame, text="Config Manage", command=lambda: self.config_manage_prompt()).grid(row=1, column=0, padx=5, pady=5)
        ttk.Button(frame, text="Features Detect", command=self.cli.features_detect).grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(frame, text="Log Analysis", command=lambda: self.log_analysis_prompt()).grid(row=1, column=2, padx=5, pady=5)

    # Swarm Tools Tab
    def create_swarm_tools_tab(self, notebook: ttk.Notebook) -> None:
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Swarm Tools")
        ttk.Label(frame, text="Swarm Orchestration").grid(row=0, column=0, columnspan=3, pady=5)
        ttk.Button(frame, text="Swarm Init", command=lambda: self.swarm_init_prompt()).grid(row=1, column=0, padx=5, pady=5)
        ttk.Button(frame, text="Agent Spawn", command=lambda: self.agent_spawn_prompt()).grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(frame, text="Task Orchestrate", command=lambda: self.task_orchestrate_prompt()).grid(row=1, column=2, padx=5, pady=5)
        ttk.Button(frame, text="Swarm Monitor", command=lambda: self.swarm_monitor_prompt()).grid(row=2, column=0, padx=5, pady=5)
        ttk.Button(frame, text="Topology Optimize", command=self.cli.topology_optimize).grid(row=2, column=1, padx=5, pady=5)
        ttk.Button(frame, text="Load Balance", command=self.cli.load_balance).grid(row=2, column=2, padx=5, pady=5)
        ttk.Button(frame, text="Coordination Sync", command=self.cli.coordination_sync).grid(row=3, column=0, padx=5, pady=5)
        ttk.Button(frame, text="Swarm Scale", command=lambda: self.swarm_scale_prompt()).grid(row=3, column=1, padx=5, pady=5)
        ttk.Button(frame, text="Swarm Destroy", command=self.cli.swarm_destroy).grid(row=3, column=2, padx=5, pady=5)

    # SPARC Batch Tab
    def create_sparc_batch_tab(self, notebook: ttk.Notebook) -> None:
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="SPARC Batch")
        ttk.Label(frame, text="SPARC Batch & Concurrent").grid(row=0, column=0, columnspan=3, pady=5)
        ttk.Button(frame, text="SPARC Batch", command=lambda: self.sparc_batch_prompt()).grid(row=1, column=0, padx=5, pady=5)
        ttk.Button(frame, text="SPARC Pipeline", command=lambda: self.sparc_pipeline_prompt()).grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(frame, text="SPARC Concurrent", command=lambda: self.sparc_concurrent_prompt()).grid(row=1, column=2, padx=5, pady=5)

    # Patterns Tab
    def create_patterns_tab(self, notebook: ttk.Notebook) -> None:
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Patterns")
        ttk.Label(frame, text="Spezialisierte Swarm‑Muster").grid(row=0, column=0, columnspan=4, pady=5)
        ttk.Button(frame, text="Full Stack", command=lambda: self.spawn_pattern("full-stack", "coder,architect,tester" )).grid(row=1, column=0, padx=5, pady=5)
        ttk.Button(frame, text="Front‑End", command=lambda: self.spawn_pattern("frontend", "frontend-coder,tester" )).grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(frame, text="Back‑End", command=lambda: self.spawn_pattern("backend", "backend-coder,tester" )).grid(row=1, column=2, padx=5, pady=5)
        ttk.Button(frame, text="Distributed", command=lambda: self.spawn_pattern("distributed", "researcher,architect,tester" )).grid(row=1, column=3, padx=5, pady=5)
        ttk.Button(frame, text="Custom", command=lambda: self.custom_pattern_prompt()).grid(row=2, column=0, padx=5, pady=5)

    # Utility Prompt Methods for Advanced Tabs
    def neural_train_prompt(self) -> None:
        pattern = simple_input(self.root, "Neural Train", "Trainingsmuster/Name:") or ""
        epochs_str = simple_input(self.root, "Neural Train", "Anzahl der Epochen (Standard 50):") or "50"
        try:
            epochs = int(epochs_str)
        except Exception:
            epochs = 50
        data_file = simple_input(self.root, "Neural Train", "Datenquelle (optional):")
        self.cli.neural_train(pattern, epochs, data_file)

    def neural_predict_prompt(self) -> None:
        model = simple_input(self.root, "Neural Predict", "Modellname:") or ""
        input_file = simple_input(self.root, "Neural Predict", "Eingabedatei:") or ""
        self.cli.neural_predict(model, input_file)

    def pattern_recognize_prompt(self) -> None:
        pattern = simple_input(self.root, "Pattern Recognize", "Mustername:") or ""
        input_file = simple_input(self.root, "Pattern Recognize", "Eingabedatei (optional):")
        self.cli.pattern_recognize(pattern, input_file)

    def learning_adapt_prompt(self) -> None:
        model = simple_input(self.root, "Learning Adapt", "Modellname:") or ""
        data_file = simple_input(self.root, "Learning Adapt", "Datenquelle (optional):")
        self.cli.learning_adapt(model, data_file)

    def compress_model_prompt(self) -> None:
        model = simple_input(self.root, "Model Compress", "Modellname:") or ""
        out = simple_input(self.root, "Model Compress", "Ausgabedatei (optional):")
        self.cli.neural_compress(model, out)

    def ensemble_create_prompt(self) -> None:
        models = simple_input(self.root, "Ensemble Create", "Modelle (kommagetrennt):") or ""
        output_model = simple_input(self.root, "Ensemble Create", "Name des Ensemble-Modells:") or ""
        self.cli.ensemble_create(models, output_model)

    def transfer_learn_prompt(self) -> None:
        base = simple_input(self.root, "Transfer Learn", "Basismodell:") or ""
        new_data = simple_input(self.root, "Transfer Learn", "Neue Daten:") or ""
        self.cli.transfer_learn(base, new_data)

    def explain_model_prompt(self) -> None:
        model = simple_input(self.root, "Model Explain", "Modellname:") or ""
        input_file = simple_input(self.root, "Model Explain", "Eingabedatei:") or ""
        self.cli.neural_explain(model, input_file)

    def cognitive_analyze_prompt(self) -> None:
        behaviour = simple_input(self.root, "Cognitive Analyze", "Verhalten/Beschreibung:") or ""
        self.cli.cognitive_analyze(behaviour)

    def memory_namespace_prompt(self) -> None:
        ns = simple_input(self.root, "Memory Namespace", "Namespace:") or ""
        self.cli.memory_namespace(ns)

    def memory_search_prompt(self) -> None:
        term = simple_input(self.root, "Memory Search", "Suchbegriff:") or ""
        ns = simple_input(self.root, "Memory Search", "Namespace (optional):")
        self.cli.memory_search(term, ns)

    def memory_export_prompt(self) -> None:
        outfile = simple_input(self.root, "Memory Export", "Ausgabedatei:") or "memory_export.json"
        ns = simple_input(self.root, "Memory Export", "Namespace (optional):")
        self.cli.memory_export(outfile, ns)

    def memory_import_prompt(self) -> None:
        infile = simple_input(self.root, "Memory Import", "Eingabedatei:") or "memory_export.json"
        ns = simple_input(self.root, "Memory Import", "Namespace (optional):")
        self.cli.memory_import(infile, ns)

    def memory_store_prompt(self) -> None:
        key = simple_input(self.root, "Memory Store", "Schlüssel:") or ""
        value = simple_input(self.root, "Memory Store", "Wert:") or ""
        ns = simple_input(self.root, "Memory Store", "Namespace (optional):")
        self.cli.memory_store(key, value, ns)

    def security_metrics_prompt(self) -> None:
        last = simple_input(self.root, "Security Metrics", "Zeitraum (z. B. last-24h) oder leer:")
        self.cli.security_metrics(last)

    def security_audit_prompt(self) -> None:
        trace = messagebox.askyesno("Security Audit", "Vollständigen Audit-Trace ausgeben?")
        self.cli.security_audit(trace)

    def repo_architect_prompt(self) -> None:
        sec = messagebox.askyesno("Repo Architect", "Sicherheitsfokus aktivieren?")
        compliance = simple_input(self.root, "Repo Architect", "Compliance-Standard (optional):") or None
        self.cli.github_repo_architect_optimize(sec, compliance)

    def github_repo_analyze_prompt(self) -> None:
        analysis = simple_input(self.root, "Repo Analyze", "Analyseart (optional):") or None
        target = simple_input(self.root, "Repo Analyze", "Ziel (optional):") or None
        self.cli.github_repo_analyze(analysis, target)

    def github_pr_manage_prompt(self) -> None:
        reviewers = simple_input(self.root, "PR Manage", "Reviewer (kommagetrennt, optional):") or None
        ai = messagebox.askyesno("PR Manage", "AI-Unterstützung aktivieren?")
        self.cli.github_pr_manage(reviewers, ai)

    def github_issue_prompt(self) -> None:
        proj = simple_input(self.root, "Issue Track", "Projektname (optional):") or None
        self.cli.github_issue_track(proj)

    def github_release_prompt(self) -> None:
        version = simple_input(self.root, "Release", "Versionsnummer:") or "1.0.0"
        auto = messagebox.askyesno("Release", "Auto-Changelog erstellen?")
        self.cli.github_release_coord(version, auto)

    def github_workflow_prompt(self) -> None:
        file = simple_input(self.root, "Workflow Auto", "Workflow-Datei:") or ""
        self.cli.github_workflow_auto(file)

    def github_code_review_prompt(self) -> None:
        multi = messagebox.askyesno("Code Review", "Mehrere Reviewer?")
        ai = messagebox.askyesno("Code Review", "AI-Unterstützung aktivieren?")
        self.cli.github_code_review(multi, ai)

    def github_sync_coord_prompt(self) -> None:
        multi = messagebox.askyesno("Sync Coordinator", "Multi-Package Synchronisation?")
        self.cli.github_sync_coordinator(multi)

    def workflow_create_prompt(self) -> None:
        name = simple_input(self.root, "Workflow Create", "Name:") or ""
        parallel = messagebox.askyesno("Workflow Create", "Parallel ausführen?")
        self.cli.workflow_create(name, parallel)

    def workflow_execute_prompt(self) -> None:
        name = simple_input(self.root, "Workflow Execute", "Name:") or ""
        self.cli.workflow_execute(name)

    def workflow_export_prompt(self) -> None:
        name = simple_input(self.root, "Workflow Export", "Name:") or ""
        outfile = simple_input(self.root, "Workflow Export", "Ausgabedatei:") or "workflow.json"
        self.cli.workflow_export(name, outfile)

    def pipeline_create_prompt(self) -> None:
        config = simple_input(self.root, "Pipeline Create", "Konfigurationsdatei:") or ""
        self.cli.pipeline_create(config)

    def scheduler_manage_prompt(self) -> None:
        sched = simple_input(self.root, "Scheduler Manage", "Schedulername:") or ""
        action = simple_input(self.root, "Scheduler Manage", "Aktion (start, stop, status):") or ""
        self.cli.scheduler_manage(sched, action)

    def trigger_setup_prompt(self) -> None:
        name = simple_input(self.root, "Trigger Setup", "Trigger-Name:") or ""
        target = simple_input(self.root, "Trigger Setup", "Ziel oder Datei:") or ""
        self.cli.trigger_setup(name, target)

    def batch_process_prompt(self) -> None:
        items = simple_input(self.root, "Batch Process", "Items (kommagetrennt):") or ""
        concurrent = messagebox.askyesno("Batch Process", "Parallel?")
        self.cli.batch_process(items, concurrent)

    def parallel_execute_prompt(self) -> None:
        tasks = simple_input(self.root, "Parallel Execute", "Tasks (kommagetrennt):") or ""
        self.cli.parallel_execute(tasks)

    def daa_agent_create_prompt(self) -> None:
        agent_type = simple_input(self.root, "Agent Create", "Agententyp:") or ""
        caps = simple_input(self.root, "Agent Create", "Fähigkeiten (JSON oder Liste):") or "[]"
        resources = simple_input(self.root, "Agent Create", "Ressourcen (JSON):") or "{}"
        sec_level = simple_input(self.root, "Agent Create", "Sicherheitsstufe (optional):")
        sandbox = messagebox.askyesno("Agent Create", "Sandbox aktivieren?")
        self.cli.daa_agent_create(agent_type, caps, resources, sec_level if sec_level else None, sandbox)

    def daa_capability_prompt(self) -> None:
        req = simple_input(self.root, "Capability Match", "Task-Anforderungen (JSON-Liste):") or "[]"
        self.cli.daa_capability_match(req)

    def daa_lifecycle_prompt(self) -> None:
        agent_id = simple_input(self.root, "Lifecycle Manage", "Agent-ID:") or ""
        action = simple_input(self.root, "Lifecycle Manage", "Aktion:") or ""
        self.cli.daa_lifecycle_manage(agent_id, action)

    def daa_resource_prompt(self) -> None:
        agent_id = simple_input(self.root, "Resource Allocation", "Agent-ID:") or ""
        cpu = simple_input(self.root, "Resource Allocation", "CPU-Limit:") or ""
        memory = simple_input(self.root, "Resource Allocation", "Memory-Limit:") or ""
        self.cli.daa_resource_alloc(agent_id, cpu, memory)

    def daa_communication_prompt(self) -> None:
        src = simple_input(self.root, "Communication", "Quelle:") or ""
        tgt = simple_input(self.root, "Communication", "Ziel:") or ""
        msg = simple_input(self.root, "Communication", "Nachricht:") or ""
        self.cli.daa_communication(src, tgt, msg)

    def daa_consensus_prompt(self) -> None:
        proposal = simple_input(self.root, "Consensus", "Vorschlag:") or ""
        self.cli.daa_consensus(proposal)

    def config_manage_prompt(self) -> None:
        operation = simple_input(self.root, "Config Manage", "Operation (read, write, delete):") or ""
        file = simple_input(self.root, "Config Manage", "Datei (optional):")
        self.cli.config_manage(operation, file if file else None)

    def log_analysis_prompt(self) -> None:
        logfile = simple_input(self.root, "Log Analysis", "Logdatei:") or ""
        self.cli.log_analysis(logfile)

    def swarm_init_prompt(self) -> None:
        desc = simple_input(self.root, "Swarm Init", "Beschreibung (optional):")
        self.cli.swarm_init(desc if desc else None)

    def agent_spawn_prompt(self) -> None:
        agent_type = simple_input(self.root, "Agent Spawn", "Agententyp:") or ""
        caps = simple_input(self.root, "Agent Spawn", "Fähigkeiten (JSON oder Liste):") or "[]"
        resources = simple_input(self.root, "Agent Spawn", "Ressourcen (JSON):") or "{}"
        self.cli.agent_spawn(agent_type, caps, resources)

    def task_orchestrate_prompt(self) -> None:
        desc = simple_input(self.root, "Task Orchestrate", "Aufgabenbeschreibung:") or ""
        self.cli.task_orchestrate(desc)

    def swarm_monitor_prompt(self) -> None:
        dashboard = messagebox.askyesno("Swarm Monitor", "Dashboard anzeigen?")
        realtime = messagebox.askyesno("Swarm Monitor", "Echtzeit-Monitoring?")
        self.cli.swarm_monitor(dashboard, realtime)

    def swarm_scale_prompt(self) -> None:
        scale = simple_input(self.root, "Swarm Scale", "Skalierung (z. B. up, down, 2x):") or ""
        self.cli.swarm_scale(scale)

    def sparc_batch_prompt(self) -> None:
        modes = simple_input(self.root, "SPARC Batch", "Modi (kommagetrennt):") or ""
        task = simple_input(self.root, "SPARC Batch", "Aufgabe:") or ""
        self.cli.sparc_batch(modes, task)

    def sparc_pipeline_prompt(self) -> None:
        task = simple_input(self.root, "SPARC Pipeline", "Aufgabe:") or ""
        self.cli.sparc_pipeline(task)

    def sparc_concurrent_prompt(self) -> None:
        mode = simple_input(self.root, "SPARC Concurrent", "Modus:") or ""
        tasks_file = simple_input(self.root, "SPARC Concurrent", "Aufgabendatei:") or ""
        self.cli.sparc_concurrent(mode, tasks_file)

    def spawn_pattern(self, pattern: str, agents: str) -> None:
        self.cli.hive_spawn(f"{pattern} pattern", namespace=None, agents=agents, temp=False)

    def custom_pattern_prompt(self) -> None:
        desc = simple_input(self.root, "Custom Pattern", "Beschreibung des Hives:") or ""
        ns = simple_input(self.root, "Custom Pattern", "Namespace (optional):")
        agents = simple_input(self.root, "Custom Pattern", "Agenten (Zahl oder Liste):")
        self.cli.hive_spawn(desc, namespace=ns if ns else None, agents=agents if agents else None, temp=False)


def simple_input(root: tk.Tk, title: str, prompt: str) -> Optional[str]:
    """Öffnet ein kleines Eingabefenster für eine Textzeile."""
    input_win = tk.Toplevel(root)
    input_win.title(title)
    ttk.Label(input_win, text=prompt).grid(row=0, column=0, padx=5, pady=5)
    entry = ttk.Entry(input_win, width=50)
    entry.grid(row=1, column=0, padx=5, pady=5)
    value: List[str] = []
    def submit() -> None:
        value.append(entry.get())
        input_win.destroy()
    ttk.Button(input_win, text="OK", command=submit).grid(row=2, column=0, pady=5)
    input_win.grab_set()
    root.wait_window(input_win)
    return value[0] if value else None


def simple_choice(root: tk.Tk, title: str, prompt: str, options: List[str]) -> Optional[str]:
    """Zeigt eine Liste von Optionen an und gibt die gewählte zurück."""
    choice_win = tk.Toplevel(root)
    choice_win.title(title)
    ttk.Label(choice_win, text=prompt).grid(row=0, column=0, padx=5, pady=5)
    var = tk.StringVar(value=options)
    listbox = tk.Listbox(choice_win, listvariable=var, height=min(len(options), 10))
    listbox.grid(row=1, column=0, padx=5, pady=5)
    selected: List[str] = []
    def choose() -> None:
        try:
            idx = listbox.curselection()[0]
            selected.append(options[idx])
        except Exception:
            pass
        choice_win.destroy()
    ttk.Button(choice_win, text="OK", command=choose).grid(row=2, column=0, pady=5)
    choice_win.grab_set()
    root.wait_window(choice_win)
    return selected[0] if selected else None


if __name__ == "__main__":
    app = GUIFlowApp()
    app.run()