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
