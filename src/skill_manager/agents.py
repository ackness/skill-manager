#!/usr/bin/env python3
"""
Agent configuration and detection module.
Manages different AI agent skill directory configurations.
"""

from pathlib import Path

# Agent configuration mapping
# Each agent has a name, project-level path, and global path
# Note: global=None means project-only (no global installation supported)
AGENTS = {
    # Amp, Kimi Code CLI
    "amp": {
        "name": "Amp",
        "project": ".agents/skills/",
        "global": "~/.config/agents/skills/",
    },
    "kimi-cli": {
        "name": "Kimi Code CLI",
        "project": ".agents/skills/",
        "global": "~/.config/agents/skills/",
    },
    # Antigravity
    "antigravity": {
        "name": "Antigravity",
        "project": ".agent/skills/",
        "global": "~/.gemini/antigravity/skills/",
    },
    # Augment
    "augment": {
        "name": "Augment",
        "project": ".augment/rules/",
        "global": "~/.augment/rules/",
    },
    # Claude Code
    "claude-code": {
        "name": "Claude Code",
        "project": ".claude/skills/",
        "global": "~/.claude/skills/",
    },
    # OpenClaw
    "openclaw": {
        "name": "OpenClaw",
        "project": "skills/",
        "global": "~/.moltbot/skills/",
    },
    # Cline
    "cline": {
        "name": "Cline",
        "project": ".cline/skills/",
        "global": "~/.cline/skills/",
    },
    # CodeBuddy
    "codebuddy": {
        "name": "CodeBuddy",
        "project": ".codebuddy/skills/",
        "global": "~/.codebuddy/skills/",
    },
    # Codex
    "codex": {
        "name": "Codex",
        "project": ".agents/skills/",
        "global": "~/.codex/skills/",
    },
    # Command Code
    "command-code": {
        "name": "Command Code",
        "project": ".commandcode/skills/",
        "global": "~/.commandcode/skills/",
    },
    # Continue
    "continue": {
        "name": "Continue",
        "project": ".continue/skills/",
        "global": "~/.continue/skills/",
    },
    # Crush
    "crush": {
        "name": "Crush",
        "project": ".crush/skills/",
        "global": "~/.config/crush/skills/",
    },
    # Cursor
    "cursor": {
        "name": "Cursor",
        "project": ".cursor/skills/",
        "global": "~/.cursor/skills/",
    },
    # Droid
    "droid": {
        "name": "Droid",
        "project": ".factory/skills/",
        "global": "~/.factory/skills/",
    },
    # Gemini CLI
    "gemini-cli": {
        "name": "Gemini CLI",
        "project": ".agents/skills/",
        "global": "~/.gemini/skills/",
    },
    # GitHub Copilot
    "github-copilot": {
        "name": "GitHub Copilot",
        "project": ".agents/skills/",
        "global": "~/.copilot/skills/",
    },
    # Goose
    "goose": {
        "name": "Goose",
        "project": ".goose/skills/",
        "global": "~/.config/goose/skills/",
    },
    # Junie
    "junie": {
        "name": "Junie",
        "project": ".junie/skills/",
        "global": "~/.junie/skills/",
    },
    # iFlow CLI
    "iflow-cli": {
        "name": "iFlow CLI",
        "project": ".iflow/skills/",
        "global": "~/.iflow/skills/",
    },
    # Kilo Code
    "kilo": {
        "name": "Kilo Code",
        "project": ".kilocode/skills/",
        "global": "~/.kilocode/skills/",
    },
    # Kiro CLI
    "kiro-cli": {
        "name": "Kiro CLI",
        "project": ".kiro/skills/",
        "global": "~/.kiro/skills/",
    },
    # Kode
    "kode": {
        "name": "Kode",
        "project": ".kode/skills/",
        "global": "~/.kode/skills/",
    },
    # MCPJam
    "mcpjam": {
        "name": "MCPJam",
        "project": ".mcpjam/skills/",
        "global": "~/.mcpjam/skills/",
    },
    # Mistral Vibe
    "mistral-vibe": {
        "name": "Mistral Vibe",
        "project": ".vibe/skills/",
        "global": "~/.vibe/skills/",
    },
    # Mux
    "mux": {
        "name": "Mux",
        "project": ".mux/skills/",
        "global": "~/.mux/skills/",
    },
    # OpenCode
    "opencode": {
        "name": "OpenCode",
        "project": ".agents/skills/",
        "global": "~/.config/opencode/skills/",
    },
    # OpenHands
    "openhands": {
        "name": "OpenHands",
        "project": ".openhands/skills/",
        "global": "~/.openhands/skills/",
    },
    # Pi
    "pi": {
        "name": "Pi",
        "project": ".pi/skills/",
        "global": "~/.pi/agent/skills/",
    },
    # Qoder
    "qoder": {
        "name": "Qoder",
        "project": ".qoder/skills/",
        "global": "~/.qoder/skills/",
    },
    # Qwen Code
    "qwen-code": {
        "name": "Qwen Code",
        "project": ".qwen/skills/",
        "global": "~/.qwen/skills/",
    },
    # Replit (project-only)
    "replit": {
        "name": "Replit",
        "project": ".agents/skills/",
        "global": None,
    },
    # Roo Code
    "roo": {
        "name": "Roo Code",
        "project": ".roo/skills/",
        "global": "~/.roo/skills/",
    },
    # Trae
    "trae": {
        "name": "Trae",
        "project": ".trae/skills/",
        "global": "~/.trae/skills/",
    },
    # Trae CN
    "trae-cn": {
        "name": "Trae CN",
        "project": ".trae/skills/",
        "global": "~/.trae-cn/skills/",
    },
    # Windsurf
    "windsurf": {
        "name": "Windsurf",
        "project": ".windsurf/skills/",
        "global": "~/.codeium/windsurf/skills/",
    },
    # Zencoder
    "zencoder": {
        "name": "Zencoder",
        "project": ".zencoder/skills/",
        "global": "~/.zencoder/skills/",
    },
    # Neovate
    "neovate": {
        "name": "Neovate",
        "project": ".neovate/skills/",
        "global": "~/.neovate/skills/",
    },
    # Pochi
    "pochi": {
        "name": "Pochi",
        "project": ".pochi/skills/",
        "global": "~/.pochi/skills/",
    },
    # AdaL
    "adal": {
        "name": "AdaL",
        "project": ".adal/skills/",
        "global": "~/.adal/skills/",
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
        global_path = info.get("global")
        if global_path is None:
            continue
        global_path = Path(global_path).expanduser()
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

    Raises:
        ValueError: If the agent doesn't support global deployment (global=None)
    """
    if agent_id not in AGENTS:
        raise ValueError(f"Unknown agent: {agent_id}")

    info = AGENTS[agent_id]

    if deployment_type == "global":
        global_path = info.get("global")
        if global_path is None:
            raise ValueError(f"Agent '{agent_id}' does not support global deployment (project-only)")
        return Path(global_path).expanduser()
    else:
        if project_root is None:
            project_root = Path.cwd()
        return project_root / info["project"]


def supports_global_deployment(agent_id: str) -> bool:
    """
    Check if an agent supports global deployment.

    Args:
        agent_id: The agent identifier

    Returns:
        True if the agent supports global deployment, False otherwise
    """
    if agent_id not in AGENTS:
        raise ValueError(f"Unknown agent: {agent_id}")
    return AGENTS[agent_id].get("global") is not None


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
