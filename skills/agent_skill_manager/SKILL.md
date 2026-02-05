---
name: skill-manager
description: Manage AI agent skills - download from GitHub, discover skills in repositories, deploy to multiple agents with symlink support, update, uninstall with safe deletion, and track versions. Use when users want to install, manage, or update skills for AI coding assistants like Claude Code, Cursor, Windsurf, etc.
license: MIT
compatibility: Requires Python 3.13+, uv or rye package manager, internet access for GitHub downloads
metadata:
  author: ackness
  version: "0.2.1"
  repository: https://github.com/ackness/skill-manager
  pypi: agent-skill-manager
  platforms:
    - windows
    - linux
    - macos
allowed-tools: Bash(uv:*) Bash(git:*) Read Write
---

# Skill Manager

A comprehensive CLI tool for managing AI agent skills across multiple platforms. Supports downloading skills from GitHub, discovering all skills in a repository, deploying to various AI agents with symlink support, version tracking, safe deletion with recovery, and automatic updates.

## Key Features

- **Skill Discovery** - Automatically find all SKILL.md files in a GitHub repository
- **Symlink Support** - Deploy skills using symlinks to save disk space
- **CLI-first** - Full command-line parameter support for automation
- **39 Agents** - Support for all major AI coding assistants

## Supported AI Agents

| Agent | ID | Project Path | Global Path |
|-------|-----|--------------|-------------|
| Amp | `amp` | `.agents/skills/` | `~/.config/agents/skills/` |
| Antigravity | `antigravity` | `.agent/skills/` | `~/.gemini/antigravity/skills/` |
| Augment | `augment` | `.augment/rules/` | `~/.augment/rules/` |
| Claude Code | `claude-code` | `.claude/skills/` | `~/.claude/skills/` |
| Cline | `cline` | `.cline/skills/` | `~/.cline/skills/` |
| CodeBuddy | `codebuddy` | `.codebuddy/skills/` | `~/.codebuddy/skills/` |
| Codex | `codex` | `.agents/skills/` | `~/.codex/skills/` |
| Command Code | `command-code` | `.commandcode/skills/` | `~/.commandcode/skills/` |
| Continue | `continue` | `.continue/skills/` | `~/.continue/skills/` |
| Crush | `crush` | `.crush/skills/` | `~/.config/crush/skills/` |
| Cursor | `cursor` | `.cursor/skills/` | `~/.cursor/skills/` |
| Droid | `droid` | `.factory/skills/` | `~/.factory/skills/` |
| Gemini CLI | `gemini-cli` | `.agents/skills/` | `~/.gemini/skills/` |
| GitHub Copilot | `github-copilot` | `.agents/skills/` | `~/.copilot/skills/` |
| Goose | `goose` | `.goose/skills/` | `~/.config/goose/skills/` |
| iFlow CLI | `iflow-cli` | `.iflow/skills/` | `~/.iflow/skills/` |
| Junie | `junie` | `.junie/skills/` | `~/.junie/skills/` |
| Kilo Code | `kilo` | `.kilocode/skills/` | `~/.kilocode/skills/` |
| Kimi Code CLI | `kimi-cli` | `.agents/skills/` | `~/.config/agents/skills/` |
| Kiro CLI | `kiro-cli` | `.kiro/skills/` | `~/.kiro/skills/` |
| Kode | `kode` | `.kode/skills/` | `~/.kode/skills/` |
| MCPJam | `mcpjam` | `.mcpjam/skills/` | `~/.mcpjam/skills/` |
| Mistral Vibe | `mistral-vibe` | `.vibe/skills/` | `~/.vibe/skills/` |
| Mux | `mux` | `.mux/skills/` | `~/.mux/skills/` |
| Neovate | `neovate` | `.neovate/skills/` | `~/.neovate/skills/` |
| OpenClaw | `openclaw` | `skills/` | `~/.moltbot/skills/` |
| OpenCode | `opencode` | `.agents/skills/` | `~/.config/opencode/skills/` |
| OpenHands | `openhands` | `.openhands/skills/` | `~/.openhands/skills/` |
| Pi | `pi` | `.pi/skills/` | `~/.pi/agent/skills/` |
| Pochi | `pochi` | `.pochi/skills/` | `~/.pochi/skills/` |
| Qoder | `qoder` | `.qoder/skills/` | `~/.qoder/skills/` |
| Qwen Code | `qwen-code` | `.qwen/skills/` | `~/.qwen/skills/` |
| Replit | `replit` | `.agents/skills/` | N/A (project-only) |
| Roo Code | `roo` | `.roo/skills/` | `~/.roo/skills/` |
| Trae | `trae` | `.trae/skills/` | `~/.trae/skills/` |
| Trae CN | `trae-cn` | `.trae/skills/` | `~/.trae-cn/skills/` |
| Windsurf | `windsurf` | `.windsurf/skills/` | `~/.codeium/windsurf/skills/` |
| Zencoder | `zencoder` | `.zencoder/skills/` | `~/.zencoder/skills/` |
| AdaL | `adal` | `.adal/skills/` | `~/.adal/skills/` |

## Installation

### Quick Install (Recommended)

Install with uv tool for the best experience:

```bash
# Install from PyPI (recommended)
uv tool install agent-skill-manager

# After installation, use the sm command
sm --version
sm install
```

**Benefits:**
- Clean isolated environment
- No conflicts with other packages
- Easy updates: `uv tool upgrade agent-skill-manager`
- `sm` command available globally

### Alternative: Run Without Installing

For one-time use or testing, use uvx:

```bash
# Run directly without installing
uvx agent-skill-manager

# Or run specific commands
uvx --from agent-skill-manager sm install
uvx --from agent-skill-manager sm list

# Create an alias for convenience
alias sm="uvx --from agent-skill-manager sm"
```

### Other Installation Methods

```bash
# Using pip
pip install agent-skill-manager

# From source (for development)
git clone https://github.com/ackness/skill-manager.git
cd skill-manager
uv sync
uv pip install -e .
```

After installation, the `sm` command will be available globally.

## Commands Overview

| Command | Description |
|---------|-------------|
| `sm install [url]` | Download and deploy skills (with discovery) |
| `sm download [url]` | Download a skill from GitHub |
| `sm deploy` | Deploy local skills to agents |
| `sm discover [url]` | Discover all skills in a repository |
| `sm uninstall` | Remove skills (safe delete/hard delete) |
| `sm restore` | Restore deleted skills from trash |
| `sm update [--all]` | Update skills from GitHub |
| `sm list` | Show installed skills with versions |
| `sm agents` | List all supported agents |

## CLI Options

| Option | Description |
|--------|-------------|
| `-a, --agent AGENT` | Target agent(s), can be specified multiple times |
| `-t, --type TYPE` | Deployment type: `global` (default) or `project` |
| `-d, --dest PATH` | Custom destination directory for downloads |
| `--no-symlink` | Disable symlinks, copy files instead (symlinks on by default) |
| `--no-discover` | Disable auto-discovery, install only the specified path |
| `--no-deploy` | Download only, skip deployment |
| `-y`, `--yes` | Skip confirmation prompts |

### Install Skills (CLI Mode - Recommended)

由于支持 skill 的 agent 一般没有交互式环境，优先使用 CLI 格式：

```bash
# Install all skills from a repo (auto-discovery and symlinks enabled by default)
sm install https://github.com/cloudflare/skills -a windsurf -a cursor

# Full CLI mode - no prompts
sm install https://github.com/user/repo/tree/main/skills/my-skill -a claude-code -t global

# Disable auto-discovery, install only the specified path
sm install https://github.com/user/repo/tree/main/skills/my-skill --no-discover -a cursor

# Disable symlinks, copy files instead
sm install https://github.com/cloudflare/skills --no-symlink -a windsurf

# Download to custom location
sm install https://github.com/user/repo/tree/main/skills/my-skill -d ./my-skills -a cursor
```

### Interactive Mode (For Interactive Terminals Only)

```bash
sm install
# Enter URL when prompted
# Follow the prompts to save locally and deploy
```

### Discover Skills
```bash
# Scan a repository to find all skills
sm discover https://github.com/cloudflare/skills
# Shows a table of all found skills with their paths
```

### Download Skills (CLI Mode - Recommended)

```bash
# Download all skills from repo (auto-discovery enabled by default)
sm download https://github.com/user/repo -d ~/my-skills

# Download single skill to temp directory (default)
sm download https://github.com/user/repo/tree/main/skills/my-skill

# Disable auto-discovery, download only the specified path
sm download https://github.com/user/repo/tree/main/skills/my-skill --no-discover -d ~/my-skills
```

### Interactive Mode (For Interactive Terminals Only)

```bash
sm download
# Follow prompts to enter URL and destination
```

### Deploy Skills (CLI Mode - Recommended)

For automated deployment without prompts:

```bash
# Deploy specific skills to specific agents
sm deploy skill1 skill2 -a claude-code -a cursor -t global

# Deploy with symlinks
sm deploy my-skill -a windsurf --symlink
```

### Interactive Mode (For Interactive Terminals Only)

```bash
sm deploy
# Select deployment type, agents, and skills interactively
```

### Update Skills (CLI Mode - Recommended)

```bash
# Update all skills without prompts
sm update --all -y

# Update specific skills
sm update skill1 skill2 -a claude-code
```

### Interactive Mode (For Interactive Terminals Only)

```bash
# Update selected skills interactively
sm update

# Update all skills (with confirmation)
sm update --all
```

### Uninstall Skills (CLI Mode - Recommended)

```bash
# Uninstall specific skills from specific agents
sm uninstall skill1 skill2 -a claude-code -a cursor

# Hard delete (permanent, no trash)
sm uninstall my-skill -a windsurf --hard
```

### Interactive Mode (For Interactive Terminals Only)

```bash
sm uninstall
# Select skills to remove interactively
# Choose "Safe delete" (default) or "Hard delete"
```

### Restore Skills (CLI Mode - Recommended)

```bash
# Restore specific skills
sm restore skill1 skill2 -a claude-code
```

### Interactive Mode (For Interactive Terminals Only)

```bash
sm restore
# Select skills to restore interactively (shows deletion timestamp)
```

### List Skills
```bash
sm list
```
Shows all installed skills with version information across agents.

### List Agents
```bash
sm agents
```
Shows all 39 supported agents with their project and global paths.

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

## Examples (CLI-First)

所有示例优先展示 CLI 格式，适用于自动化和无交互环境：

### Install all skills from a repository (auto-discovery)
```bash
# Auto-discovery is enabled by default - installs all skills found in repo
sm install https://github.com/cloudflare/skills -a windsurf -a cursor -a claude-code

# Use symlinks to save disk space (single copy, multiple deployments)
sm install https://github.com/cloudflare/skills --symlink -a windsurf
```

### Install a single skill (CLI mode)
```bash
# Full CLI mode - no prompts
sm install https://github.com/user/repo/tree/main/skills/my-skill -a claude-code -t global

# Download to custom location
sm install https://github.com/user/repo/tree/main/skills/my-skill -d ./my-skills -a cursor
```

### Interactive mode (alternative for interactive terminals)
```bash
sm install
# Enter URL when prompted
# Follow the prompts to save locally and deploy
```

### Discover skills in a repo
```bash
sm discover https://github.com/cloudflare/skills
# Shows a table of all found skills with their paths and URLs
```

### Update all skills
```bash
sm update --all
# Downloads latest versions from GitHub
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

### Using symlinks
```bash
# Download skills to a central location and symlink to agents (default behavior)
sm install https://github.com/cloudflare/skills -d ~/skills -a windsurf -a cursor -a claude-code

# Disable symlinks if needed
sm install https://github.com/cloudflare/skills --no-symlink -a windsurf
```
Note: On Windows, symlinks require Developer Mode or admin privileges. Falls back to copying if not supported or when `--no-symlink` is used.

## Best Practices

1. **Symlinks are enabled by default** - Save disk space automatically, use `--no-symlink` to disable
2. **Auto-discovery is enabled by default** - Discover and install all skills automatically, use `--no-discover` to disable
3. **Use safe delete by default** - You can always restore if needed
4. **Update regularly** - Run `sm update --all` periodically for bug fixes and improvements
5. **Use CLI options for automation** - Avoid prompts with `-a`, `-t`, `-y` flags
6. **Check versions** - Use `sm list` to see what's installed and outdated

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
