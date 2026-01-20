#!/usr/bin/env python3
"""
Agent configuration and detection module.
Manages different AI agent skill directory configurations.
"""

from pathlib import Path

# Agent configuration mapping
# Each agent has a name, project-level path, and global path
AGENTS = {
    "opencode": {
        "name": "OpenCode",
        "project": ".opencode/skills/",
        "global": "~/.config/opencode/skills/",
    },
    "claude-code": {
        "name": "Claude Code",
        "project": ".claude/skills/",
        "global": "~/.claude/skills/",
    },
    "codex": {
        "name": "Codex",
        "project": ".codex/skills/",
        "global": "~/.codex/skills/",
    },
    "cursor": {
        "name": "Cursor",
        "project": ".cursor/skills/",
        "global": "~/.cursor/skills/",
    },
    "amp": {
        "name": "Amp",
        "project": ".agents/skills/",
        "global": "~/.config/agents/skills/",
    },
    "kilo": {
        "name": "Kilo Code",
        "project": ".kilocode/skills/",
        "global": "~/.kilocode/skills/",
    },
    "roo": {
        "name": "Roo Code",
        "project": ".roo/skills/",
        "global": "~/.roo/skills/",
    },
    "goose": {
        "name": "Goose",
        "project": ".goose/skills/",
        "global": "~/.config/goose/skills/",
    },
    "gemini-cli": {
        "name": "Gemini CLI",
        "project": ".gemini/skills/",
        "global": "~/.gemini/skills/",
    },
    "antigravity": {
        "name": "Antigravity",
        "project": ".agent/skills/",
        "global": "~/.gemini/antigravity/skills/",
    },
    "github-copilot": {
        "name": "GitHub Copilot",
        "project": ".github/skills/",
        "global": "~/.copilot/skills/",
    },
    "clawdbot": {
        "name": "Clawdbot",
        "project": "skills/",
        "global": "~/.clawdbot/skills/",
    },
    "droid": {
        "name": "Droid",
        "project": ".factory/skills/",
        "global": "~/.factory/skills/",
    },
    "windsurf": {
        "name": "Windsurf",
        "project": ".windsurf/skills/",
        "global": "~/.codeium/windsurf/skills/",
    },
}


def detect_existing_agents() -> dict[str, Path]:
    """
    Detect which agents are installed on the system.

    Returns:
        Dictionary mapping agent IDs to their global paths for installed agents.
    """
    existing = {}
    for agent_id, info in AGENTS.items():
        global_path = Path(info["global"]).expanduser()
        if global_path.exists():
            existing[agent_id] = global_path
    return existing


def get_agent_path(agent_id: str, deployment_type: str = "global", project_root: Path | None = None) -> Path:
    """
    Get the target path for an agent.

    Args:
        agent_id: The agent identifier
        deployment_type: Either "global" or "project"
        project_root: The project root directory (required for project deployment)

    Returns:
        The target path for the agent
    """
    if agent_id not in AGENTS:
        raise ValueError(f"Unknown agent: {agent_id}")

    info = AGENTS[agent_id]

    if deployment_type == "global":
        return Path(info["global"]).expanduser()
    else:
        if project_root is None:
            project_root = Path.cwd()
        return project_root / info["project"]


def get_agent_name(agent_id: str) -> str:
    """
    Get the display name for an agent.

    Args:
        agent_id: The agent identifier

    Returns:
        The agent's display name
    """
    if agent_id not in AGENTS:
        raise ValueError(f"Unknown agent: {agent_id}")
    return AGENTS[agent_id]["name"]
