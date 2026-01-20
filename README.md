# Agent Skill Manager

A comprehensive CLI tool for managing AI agent skills across multiple platforms. Download, deploy, update, and manage skills for AI coding assistants like Claude Code, Cursor, Windsurf, and more.

[![PyPI version](https://badge.fury.io/py/agent-skill-manager.svg)](https://pypi.org/project/agent-skill-manager/)
[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Features

- 📥 **Download** skills from GitHub with metadata tracking
- 🚀 **Deploy** skills to multiple AI agents (global or project-level)
- 🔄 **Update** skills automatically from GitHub sources
- 🗑️ **Uninstall** with safe deletion (move to trash) or hard delete
- ♻️ **Restore** deleted skills from trash
- 📋 **List** all installed skills with version information

## Supported AI Agents

- Claude Code
- Cursor
- Windsurf
- OpenCode
- GitHub Copilot
- Goose
- Gemini CLI
- Roo Code
- Kilo Code
- Amp
- Codex
- Antigravity
- Clawdbot
- Droid

## Installation

### Quick Run with uvx (No Installation Required)

Run directly without installing (recommended for trying it out):

```bash
# Show help (default command)
uvx agent-skill-manager

# Use sm command for specific operations
uvx --from agent-skill-manager sm install
uvx --from agent-skill-manager sm list
uvx --from agent-skill-manager sm update --all

# Or create an alias for convenience
alias sm="uvx --from agent-skill-manager sm"
sm install  # Now you can use it like the installed version
```

### Permanent Installation

```bash
# Using uv (recommended)
uv tool install agent-skill-manager

# Using pip
pip install agent-skill-manager

# Using pipx (isolated installation)
pipx install agent-skill-manager
```

### From Source

```bash
git clone https://github.com/ackness/skill-manager.git
cd skill-manager
uv sync
uv pip install -e .
```

## Usage Methods Comparison

| Method | Command | Use Case |
|--------|---------|----------|
| **uvx (no install)** | `uvx --from agent-skill-manager sm install` | One-time use, testing, CI/CD |
| **uv tool install** | `uv tool install agent-skill-manager` then `sm install` | Regular use, isolated |
| **pip install** | `pip install agent-skill-manager` then `sm install` | Traditional installation |
| **From source** | `git clone ...` then `uv pip install -e .` | Development |

## Quick Start

```bash
# Run without installing (using uvx)
uvx --from agent-skill-manager sm install
uvx --from agent-skill-manager sm list

# Or after installation, use sm command directly:
sm install          # Install a skill from GitHub
sm list            # List installed skills
sm update --all    # Update all skills
sm deploy          # Deploy local skills to agents
sm uninstall       # Uninstall a skill (safe delete)
```

## Commands

| Command | Description |
|---------|-------------|
| `sm download` | Download a skill from GitHub |
| `sm deploy` | Deploy local skills to agents |
| `sm install` | Download and deploy in one step |
| `sm uninstall` | Remove skills (safe delete/hard delete) |
| `sm restore` | Restore deleted skills from trash |
| `sm update` | Update selected skills from GitHub |
| `sm update --all` | Update all GitHub-sourced skills |
| `sm list` | Show installed skills with versions |

## Usage Examples

### Install a skill from GitHub

```bash
sm install
# Enter URL: https://github.com/user/repo/tree/main/skills/example-skill
# Follow the prompts to save locally and deploy
```

### Update all skills

```bash
sm update --all
# Automatically updates all skills installed from GitHub
```

### List installed skills with versions

```bash
sm list
# Shows a table for each agent with:
# - Skill Name
# - Version/Updated timestamp
# - Source (GitHub/Local)
# - GitHub URL (for updatable skills)
```

### Safe delete and restore

```bash
# Uninstall with safe delete (default)
sm uninstall

# Restore if needed
sm restore
```

## Version Tracking

The tool uses two methods for version identification:

1. **GitHub Metadata** (for installed skills)
   - Tracks installation and update timestamps
   - Stores repository information
   - Enables automatic updates

2. **File Modification Time** (for local skills)
   - Uses SKILL.md modification time as fallback
   - For skills without metadata

## Directory Structure

### Global Installation
Skills are available to all projects:
```
~/.claude/skills/           # Claude Code
~/.cursor/skills/           # Cursor
~/.codeium/windsurf/skills/ # Windsurf
# ... other agents
```

### Project Installation
Skills are only available in the current project:
```
project-root/
  .claude/skills/
  .cursor/skills/
  # ... other agents
```

## Configuration

Each skill installed from GitHub includes metadata in `.skill_metadata.json`:

```json
{
  "source": "github",
  "github_url": "https://github.com/...",
  "owner": "user",
  "repo": "repo-name",
  "branch": "main",
  "path": "skills/skill-name",
  "installed_at": "2026-01-20T14:30:52+00:00",
  "updated_at": "2026-01-20T14:30:52+00:00"
}
```

## Development

### Adding Support for New Agents

Edit `src/skill_manager/agents.py` and add the agent configuration:

```python
"agent-id": {
    "name": "Agent Name",
    "project": ".agent/skills/",
    "global": "~/.agent/skills/",
}
```

### Running Tests

```bash
uv run pytest
```

### Code Formatting

```bash
uv run ruff format .
uv run ruff check . --fix
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Related Projects

- [Agent Skills Specification](https://agentskills.io/specification)
- [Agent Skills Registry](https://agentskills.io)

## License

MIT License - See [LICENSE](LICENSE) file for details

## Author

**ackness** - [ackness8@gmail.com](mailto:ackness8@gmail.com)

## Acknowledgments

- Built following the [Agent Skills specification](https://agentskills.io/specification)
- Supports all major AI coding assistants
