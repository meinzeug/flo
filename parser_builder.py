import argparse
from typing import List, Optional

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



__all__ = ["build_parser"]
