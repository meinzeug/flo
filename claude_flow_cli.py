import os
import subprocess
from pathlib import Path
from typing import List, Optional

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
        env = os.environ.copy()
        env.setdefault("npm_config_yes", "true")
        try:
            # Führe den Befehl aus und speichere die Argumentliste in der Historie
            subprocess.run(cmd, cwd=self.working_dir, env=env, timeout=15)
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
        env.setdefault("npm_config_yes", "true")
        try:
            result = subprocess.run(
                cmd,
                cwd=self.working_dir,
                env=env,
                capture_output=True,
                text=True,
                timeout=15,
            )
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

__all__ = ["ClaudeFlowCLI"]
