import os
import subprocess
from pathlib import Path
from typing import List


class SetupManager:
    """Übernimmt die Einrichtung der Umgebung und lädt Tokens."""

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
        cls._run_command(["sudo", "apt-get", "update", "-y"])
        cls._run_command(["sudo", "apt-get", "install", "-y", "nodejs", "npm"])

    @classmethod
    def install_claude_code(cls) -> None:
        """Installiert @anthropic-ai/claude-code global via npm."""
        print("[Setup] Installiere @anthropic-ai/claude-code global …")
        cls._run_command(["sudo", "npm", "install", "-g", "@anthropic-ai/claude-code"])
        cls._run_command(["claude", "--dangerously-skip-permissions"])

    @classmethod
    def install_claude_flow(cls) -> None:
        """Installiert claude-flow@alpha global via npm."""
        print("[Setup] Installiere claude-flow@alpha global …")
        cls._run_command(["sudo", "npm", "install", "-g", "claude-flow@alpha"])

    @classmethod
    def setup_environment(cls) -> None:
        """Prüft die Verfügbarkeit von node, npm, claude und claude-flow."""
        if not cls._command_exists("node") or not cls._command_exists("npm"):
            cls.install_node_and_npm()
        else:
            print("[Setup] Node.js und npm sind vorhanden.")

        if cls._command_exists("claude"):
            print("[Setup] 'claude' ist vorhanden.")
        else:
            cls.install_claude_code()

        # Vermeide potenziell lange Netzwerkaufrufe durch npx. Stattdessen
        # wird lediglich geprüft, ob das Kommando ``claude-flow`` bereits im
        # PATH vorhanden ist. Damit startet die Anwendung auch in Umgebungen
        # ohne npm oder ohne Internetzugang schnell.
        if cls._command_exists("claude-flow"):
            print("[Setup] claude-flow ist vorhanden.")
        else:
            print(
                "[Setup] Warnung: 'claude-flow' scheint nicht installiert zu sein."
                " Einige Funktionen stehen möglicherweise nicht zur Verfügung."
            )

        if not cls._command_exists("claude"):
            print(
                "[Setup] Warnung: Das Kommando 'claude' ist nach der Installation nicht auffindbar."
                " Bitte stellen Sie sicher, dass @anthropic-ai/claude-code korrekt installiert ist."
            )
        # Keine weitere Verifikation per ``npx`` um Wartezeiten zu vermeiden.
        cls.load_env_tokens()

    @classmethod
    def load_env_tokens(cls) -> None:
        """Lädt Tokens aus einer .env-Datei und setzt ein Standardmodell."""
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
                        if key and value and key not in os.environ:
                            os.environ[key] = value
                            print(f"[Setup] Setze Umgebungsvariable {key} aus .env")
        if "GIT_TOKEN" not in os.environ:
            print("[Setup] Warnung: GitHub‑Token nicht gesetzt. Bitte setzen Sie GIT_TOKEN in Ihrer .env oder als Umgebungsvariable.")
        if "OPENROUTER_TOKEN" not in os.environ:
            print("[Setup] Warnung: OpenRouter‑Token nicht gesetzt. Bitte setzen Sie OPENROUTER_TOKEN in Ihrer .env oder als Umgebungsvariable.")
        if "OPENROUTER_MODEL" not in os.environ:
            os.environ["OPENROUTER_MODEL"] = "qwen/qwen3-coder:free"
            print("[Setup] Setze OPENROUTER_MODEL=qwen/qwen3-coder:free")

__all__ = ["SetupManager"]
