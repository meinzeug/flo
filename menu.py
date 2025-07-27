from __future__ import annotations
from pathlib import Path
from typing import Dict, List, Optional
from project_manager import ProjectManager
from claude_flow_cli import ClaudeFlowCLI

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





__all__ = ["ProjectManagerMenu", "MonitoringDashboard", "QueenChat"]
