# Agent Skill Manager

ALL codes are written by Claude Code.

A comprehensive CLI tool for managing AI agent skills across multiple platforms. Download, deploy, update, and manage skills for AI coding assistants like Claude Code, Cursor, Windsurf, and more.

[![PyPI version](https://badge.fury.io/py/agent-skill-manager.svg)](https://pypi.org/project/agent-skill-manager/)
[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Features

- 📥 **Download** skills from GitHub with metadata tracking
- 🔍 **Discover** all skills in a repository automatically
- 🚀 **Deploy** skills to multiple AI agents (global or project-level)
- 🔗 **Symlink** support - save disk space with symbolic links
- 🔄 **Update** skills automatically from GitHub sources
- 🗑️ **Uninstall** with safe deletion (move to trash) or hard delete
- ♻️ **Restore** deleted skills from trash
- 📋 **List** all installed skills with version information
- ⚡ **CLI-first** - full command-line parameter support for automation
- 🏎️ **Fast downloads** - 3-tier strategy: git sparse-checkout → Tree API + raw URLs → Contents API fallback

## Supported AI Agents

<!-- supported-agents:start -->
| Agent | `--agent` | Project Path | Global Path |
|-------|-----------|--------------|-------------|
| Amp, Kimi Code CLI | `amp`, `kimi-cli` | `.agents/skills/` | `~/.config/agents/skills/` |
| Antigravity | `antigravity` | `.agent/skills/` | `~/.gemini/antigravity/skills/` |
| Augment | `augment` | `.augment/rules/` | `~/.augment/rules/` |
| Claude Code | `claude-code` | `.claude/skills/` | `~/.claude/skills/` |
| OpenClaw | `openclaw` | `skills/` | `~/.moltbot/skills/` |
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
| Junie | `junie` | `.junie/skills/` | `~/.junie/skills/` |
| iFlow CLI | `iflow-cli` | `.iflow/skills/` | `~/.iflow/skills/` |
| Kilo Code | `kilo` | `.kilocode/skills/` | `~/.kilocode/skills/` |
| Kiro CLI | `kiro-cli` | `.kiro/skills/` | `~/.kiro/skills/` |
| Kode | `kode` | `.kode/skills/` | `~/.kode/skills/` |
| MCPJam | `mcpjam` | `.mcpjam/skills/` | `~/.mcpjam/skills/` |
| Mistral Vibe | `mistral-vibe` | `.vibe/skills/` | `~/.vibe/skills/` |
| Mux | `mux` | `.mux/skills/` | `~/.mux/skills/` |
| OpenCode | `opencode` | `.agents/skills/` | `~/.config/opencode/skills/` |
| OpenHands | `openhands` | `.openhands/skills/` | `~/.openhands/skills/` |
| Pi | `pi` | `.pi/skills/` | `~/.pi/agent/skills/` |
| Qoder | `qoder` | `.qoder/skills/` | `~/.qoder/skills/` |
| Qwen Code | `qwen-code` | `.qwen/skills/` | `~/.qwen/skills/` |
| Replit | `replit` | `.agents/skills/` | N/A (project-only) |
| Roo Code | `roo` | `.roo/skills/` | `~/.roo/skills/` |
| Trae | `trae` | `.trae/skills/` | `~/.trae/skills/` |
| Trae CN | `trae-cn` | `.trae/skills/` | `~/.trae-cn/skills/` |
| Windsurf | `windsurf` | `.windsurf/skills/` | `~/.codeium/windsurf/skills/` |
| Zencoder | `zencoder` | `.zencoder/skills/` | `~/.zencoder/skills/` |
| Neovate | `neovate` | `.neovate/skills/` | `~/.neovate/skills/` |
| Pochi | `pochi` | `.pochi/skills/` | `~/.pochi/skills/` |
| AdaL | `adal` | `.adal/skills/` | `~/.adal/skills/` |
<!-- supported-agents:end -->

> [!NOTE]
> **Kiro CLI users:** After installing skills, manually add them to your custom agent's `resources` in
> `.kiro/agents/<agent>.json`:
>
> ```json
> {
>   "resources": ["skill://.kiro/skills/**/SKILL.md"]
> }
> ```

## Installation

### Recommended: Install with uv tool

The best way to install is using `uv tool`:

```bash
# Install from PyPI
uv tool install agent-skill-manager

# Verify installation
sm --version

# Start using
sm install
```

**Why uv tool?**
- Isolated environment (no package conflicts)
- Easy updates: `uv tool upgrade agent-skill-manager`
- Clean uninstall: `uv tool uninstall agent-skill-manager`
- Works across all projects

### Alternative: Run Without Installing

For one-time use or testing:

```bash
# Run directly with uvx (no installation needed)
uvx agent-skill-manager

# Or run specific commands
uvx --from agent-skill-manager sm install
uvx --from agent-skill-manager sm list
```

### Other Installation Methods

```bash
# Using pip
pip install agent-skill-manager

# Using pipx (isolated like uv tool)
pipx install agent-skill-manager

# From source (for development)
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
sm install          # Install a skill from GitHub (interactive)
sm list             # List installed skills
sm update --all     # Update all skills
sm deploy           # Deploy local skills to agents
sm uninstall        # Uninstall a skill (safe delete)
sm agents           # List all supported agents
```

## Commands

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
| `sm --version` / `sm -v` | Show version information |

## CLI Options

| Option | Description |
|--------|-------------|
| `-a, --agent AGENT` | Target agent(s), can be specified multiple times |
| `-t, --type TYPE` | Deployment type: `global` (default) or `project` |
| `-d, --dest PATH` | Custom destination directory (default: `~/.skill-manager/skills/`) |
| `-s, --skills NAME` | Skill name(s) to install (default: all discovered skills) |
| `--no-symlink` | Disable symlinks, copy files instead (symlinks on by default) |
| `--no-discover` | Disable auto-discovery (on by default) |
| `--no-deploy` | Download only, skip deployment |
| `-y, --yes` | Skip confirmation prompts |

## Network Configuration

The tool supports proxy, GitHub token, and GitHub mirror via environment variables:

| Variable | Description | Example |
|----------|-------------|---------|
| `GITHUB_TOKEN` / `GH_TOKEN` | GitHub personal access token (increases API rate limit) | `ghp_xxxx` |
| `HTTP_PROXY` / `HTTPS_PROXY` | HTTP/HTTPS proxy URL | `http://127.0.0.1:7890` |
| `ALL_PROXY` | Fallback proxy for both HTTP and HTTPS | `socks5://127.0.0.1:1080` |
| `GITHUB_MIRROR` | GitHub download mirror prefix | `https://mirror.ghproxy.com` |

```bash
# Example: use proxy for faster downloads
export HTTPS_PROXY=http://127.0.0.1:7890
sm install https://github.com/cloudflare/skills -a windsurf

# Example: use GitHub token to avoid rate limits
export GITHUB_TOKEN=ghp_your_token_here
sm install https://github.com/cloudflare/skills -a windsurf

# Example: use GitHub mirror (for users in China)
export GITHUB_MIRROR=https://mirror.ghproxy.com
sm install https://github.com/cloudflare/skills -a windsurf

# PowerShell (Windows)
$env:HTTPS_PROXY="http://127.0.0.1:7890"
$env:GITHUB_TOKEN="ghp_your_token_here"
sm install https://github.com/cloudflare/skills -a windsurf
```

> [!TIP]
> Get a GitHub token at https://github.com/settings/tokens (only `public_repo` scope needed).
> Network status is shown during GitHub operations.

## Usage Examples

### Install skills from a GitHub repository

```bash
# Install all skills from a repo (auto-discovery and symlinks enabled by default)
sm install https://github.com/cloudflare/skills -a windsurf -a cursor

# Install specific skills only
sm install https://github.com/cloudflare/skills -s mcp -s browser-rendering -a windsurf

# Full CLI mode - no prompts
sm install https://github.com/user/repo/tree/main/skills/my-skill -a claude-code -t global

# Disable auto-discovery to install only the specific path
sm install https://github.com/user/repo/tree/main/skills/my-skill --no-discover -a cursor

# Disable symlinks, copy files instead
sm install https://github.com/cloudflare/skills --no-symlink -a windsurf

# Download to custom location
sm install https://github.com/user/repo/tree/main/skills/my-skill -d ./my-skills -a cursor
```

### Install skills from a local directory

```bash
# Install from a previously downloaded skills directory
sm install ~/.skill-manager/skills -a windsurf -a cursor

# Install specific skills from local directory
sm install ~/my-skills -s my-skill-name -a claude-code

# Install from any local directory containing SKILL.md files
sm install ./path/to/skills -a windsurf
```

### Discover skills in a repository

```bash
# Scan a repository to find all skills
sm discover https://github.com/cloudflare/skills
# Shows a table of all found skills with their paths
```

### Interactive mode

```bash
sm install
# Enter URL when prompted, all skills are pre-selected by default
# Follow the prompts to select agents and deploy
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

### Using symlinks

Symlinks allow you to maintain a single copy of skills while deploying to multiple agents:

```bash
# Download skills to a central location and symlink to agents (default behavior)
sm install https://github.com/cloudflare/skills -d ~/skills -a windsurf -a cursor -a claude-code

# Disable symlinks if needed
sm install https://github.com/cloudflare/skills --no-symlink -a windsurf
```

> [!NOTE]
> On Windows, symlinks require Developer Mode or administrator privileges. If symlinks are not supported, the tool will automatically fall back to copying.

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

### Default Skills Cache
Downloaded skills are stored in `~/.skill-manager/skills/` by default (cross-platform).

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
