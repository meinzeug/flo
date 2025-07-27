### 2025-07-28 Setup updates
- Extended SetupManager to log to flow_autogen.log.
- Added checks for claude-flow version, screen command, and missing .env.
- Each step now uses _log helper for unified output.
### 2025-07-29 TUI scroll fix
- _run_task now moves cursor to the end after inserting text so new log output
  is immediately visible in the FloTUI window.
### 2025-07-30 FloTUI menu update
- Added MonitoringDashboard and token setup as dedicated options in the main
  menu.
- Implemented `configure_tokens` and `show_monitoring` methods in run_flo.py.
- Main menu now lists Projects, Hive, Monitoring, Token Setup, Advanced, About
  and Exit.
### 2025-07-27 Auto dependency install
- New ensure_package helper installs missing packages at runtime.

### 2025-07-27 Dependency fix
- Added requirements.txt to document prompt_toolkit dependency after start failure.

### 2025-07-27 TUI additions
- ProjectManagerTUI kann jetzt Tokens konfigurieren und Quick Commands verwalten.

# Brain notes
## Plan
- Split run_flo.py (2647 lines) into modules.
- Modules:
  - setup_manager.py -> SetupManager
  - openrouter_client.py -> OpenRouterClient
  - claude_flow_cli.py -> ClaudeFlowCLI
  - project_manager.py -> ProjectManager
  - menu.py -> ProjectManagerMenu, MonitoringDashboard, QueenChat
  - parser_builder.py -> build_parser
- run_flo.py will import from these modules and define main function.
- Add __all__ as needed.
- Add .gitignore to ignore .env, .venv, package.json etc not tracked.

## Implemented Modules
- setup_manager.py
- openrouter_client.py
- claude_flow_cli.py
- project_manager.py
- menu.py
- parser_builder.py
- run_flo.py now imports these.
- Added .gitignore for untracked files.
\n### 2025-07-27 Debugging\n- Modified SetupManager.setup_environment to set npm_config_yes and timeout to avoid interactive npx hang.\n- Updated .gitignore to exclude __pycache__.\n
- Added timeout and npm_config_yes handling in CLI _run to prevent hang when npx prompts.
\n### 2025-07-27 Further fixes
- SetupManager.skip verifying claude-flow with npx to avoid lengthy install
  checks; now only check if command exists.
- OpenRouterClient timeout reduced to 5s and handles RequestException for
  better failure handling in restricted environments.

### 2025-07-27 Argument parser fix
- Removed required=True from parser subcommands.
- Added check in run_flo.main to print help when no command provided.
- Now running "python3 run_flo.py" shows help instead of error.
\n### Fix openrouter timeout\n- Modified openrouter_client.generate_document to stream response with 10s timeout and return placeholder text on failure.
\n### 2025-07-27 Run test\n- Executed run_flo.py and tested ProjectManager menu.\n- Network requests to openrouter timed out; placeholder text used.\n- No Python errors during startup or menu operations.\n
\n### 2025-07-27 TUI redesign\n- Replaced CLI entry in run_flo.py with a prompt_toolkit TUI (FloTUI).\n- Legacy CLI preserved when arguments are supplied.\n- Added basic menus for Project and Hive actions using arrow navigation.\n- Commands run in background threads and output captured to a scrollable text area.

### 2025-07-27 TUI enhancements
- Added header and ESC key for quitting.
- Integrated ProjectManagerMenu via "Advanced" menu using run_in_terminal.
- Added basic status bar.
\n### 2025-07-27 More TUI updates\n- Implemented ProjectManagerTUI using prompt_toolkit dialogs.\n- launch_manager_menu now opens this dialog instead of the old CLI menu.\n
\n### 2025-07-27 TUI layout update\n- Replaced menubar with vertical RadioList menu.\n- Added Frame and Box layout with header, menu pane, output pane, and status bar.\n- ESC or Ctrl+C quits, Enter selects menu item.\n- run_flo.py compiles and CLI fallback unaffected.\n
### 2025-07-27 Structured TUI menus
- Replaced main menu options with categories Projects, Hive, Advanced, Exit.
- Added projects_menu and hive_menu subdialogs using radiolist_dialog.
- Each action triggers create/list/monitor or spawn/status/sessions.
- Updated brain.md with new section.
\n### 2025-07-27 Final tweaks\n- Added "About" option to main menu with info dialog.\n- Updated handle_choice and new show_about method.\n
\n### 2025-07-27 Help and spinner\n- Added F1 help dialog and F10 exit shortcut in FloTUI.\n- Implemented spinner in _run_task to show activity.\n- Header now mentions F1 help.
\n### 2025-07-27 Spinner progress\n- Updated spinner in _run_task to display a pseudo percentage progress.
