---
name: skill-manager
description: Manage AI agent skills - download from GitHub, deploy to multiple agents, update, uninstall with safe deletion, and track versions. Use when users want to install, manage, or update skills for AI coding assistants like Claude Code, Cursor, Windsurf, etc.
license: MIT
compatibility: Requires Python 3.13+, uv or rye package manager, internet access for GitHub downloads
metadata:
  author: ackness
  version: "0.1.0"
  repository: https://github.com/ackness/skill-manager
  pypi: agent-skill-manager
  platforms:
    - windows
    - linux
    - macos
allowed-tools: Bash(uv:*) Bash(git:*) Read Write
---

# Skill Manager

A comprehensive CLI tool for managing AI agent skills across multiple platforms. Supports downloading skills from GitHub, deploying to various AI agents, version tracking, safe deletion with recovery, and automatic updates.

## Supported AI Agents

- Claude Code
- Cursor
- Windsurf
- OpenCode
- Copilot
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

### Quick Run (No Installation Required)

Run directly with uvx without installing (perfect for one-time use or testing):

```bash
# Show help menu
uvx agent-skill-manager

# Run specific commands
uvx --from agent-skill-manager sm install
uvx --from agent-skill-manager sm list
uvx --from agent-skill-manager sm update --all

# Create a shell alias for convenience
alias sm="uvx --from agent-skill-manager sm"
# Now use it like: sm install, sm list, etc.
```

**Benefits of uvx:**
- No installation needed
- Always uses the latest version from PyPI
- Isolated environment (no conflicts)
- Perfect for CI/CD or automated scripts

### Permanent Installation

```bash
# Install from PyPI with uv (recommended)
uv tool install agent-skill-manager

# Install from PyPI with pip
pip install agent-skill-manager

# Or install from source
git clone https://github.com/ackness/skill-manager.git
cd skill-manager
uv sync
uv pip install -e .
```

After installation, the `sm` command will be available globally.

## Commands Overview

### Download Skills
```bash
sm download
```
Downloads a skill from GitHub to local storage. Saves metadata for version tracking and future updates.

**When to use:** When you want to save a skill locally without deploying it yet.

**Interactive prompts:**
- GitHub URL of the skill
- Whether to save to local skills/ directory
- Category for organization (optional)

### Deploy Skills
```bash
sm deploy
```
Deploys skills from your local `skills/` directory to selected AI agents.

**When to use:** When you have local skills ready to deploy to agents.

**Interactive prompts:**
- Deployment location (global/project)
- Target agents
- Skills to deploy

### Install Skills
```bash
sm install
```
Combined operation: downloads from GitHub and deploys to agents in one step.

**When to use:** When you want to quickly install a skill from GitHub to your agents.

**Interactive prompts:**
- GitHub URL
- Whether to save locally
- Category (if saving locally)
- Whether to deploy
- Target agents and deployment location

### Update Skills
```bash
# Update selected skills
sm update

# Update all skills with GitHub metadata
sm update --all
```
Updates skills from their GitHub sources. Only works for skills installed via `sm install` or with saved metadata.

**When to use:** When you want to get the latest version of installed skills.

**Features:**
- Automatic backup before update
- Rollback on failure
- Updates metadata timestamps
- Shows version information

### Uninstall Skills
```bash
sm uninstall
```
Removes skills from agents with two deletion modes:
- **Safe delete (default):** Moves to `.trash` with timestamp for recovery
- **Hard delete:** Permanent removal

**When to use:** When you want to remove skills from agents.

**Interactive prompts:**
- Deployment type
- Target agents
- Skills to remove
- Deletion type (safe/hard)

### Restore Skills
```bash
sm restore
```
Restores previously deleted skills from trash.

**When to use:** When you accidentally deleted a skill or want to recover it.

**Interactive prompts:**
- Deployment type
- Target agents
- Skills to restore (shows deletion timestamp)

### List Skills
```bash
sm list
```
Shows all installed skills with version information across agents.

**When to use:** When you want to see what skills are installed and their versions.

**Displays:**
- Skill names
- Version/update timestamp
- Source (GitHub/Local)
- GitHub URL (for updatable skills)
- Organized by agent

## Directory Structure

### Global Installation
Skills installed globally are available to all projects:
```
~/.claude/skills/           # Claude Code
~/.cursor/skills/           # Cursor
~/.codeium/windsurf/skills/ # Windsurf
# ... other agents
```

### Project Installation
Skills installed at project level are only available in that project:
```
project-root/
  .claude/skills/
  .cursor/skills/
  # ... other agents
```

### Metadata Storage
Each skill installed from GitHub includes metadata:
```
skill-name/
  SKILL.md
  .skill_metadata.json    # Contains GitHub source, timestamps
  # ... skill files
```

### Trash Storage
Safely deleted skills are stored with timestamps:
```
~/.claude/
  skills/                 # Active skills
  .trash/                 # Deleted skills
    20260120_143052/      # Timestamp directory
      skill-name/
        .trash_metadata   # Deletion info
        # ... skill files
```

## Version Tracking

The tool uses two methods for version identification:

1. **GitHub Metadata** (for installed skills):
   - Tracks installation and update timestamps
   - Stores repository information
   - Enables automatic updates
   - Format: ISO 8601 timestamp

2. **File Modification Time** (for local skills):
   - Uses SKILL.md modification time
   - Fallback for skills without metadata
   - Format: YYYY-MM-DD HH:MM:SS

## Examples

### Install a skill from GitHub

With uvx (no installation needed):
```bash
uvx --from agent-skill-manager sm install
# Enter URL: https://github.com/user/repo/tree/main/skills/example-skill
# Save locally? Yes
# Category: productivity
# Deploy? Yes
# Select agents: Claude Code, Cursor
# Deployment: Global
```

Or with installed version:
```bash
sm install
# Follow the same prompts as above
```

### Update all skills
```bash
sm update --all
# Selects all agents with GitHub-sourced skills
# Downloads latest versions
# Updates metadata timestamps
```

### List installed skills
```bash
sm list
# Shows table for each agent:
# Skill Name | Version/Updated | Source | GitHub URL
```

### Uninstall with safe delete
```bash
sm uninstall
# Select skills to remove
# Choose "Safe delete"
# Skills moved to .trash with timestamp
# Can be restored later with sm restore
```

## Best Practices

1. **Use safe delete by default** - You can always restore if needed
2. **Update regularly** - Run `sm update --all` periodically for bug fixes and improvements
3. **Save skills locally** - Keep a local copy in `skills/` for backup
4. **Organize with categories** - Use categories when saving locally for better organization
5. **Check versions** - Use `sm list` to see what's installed and outdated

## Troubleshooting

### Command not found: sm
Reinstall the package:
```bash
uv pip install -e .
```

### GitHub download fails
- Check internet connection
- Verify the GitHub URL is correct
- Ensure the URL points to a directory, not a file
- Check if the repository is public

### Skill not showing in agent
- Verify the agent is running
- Check deployment location (global vs project)
- Ensure the skill has a valid SKILL.md file
- Restart the agent if necessary

### Update fails
- The tool automatically restores from backup
- Check if the GitHub repository still exists
- Verify internet connection
- Try reinstalling: `sm uninstall` then `sm install`

## Technical Details

### Metadata Format
```json
{
  "source": "github",
  "github_url": "https://github.com/...",
  "owner": "user",
  "repo": "repo-name",
  "branch": "main",
  "path": "skills/skill-name",
  "installed_at": "2026-01-20T14:30:52.123456+00:00",
  "updated_at": "2026-01-20T14:30:52.123456+00:00"
}
```

### Agent Configuration
Each agent has defined paths for:
- **project**: Skills directory within current project
- **global**: User-wide skills directory
- See `src/skill_manager/agents.py` for complete mapping

### Update Process
1. Read skill metadata to get GitHub source
2. Download updated version to temporary location
3. Create backup of current version
4. Remove current version
5. Move updated version to skill location
6. Update metadata timestamp
7. Clean up temporary files
8. On failure: restore from backup

## Development

To add support for a new AI agent:

1. Edit `src/skill_manager/agents.py`
2. Add agent configuration:
```python
"agent-id": {
    "name": "Agent Name",
    "project": ".agent/skills/",
    "global": "~/.agent/skills/",
}
```
3. Test with `sm list` to verify detection

## Related Resources

- Agent Skills Specification: https://agentskills.io/specification
- Report Issues: https://github.com/ackness/skill-manager/issues
- Skill Registry: https://agentskills.io

## License

MIT License - See LICENSE file for details
