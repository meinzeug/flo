#!/usr/bin/env python3
"""Flow TUI launcher.

This script starts a text user interface (TUI) for the Flow automation tools.
It keeps the legacy CLI as a fallback when arguments are provided.
"""

from __future__ import annotations

import io
import sys
import threading
import itertools
import time
import os

import subprocess


def ensure_package(pkg_name: str) -> None:
    """Import ``pkg_name`` and install via pip if missing."""
    try:
        __import__(pkg_name)
    except ModuleNotFoundError:
        print(f"\U0001F4E6 Package '{pkg_name}' not found. Installing…")
        subprocess.check_call([sys.executable, "-m", "pip", "install", pkg_name])
        print(f"\u2714 Installed '{pkg_name}'")
        globals()[pkg_name] = __import__(pkg_name)


# Fallback for prompt_toolkit in minimal environments
ensure_package("prompt_toolkit")

from contextlib import redirect_stdout
from pathlib import Path
from typing import List, Optional

from prompt_toolkit.application import Application, run_in_terminal
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import Layout, HSplit, VSplit
from prompt_toolkit.shortcuts import (
    input_dialog,
    message_dialog,
    radiolist_dialog,
)
from prompt_toolkit.widgets import TextArea, RadioList, Frame, Box

from setup_manager import SetupManager
from claude_flow_cli import ClaudeFlowCLI
from project_manager import ProjectManager
from menu import ProjectManagerMenu, MonitoringDashboard


class ProjectManagerTUI:
    """Minimal prompt_toolkit based menu for :class:`ProjectManager`."""

    def __init__(self, pm: ProjectManager) -> None:
        self.pm = pm
        self.quick_commands: dict[str, list[str]] = {}

    def run(self) -> None:
        while True:
            choice = radiolist_dialog(
                title="Project Manager",
                text="Choose an action",
                values=[
                    ("create", "Create project"),
                    ("list", "List projects"),
                    ("monitor", "Monitor & heal"),
                    ("config", "Configure tokens"),
                    ("quick", "Quick commands"),
                    ("back", "Back"),
                ],
            ).run()
            if choice == "create":
                idea = input_dialog(title="New Project", text="Describe your idea:").run()
                if not idea:
                    continue
                template = input_dialog(title="Template", text="Template (optional):").run()
                self.pm.create_project(idea, template or None)
            elif choice == "list":
                projects = sorted(p.name for p in self.pm.base_dir.glob("*") if p.is_dir())
                msg = "No projects found" if not projects else "\n".join(projects)
                message_dialog(title="Projects", text=msg).run()
            elif choice == "monitor":
                session = input_dialog(title="Monitor", text="Session ID:").run()
                if session:
                    self.pm.monitor_and_self_heal(session)
            elif choice == "config":
                self.configure_tokens()
            elif choice == "quick":
                self.manage_quick_commands()
            else:
                break

    def configure_tokens(self) -> None:
        """Configure API tokens and model via dialog."""
        git_token = input_dialog(title="GitHub token", text="GIT_TOKEN:").run()
        open_token = input_dialog(title="OpenRouter token", text="OPENROUTER_TOKEN:").run()
        model = input_dialog(
            title="OpenRouter model",
            text=f"OPENROUTER_MODEL ({os.environ.get('OPENROUTER_MODEL','qwen/qwen3-coder:free')}):",
        ).run()
        if git_token:
            os.environ["GIT_TOKEN"] = git_token
        if open_token:
            os.environ["OPENROUTER_TOKEN"] = open_token
        if model:
            os.environ["OPENROUTER_MODEL"] = model
        with open(".env", "w", encoding="utf-8") as f:
            if os.environ.get("GIT_TOKEN"):
                f.write(f"GIT_TOKEN={os.environ['GIT_TOKEN']}\n")
            if os.environ.get("OPENROUTER_TOKEN"):
                f.write(f"OPENROUTER_TOKEN={os.environ['OPENROUTER_TOKEN']}\n")
            if os.environ.get("OPENROUTER_MODEL"):
                f.write(f"OPENROUTER_MODEL={os.environ['OPENROUTER_MODEL']}\n")
        message_dialog(title="Config", text="Tokens saved").run()

    def manage_quick_commands(self) -> None:
        """Simple management of quick commands."""
        while True:
            choice = radiolist_dialog(
                title="Quick Commands",
                text="Choose action",
                values=[
                    ("run", "Run command"),
                    ("add", "Add command"),
                    ("list", "List commands"),
                    ("delete", "Delete command"),
                    ("back", "Back"),
                ],
            ).run()
            if choice == "run":
                if not self.quick_commands:
                    message_dialog(title="Quick", text="No commands").run()
                    continue
                items = [(name, name) for name in self.quick_commands.keys()]
                sel = radiolist_dialog(title="Run Quick", text="Select", values=items).run()
                if sel:
                    args = self.quick_commands[sel]
                    self.pm.cli._run(args)
            elif choice == "add":
                name = input_dialog(title="Add Quick", text="Name:").run()
                cmd = input_dialog(title="Add Quick", text="Args:").run()
                if name and cmd:
                    self.quick_commands[name] = cmd.split()
            elif choice == "list":
                if not self.quick_commands:
                    msg = "No commands"
                else:
                    msg = "\n".join(f"{k}: {' '.join(v)}" for k, v in self.quick_commands.items())
                message_dialog(title="Commands", text=msg).run()
            elif choice == "delete":
                if not self.quick_commands:
                    message_dialog(title="Quick", text="No commands").run()
                    continue
                items = [(name, name) for name in self.quick_commands.keys()]
                sel = radiolist_dialog(title="Delete Quick", text="Select", values=items).run()
                if sel and sel in self.quick_commands:
                    del self.quick_commands[sel]
            else:
                break

from parser_builder import build_parser


class FloTUI:
    """Simple TUI wrapper around :class:`ProjectManager` and :class:`ClaudeFlowCLI`."""

    def __init__(self) -> None:
        SetupManager.setup_environment()
        self.cli = ClaudeFlowCLI(Path.cwd())
        self.pm = ProjectManager(Path("projects").resolve(), self.cli)

        self.header = TextArea(
            text=" Flo TUI - use arrow keys, F1 for help ",
            height=1,
            style="reverse",
            focusable=False,
        )
        self.output = TextArea(style="class:output", scrollbar=True, focusable=True)
        self.status = TextArea(height=1, text="Ready", style="reverse")

        kb = KeyBindings()

        @kb.add("c-c")
        @kb.add("c-q")
        def _(event) -> None:
            event.app.exit()

        @kb.add("f10")
        def _(event) -> None:
            """Exit application with F10."""
            event.app.exit()

        @kb.add("f1")
        def _(event) -> None:
            """Show help dialog."""
            self.show_help()

        @kb.add("escape")
        def _(event) -> None:
            event.app.exit()

        self.menu = RadioList(
            [
                ("projects", "Projects"),
                ("hive", "Hive"),
                ("monitor", "Monitoring"),
                ("tokens", "Token Setup"),
                ("advanced", "Advanced"),
                ("about", "About"),
                ("exit", "Exit"),
            ]
        )

        @kb.add("enter")
        def _(event) -> None:
            self.handle_choice(self.menu.current_value)

        menu_frame = Frame(self.menu, title="Menu", width=24)
        body = VSplit([
            menu_frame,
            Box(self.output, padding=1, style="class:output"),
        ])
        layout = Layout(HSplit([self.header, body, self.status]))

        self.app = Application(layout=layout, full_screen=True, key_bindings=kb)

    # ------------------------------------------------------------------
    # Utility helpers
    def _run_task(self, func, *args) -> None:
        """Execute a function in a background thread and display its output."""
        stop = threading.Event()

        def spinner() -> None:
            symbols = "|/-\\"
            i = 0
            pct = 0
            while not stop.is_set():
                self.status.text = f"Working {symbols[i % len(symbols)]} {pct}%"
                self.app.invalidate()
                time.sleep(0.1)
                i += 1
                pct = (pct + 2) % 100
            self.status.text = "Ready"
            self.app.invalidate()

        def worker() -> None:
            buf = io.StringIO()
            with redirect_stdout(buf):
                try:
                    func(*args)
                except Exception as exc:  # pragma: no cover - runtime feedback only
                    print(f"[Error] {exc}")
            text = buf.getvalue()
            def update() -> None:
                self.output.buffer.insert_text(text)
                # Scroll to bottom so the newest output is visible
                self.output.buffer.cursor_position = len(self.output.buffer.text)
            self.app.call_from_executor(update)
            stop.set()

        threading.Thread(target=spinner, daemon=True).start()
        threading.Thread(target=worker, daemon=True).start()

    def _info(self, text: str) -> None:
        self.status.text = text
        self.app.invalidate()

    def configure_tokens(self) -> None:
        """Configure API tokens and model via dialog."""
        git_token = input_dialog(title="GitHub token", text="GIT_TOKEN:").run()
        open_token = input_dialog(title="OpenRouter token", text="OPENROUTER_TOKEN:").run()
        model = input_dialog(
            title="OpenRouter model",
            text=f"OPENROUTER_MODEL ({os.environ.get('OPENROUTER_MODEL','qwen/qwen3-coder:free')}):",
        ).run()
        if git_token:
            os.environ["GIT_TOKEN"] = git_token
        if open_token:
            os.environ["OPENROUTER_TOKEN"] = open_token
        if model:
            os.environ["OPENROUTER_MODEL"] = model
        with open(".env", "w", encoding="utf-8") as f:
            if os.environ.get("GIT_TOKEN"):
                f.write(f"GIT_TOKEN={os.environ['GIT_TOKEN']}\n")
            if os.environ.get("OPENROUTER_TOKEN"):
                f.write(f"OPENROUTER_TOKEN={os.environ['OPENROUTER_TOKEN']}\n")
            if os.environ.get("OPENROUTER_MODEL"):
                f.write(f"OPENROUTER_MODEL={os.environ['OPENROUTER_MODEL']}\n")
        message_dialog(title="Config", text="Tokens saved").run()

    def show_monitoring(self) -> None:
        """Open MonitoringDashboard in terminal."""
        def _open() -> None:
            MonitoringDashboard(self.cli).show()

        run_in_terminal(_open)

    def handle_choice(self, choice: str | None) -> None:
        if choice == "projects":
            self.projects_menu()
        elif choice == "hive":
            self.hive_menu()
        elif choice == "monitor":
            self.show_monitoring()
        elif choice == "tokens":
            self.configure_tokens()
        elif choice == "advanced":
            self.launch_manager_menu()
        elif choice == "about":
            self.show_about()
        else:
            self.app.exit()

    # ------------------------------------------------------------------
    # Menu handlers
    def create_project(self) -> None:
        idea = input_dialog(title="New Project", text="Describe your idea:").run()
        if not idea:
            return
        template = input_dialog(title="Template", text="Template (optional):").run()
        self._info("Creating project ...")
        self._run_task(self.pm.create_project, idea, template or None)

    def list_projects(self) -> None:
        projects = sorted(p.name for p in self.pm.base_dir.glob("*") if p.is_dir())
        if not projects:
            message_dialog(title="Projects", text="No projects found").run()
        else:
            message_dialog(title="Projects", text="\n".join(projects)).run()

    def spawn_hive(self) -> None:
        desc = input_dialog(title="Hive Spawn", text="Description:").run()
        if desc:
            self._info("Spawning hive ...")
            self._run_task(self.cli.hive_spawn, desc)

    def hive_status(self) -> None:
        self._info("Retrieving status ...")
        self._run_task(self.cli.hive_status)

    def hive_sessions(self) -> None:
        self._info("Listing sessions ...")
        self._run_task(self.cli.hive_sessions)

    # ------------------------------------------------------------------
    # Sub menus
    def projects_menu(self) -> None:
        while True:
            choice = radiolist_dialog(
                title="Projects",
                text="Choose an action",
                values=[
                    ("create", "Create project"),
                    ("list", "List projects"),
                    ("monitor", "Monitor & heal"),
                    ("back", "Back"),
                ],
            ).run()
            if choice == "create":
                self.create_project()
            elif choice == "list":
                self.list_projects()
            elif choice == "monitor":
                session = input_dialog(title="Monitor", text="Session ID:").run()
                if session:
                    self._info("Monitoring ...")
                    self._run_task(self.pm.monitor_and_self_heal, session)
            else:
                break

    def hive_menu(self) -> None:
        while True:
            choice = radiolist_dialog(
                title="Hive",
                text="Choose an action",
                values=[
                    ("spawn", "Spawn hive"),
                    ("status", "Hive status"),
                    ("sessions", "Hive sessions"),
                    ("back", "Back"),
                ],
            ).run()
            if choice == "spawn":
                self.spawn_hive()
            elif choice == "status":
                self.hive_status()
            elif choice == "sessions":
                self.hive_sessions()
            else:
                break

    def launch_manager_menu(self) -> None:
        """Open the project manager menu inside the TUI."""

        def _open() -> None:
            ProjectManagerTUI(self.pm).run()

        run_in_terminal(_open)

    def show_help(self) -> None:
        """Display a help dialog with keyboard shortcuts."""
        message = (
            "Shortcuts:\n"
            "  ↑/↓ - Navigate menu\n"
            "  Enter - Select option\n"
            "  Esc/F10 - Quit\n"
            "  F1 - This help dialog"
        )
        message_dialog(title="Help", text=message).run()

    def show_about(self) -> None:
        """Display information about the TUI."""
        message = (
            "Flo TUI\n\n"
            "A simple terminal user interface for controlling Claude-Flow."
        )
        message_dialog(title="About Flo", text=message).run()

    def run(self) -> None:
        self.app.run()


# ----------------------------------------------------------------------
# Legacy CLI fallback

def run_cli(argv: Optional[List[str]] = None) -> None:
    SetupManager.setup_environment()
    parser = build_parser()
    args = parser.parse_args(argv)
    if not args.command:
        parser.print_help()
        return

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
        cli.daa_agent_create(
            args.agent_type,
            args.capabilities,
            args.resources,
            args.security_level,
            args.sandbox,
        )
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
        cli.run_background(args.cli_args)
    elif cmd == "sparc-full":
        cli.sparc_full_workflow(args.feature)
    elif cmd == "new-project":
        base_dir = Path(args.base_dir).expanduser().resolve()
        pm = ProjectManager(base_dir, cli)
        pm.create_project(args.idea, template=args.template)
    elif cmd == "manager":
        base_dir = Path("projects").expanduser().resolve()
        pm = ProjectManager(base_dir, cli)
        menu = ProjectManagerMenu(pm)
        menu.run()
    else:
        parser.print_help()


# ----------------------------------------------------------------------

def main(argv: Optional[List[str]] | None = None) -> None:
    if argv:
        run_cli(argv)
    elif len(sys.argv) > 1:
        run_cli(sys.argv[1:])
    else:
        FloTUI().run()


if __name__ == "__main__":
    main()
