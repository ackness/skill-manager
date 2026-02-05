#!/usr/bin/env python3
"""
Skill Manager - CLI tool for managing AI agent skills.

Usage: sm <command> or skill-manager <command>

Commands:
    download      - Download skills from GitHub
    deploy        - Deploy local skills to agents
    install       - Download and deploy skills in one step
    uninstall     - Remove skills from agents (safe delete)
    restore       - Restore deleted skills from trash
    update        - Update skills from GitHub
    update --all  - Update all skills from GitHub
    list          - List installed skills and versions
    discover      - Discover skills in a GitHub repository
"""

import argparse
import shutil
import sys
from pathlib import Path

from InquirerPy import inquirer
from InquirerPy.base.control import Choice
from InquirerPy.separator import Separator
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from . import __version__
from .agents import AGENTS, detect_existing_agents, get_agent_name, get_agent_path, supports_global_deployment
from .deployment import (
    deploy_multiple_skills,
    deploy_skill_to_agents,
    is_symlink_supported,
    update_all_skills,
    update_skill,
)
from .github import (
    discover_skills_in_repo,
    download_multiple_skills,
    download_skill_from_github,
    get_system_temp_dir,
    parse_github_url,
)
from .metadata import (
    list_updatable_skills,
    read_skill_metadata,
    save_skill_metadata,
)
from .removal import (
    hard_delete_skill,
    list_installed_skills,
    list_trashed_skills,
    restore_skill,
    soft_delete_skill,
)
from .validation import (
    get_project_root,
    get_skill_name,
    scan_available_skills,
    validate_skill,
)

console = Console()


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser with all subcommands."""
    parser = argparse.ArgumentParser(
        prog="sm",
        description="CLI tool for managing AI agent skills",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("-v", "--version", action="version", version=f"%(prog)s {__version__}")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Install command
    install_parser = subparsers.add_parser("install", help="Download and deploy skills from GitHub")
    install_parser.add_argument("url", nargs="?", help="GitHub URL of the skill or repository")
    install_parser.add_argument(
        "-a", "--agent", action="append", dest="agents", help="Target agent(s) (can be specified multiple times)"
    )
    install_parser.add_argument(
        "-t", "--type", choices=["global", "project"], default="global", help="Deployment type (default: global)"
    )
    install_parser.add_argument("-d", "--dest", type=Path, help="Destination directory for downloaded skills")
    install_parser.add_argument("--no-symlink", action="store_true", help="Disable symlinks, copy files instead")
    install_parser.add_argument(
        "--no-discover", action="store_true", help="Disable auto-discovery, install only the specified path"
    )
    install_parser.add_argument("--no-deploy", action="store_true", help="Download only, do not deploy")
    install_parser.add_argument("-y", "--yes", action="store_true", help="Skip confirmation prompts")

    # Download command
    download_parser = subparsers.add_parser("download", help="Download skills from GitHub")
    download_parser.add_argument("url", nargs="?", help="GitHub URL of the skill or repository")
    download_parser.add_argument("-d", "--dest", type=Path, help="Destination directory")
    download_parser.add_argument(
        "--no-discover", action="store_true", help="Disable auto-discovery, download only the specified path"
    )
    download_parser.add_argument("-y", "--yes", action="store_true", help="Skip confirmation prompts")

    # Deploy command
    deploy_parser = subparsers.add_parser("deploy", help="Deploy local skills to agents")
    deploy_parser.add_argument("skills", nargs="*", help="Skill names or paths to deploy")
    deploy_parser.add_argument("-a", "--agent", action="append", dest="agents", help="Target agent(s)")
    deploy_parser.add_argument("-t", "--type", choices=["global", "project"], default="global", help="Deployment type")
    deploy_parser.add_argument("--no-symlink", action="store_true", help="Disable symlinks, copy files instead")
    deploy_parser.add_argument("-y", "--yes", action="store_true", help="Skip confirmation prompts")

    # Discover command
    discover_parser = subparsers.add_parser("discover", help="Discover skills in a GitHub repository")
    discover_parser.add_argument("url", nargs="?", help="GitHub URL to scan")

    # Uninstall command
    uninstall_parser = subparsers.add_parser("uninstall", help="Remove skills from agents")
    uninstall_parser.add_argument("skills", nargs="*", help="Skill names to uninstall")
    uninstall_parser.add_argument("-a", "--agent", action="append", dest="agents", help="Target agent(s)")
    uninstall_parser.add_argument("-t", "--type", choices=["global", "project"], default="global", help="Deployment type")
    uninstall_parser.add_argument("--hard", action="store_true", help="Permanently delete (no trash)")
    uninstall_parser.add_argument("-y", "--yes", action="store_true", help="Skip confirmation prompts")

    # Restore command
    restore_parser = subparsers.add_parser("restore", help="Restore deleted skills from trash")
    restore_parser.add_argument("skills", nargs="*", help="Skill names to restore")
    restore_parser.add_argument("-a", "--agent", action="append", dest="agents", help="Target agent(s)")
    restore_parser.add_argument("-t", "--type", choices=["global", "project"], default="global", help="Deployment type")
    restore_parser.add_argument("-y", "--yes", action="store_true", help="Skip confirmation prompts")

    # Update command
    update_parser = subparsers.add_parser("update", help="Update skills from GitHub")
    update_parser.add_argument("skills", nargs="*", help="Skill names to update")
    update_parser.add_argument("-a", "--agent", action="append", dest="agents", help="Target agent(s)")
    update_parser.add_argument("-t", "--type", choices=["global", "project"], default="global", help="Deployment type")
    update_parser.add_argument("--all", action="store_true", help="Update all skills")
    update_parser.add_argument("-y", "--yes", action="store_true", help="Skip confirmation prompts")

    # List command
    list_parser = subparsers.add_parser("list", help="List installed skills")
    list_parser.add_argument("-a", "--agent", action="append", dest="agents", help="Target agent(s)")
    list_parser.add_argument("-t", "--type", choices=["global", "project"], default="global", help="Deployment type")

    # Agents command (list available agents)
    subparsers.add_parser("agents", help="List all supported agents")

    return parser


def select_agents(existing_agents: dict[str, Path]) -> list[str]:
    """
    Interactive prompt to select agents for deployment.

    Args:
        existing_agents: Dictionary of detected agents

    Returns:
        List of selected agent IDs
    """
    choices = []

    if existing_agents:
        choices.append(Separator("--- Detected Agents ---"))
        for agent_id in sorted(existing_agents.keys()):
            info = AGENTS[agent_id]
            choices.append(
                Choice(
                    value=agent_id,
                    name=f"{info['name']} ({existing_agents[agent_id]})",
                    enabled=True,
                )
            )

    other_agents = [aid for aid in AGENTS.keys() if aid not in existing_agents]
    if other_agents:
        choices.append(Separator("--- Other Available Agents ---"))
        for agent_id in sorted(other_agents):
            info = AGENTS[agent_id]
            global_path = Path(info["global"]).expanduser()
            choices.append(
                Choice(
                    value=agent_id,
                    name=f"{info['name']} ({global_path})",
                    enabled=False,
                )
            )

    selected = inquirer.checkbox(
        message="Select agents to deploy to:",
        choices=choices,
        instruction="(Space to select, Enter to confirm)",
    ).execute()

    return selected


def select_deployment_type() -> str:
    """
    Interactive prompt to select deployment type.

    Returns:
        Either "global" or "project"
    """
    return inquirer.select(
        message="Select deployment location:",
        choices=[
            Choice(value="global", name="Global directory (recommended) - Available to all projects"),
            Choice(value="project", name="Project directory - Current project only"),
        ],
        default="global",
    ).execute()


def select_skills(available_skills: list[Path]) -> list[Path]:
    """
    Interactive prompt to select skills for deployment.

    Args:
        available_skills: List of available skill paths

    Returns:
        List of selected skill paths
    """
    if not available_skills:
        console.print("[yellow]No skills found[/yellow]")
        return []

    # Group by category
    categories = {}
    for skill in available_skills:
        parts = skill.parts
        if len(parts) > 1:
            category = parts[0]
            skill_name = "/".join(parts[1:])
        else:
            category = "Other"
            skill_name = str(skill)

        if category not in categories:
            categories[category] = []
        categories[category].append((skill, skill_name))

    # Build choice list
    choices = []
    for category in sorted(categories.keys()):
        choices.append(Separator(f"--- {category.upper()} ---"))
        for skill, skill_name in sorted(categories[category], key=lambda x: x[1]):
            choices.append(
                Choice(
                    value=skill,
                    name=skill_name,
                    enabled=False,
                )
            )

    selected = inquirer.checkbox(
        message="Select skills to deploy:",
        choices=choices,
        instruction="(Space to select, Enter to confirm)",
    ).execute()

    return selected


def cmd_download() -> int:
    """
    Download command - Download skills from GitHub.

    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    console.print(
        Panel.fit(
            "[bold cyan]Download Skill[/bold cyan]\nDownload a skill from GitHub",
            border_style="cyan",
        )
    )

    # Get GitHub URL
    url = inquirer.text(
        message="Enter GitHub skill URL:",
        validate=lambda x: len(x) > 0,
        invalid_message="URL cannot be empty",
    ).execute()

    console.print()

    # Parse URL to show info
    try:
        owner, repo, branch, path = parse_github_url(url)
        console.print(f"[dim]Repository: {owner}/{repo}[/dim]")
        console.print(f"[dim]Branch: {branch}[/dim]")
        console.print(f"[dim]Path: {path or '(root)'}[/dim]\n")
    except ValueError as e:
        console.print(f"[red]Error: {e}[/red]")
        return 1

    # Ask where to save
    save_to_local = inquirer.confirm(
        message="Save to local skills/ directory?",
        default=True,
    ).execute()

    console.print()

    # Determine destination
    if save_to_local:
        project_root = get_project_root()
        skills_dir = project_root / "skills"

        # Ask for category
        category = inquirer.text(
            message="Enter category name (leave empty for root):",
            default="",
        ).execute()

        if category:
            dest_dir = skills_dir / category
        else:
            dest_dir = skills_dir
    else:
        dest_dir = Path.cwd() / ".tmp_skills"

    # Download
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Downloading skill...", total=None)
            skill_dir, metadata = download_skill_from_github(url, dest_dir)
            progress.update(task, completed=True)

        # Save metadata
        save_skill_metadata(
            skill_dir,
            url,
            metadata["owner"],
            metadata["repo"],
            metadata["branch"],
            metadata["path"],
        )

        # Validate
        if not validate_skill(skill_dir):
            console.print(f"[yellow]Warning: {skill_dir} does not contain SKILL.md, may not be a valid skill[/yellow]")

        console.print(f"[green]✓[/green] Skill downloaded to: {skill_dir}\n")
        return 0

    except Exception as e:
        console.print(f"[red]Download failed: {e}[/red]")
        return 1


def cmd_deploy() -> int:
    """
    Deploy command - Deploy local skills to agents.

    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    console.print(
        Panel.fit(
            "[bold cyan]Deploy Skills[/bold cyan]\nDeploy local skills to AI agents",
            border_style="cyan",
        )
    )

    # Get project root and skills directory
    project_root = get_project_root()
    skills_dir = project_root / "skills"

    console.print(f"\n[dim]Project directory: {project_root}[/dim]")
    console.print(f"[dim]Skills directory: {skills_dir}[/dim]\n")

    # Scan for skills
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Scanning for skills...", total=None)
        available_skills = scan_available_skills(skills_dir)
        progress.update(task, completed=True)

    if not available_skills:
        console.print("[red]No skills found. Exiting.[/red]")
        return 1

    console.print(f"[green]✓[/green] Found {len(available_skills)} skills\n")

    # Detect agents
    existing_agents = detect_existing_agents()
    if existing_agents:
        console.print(f"[green]✓[/green] Detected {len(existing_agents)} installed agents\n")

    # Select deployment type
    deployment_type = select_deployment_type()
    console.print()

    # Select agents
    selected_agents = select_agents(existing_agents)
    if not selected_agents:
        console.print("[yellow]No agents selected. Exiting.[/yellow]")
        return 0

    console.print()

    # Select skills
    selected_skills = select_skills(available_skills)
    if not selected_skills:
        console.print("[yellow]No skills selected. Exiting.[/yellow]")
        return 0

    console.print()

    # Show summary
    table = Table(title="Deployment Plan", show_header=True, header_style="bold magenta")
    table.add_column("Agent", style="cyan", no_wrap=True)
    table.add_column("Target Path", style="green")
    table.add_column("Skills Count", justify="right", style="yellow")

    for agent_id in selected_agents:
        target_path = get_agent_path(agent_id, deployment_type, project_root)
        table.add_row(
            get_agent_name(agent_id),
            str(target_path),
            str(len(selected_skills)),
        )

    console.print(table)
    console.print(f"\nWill deploy {len(selected_skills)} skills:")
    for skill in selected_skills:
        console.print(f"  • {skill}")

    console.print()

    # Confirm
    confirm = inquirer.confirm(
        message="Confirm deployment?",
        default=True,
    ).execute()

    if not confirm:
        console.print("[yellow]Deployment cancelled.[/yellow]")
        return 0

    console.print()

    # Deploy
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Deploying skills...", total=len(selected_agents) * len(selected_skills))

        def progress_callback(agent_id, skill_path):
            progress.advance(task)

        total_deployed, total_failed = deploy_multiple_skills(
            selected_skills,
            skills_dir,
            selected_agents,
            deployment_type,
            project_root,
            progress_callback,
        )

    # Show results
    console.print()
    if total_failed == 0:
        console.print(
            Panel.fit(
                f"[bold green]✓ Deployment successful![/bold green]\n\n"
                f"Deployed {total_deployed} skills to {len(selected_agents)} agents",
                border_style="green",
            )
        )
    else:
        console.print(
            Panel.fit(
                f"[bold yellow]⚠ Deployment completed with errors[/bold yellow]\n\n"
                f"Success: {total_deployed} | Failed: {total_failed}",
                border_style="yellow",
            )
        )

    return 0 if total_failed == 0 else 1


def cmd_install() -> int:
    """
    Install command - Download and deploy skills in one step.

    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    console.print(
        Panel.fit(
            "[bold cyan]Install Skill[/bold cyan]\nDownload and deploy a skill from GitHub",
            border_style="cyan",
        )
    )

    # Get GitHub URL
    url = inquirer.text(
        message="Enter GitHub skill URL:",
        validate=lambda x: len(x) > 0,
        invalid_message="URL cannot be empty",
    ).execute()

    console.print()

    # Parse URL to show info
    try:
        owner, repo, branch, path = parse_github_url(url)
        console.print(f"[dim]Repository: {owner}/{repo}[/dim]")
        console.print(f"[dim]Branch: {branch}[/dim]")
        console.print(f"[dim]Path: {path or '(root)'}[/dim]\n")
    except ValueError as e:
        console.print(f"[red]Error: {e}[/red]")
        return 1

    # Ask whether to save locally
    save_to_local = inquirer.confirm(
        message="Save to local skills/ directory?",
        default=True,
    ).execute()

    console.print()

    # Determine destination
    if save_to_local:
        project_root = get_project_root()
        skills_dir = project_root / "skills"

        # Ask for category
        category = inquirer.text(
            message="Enter category name (leave empty for root):",
            default="",
        ).execute()

        if category:
            dest_dir = skills_dir / category
        else:
            dest_dir = skills_dir
    else:
        dest_dir = Path.cwd() / ".tmp_skills"

    # Download skill
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Downloading skill...", total=None)
            skill_dir, metadata = download_skill_from_github(url, dest_dir)
            progress.update(task, completed=True)

        # Save metadata
        save_skill_metadata(
            skill_dir,
            url,
            metadata["owner"],
            metadata["repo"],
            metadata["branch"],
            metadata["path"],
        )

        # Validate
        if not validate_skill(skill_dir):
            console.print(f"[yellow]Warning: {skill_dir} does not contain SKILL.md, may not be a valid skill[/yellow]")

        console.print(f"[green]✓[/green] Skill downloaded to: {skill_dir}\n")

    except Exception as e:
        console.print(f"[red]Download failed: {e}[/red]")
        return 1

    # Ask whether to deploy
    should_deploy = inquirer.confirm(
        message="Deploy to AI agents?",
        default=True,
    ).execute()

    if not should_deploy:
        console.print("[yellow]Skipping deployment.[/yellow]")
        return 0

    console.print()

    # Detect agents
    existing_agents = detect_existing_agents()
    if existing_agents:
        console.print(f"[green]✓[/green] Detected {len(existing_agents)} installed agents\n")

    # Select deployment type
    deployment_type = select_deployment_type()
    console.print()

    # Select agents
    selected_agents = select_agents(existing_agents)
    if not selected_agents:
        console.print("[yellow]No agents selected.[/yellow]")
        return 0

    console.print()

    # Deploy
    success_count, fail_count = deploy_skill_to_agents(
        skill_dir, selected_agents, deployment_type, get_project_root() if deployment_type == "project" else None
    )

    # Clean up temporary files
    if not save_to_local and skill_dir.parent.name == ".tmp_skills":
        shutil.rmtree(skill_dir.parent, ignore_errors=True)

    console.print()

    # Show results
    if fail_count == 0:
        console.print(
            Panel.fit(
                f"[bold green]✓ Installation successful![/bold green]\n\n"
                f"Skill: {get_skill_name(skill_dir)}\n"
                f"Deployed to {success_count} agents",
                border_style="green",
            )
        )
    else:
        console.print(
            Panel.fit(
                f"[bold yellow]⚠ Installation completed with errors[/bold yellow]\n\n"
                f"Success: {success_count} | Failed: {fail_count}",
                border_style="yellow",
            )
        )

    return 0 if fail_count == 0 else 1


def cmd_uninstall() -> int:
    """
    Uninstall command - Remove skills from agents.

    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    console.print(
        Panel.fit(
            "[bold cyan]Uninstall Skills[/bold cyan]\nRemove skills from AI agents",
            border_style="cyan",
        )
    )

    # Detect agents
    existing_agents = detect_existing_agents()
    if not existing_agents:
        console.print("[red]No agents detected. Exiting.[/red]")
        return 1

    console.print(f"\n[green]✓[/green] Detected {len(existing_agents)} installed agents\n")

    # Select deployment type
    deployment_type = select_deployment_type()
    console.print()

    # Select agents
    selected_agents = select_agents(existing_agents)
    if not selected_agents:
        console.print("[yellow]No agents selected. Exiting.[/yellow]")
        return 0

    console.print()

    # For each selected agent, list installed skills
    all_skills = {}
    for agent_id in selected_agents:
        project_root = get_project_root() if deployment_type == "project" else None
        skills = list_installed_skills(agent_id, deployment_type, project_root)
        if skills:
            all_skills[agent_id] = skills

    if not all_skills:
        console.print("[yellow]No skills found in selected agents.[/yellow]")
        return 0

    # Build skill selection list grouped by agent
    choices = []
    for agent_id in sorted(all_skills.keys()):
        agent_name = get_agent_name(agent_id)
        choices.append(Separator(f"--- {agent_name} ---"))
        for skill in all_skills[agent_id]:
            choices.append(
                Choice(
                    value=(agent_id, skill),
                    name=skill,
                    enabled=False,
                )
            )

    selected_to_remove = inquirer.checkbox(
        message="Select skills to uninstall:",
        choices=choices,
        instruction="(Space to select, Enter to confirm)",
    ).execute()

    if not selected_to_remove:
        console.print("[yellow]No skills selected. Exiting.[/yellow]")
        return 0

    console.print()

    # Ask for deletion type
    deletion_type = inquirer.select(
        message="Select deletion type:",
        choices=[
            Choice(value="soft", name="Safe delete (move to trash) - Can be restored later"),
            Choice(value="hard", name="Hard delete (permanent) - Cannot be restored"),
        ],
        default="soft",
    ).execute()

    console.print()

    # Show summary
    console.print(f"[yellow]Will {deletion_type} delete {len(selected_to_remove)} skills:[/yellow]")
    for agent_id, skill in selected_to_remove:
        console.print(f"  • {get_agent_name(agent_id)}: {skill}")

    console.print()

    # Confirm
    confirm = inquirer.confirm(
        message=f"Confirm {deletion_type} deletion?",
        default=True,
    ).execute()

    if not confirm:
        console.print("[yellow]Deletion cancelled.[/yellow]")
        return 0

    console.print()

    # Perform deletion
    success_count = 0
    fail_count = 0
    project_root = get_project_root() if deployment_type == "project" else None

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Removing skills...", total=len(selected_to_remove))

        for agent_id, skill in selected_to_remove:
            if deletion_type == "soft":
                success = soft_delete_skill(skill, agent_id, deployment_type, project_root)
            else:
                success = hard_delete_skill(skill, agent_id, deployment_type, project_root)

            if success:
                success_count += 1
            else:
                fail_count += 1
            progress.advance(task)

    # Show results
    console.print()
    if fail_count == 0:
        console.print(
            Panel.fit(
                f"[bold green]✓ Uninstallation successful![/bold green]\n\n"
                f"Removed {success_count} skills\n"
                + ("[dim]Skills moved to trash and can be restored with 'sm restore'[/dim]" if deletion_type == "soft" else ""),
                border_style="green",
            )
        )
    else:
        console.print(
            Panel.fit(
                f"[bold yellow]⚠ Uninstallation completed with errors[/bold yellow]\n\n"
                f"Success: {success_count} | Failed: {fail_count}",
                border_style="yellow",
            )
        )

    return 0 if fail_count == 0 else 1


def cmd_restore() -> int:
    """
    Restore command - Restore deleted skills from trash.

    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    console.print(
        Panel.fit(
            "[bold cyan]Restore Skills[/bold cyan]\nRestore deleted skills from trash",
            border_style="cyan",
        )
    )

    # Detect agents
    existing_agents = detect_existing_agents()
    if not existing_agents:
        console.print("[red]No agents detected. Exiting.[/red]")
        return 1

    console.print(f"\n[green]✓[/green] Detected {len(existing_agents)} installed agents\n")

    # Select deployment type
    deployment_type = select_deployment_type()
    console.print()

    # Select agents
    selected_agents = select_agents(existing_agents)
    if not selected_agents:
        console.print("[yellow]No agents selected. Exiting.[/yellow]")
        return 0

    console.print()

    # For each selected agent, list trashed skills
    all_trashed = {}
    for agent_id in selected_agents:
        project_root = get_project_root() if deployment_type == "project" else None
        trashed = list_trashed_skills(agent_id, deployment_type, project_root)
        if trashed:
            all_trashed[agent_id] = trashed

    if not all_trashed:
        console.print("[yellow]No skills found in trash.[/yellow]")
        return 0

    # Build skill selection list grouped by agent
    choices = []
    for agent_id in sorted(all_trashed.keys()):
        agent_name = get_agent_name(agent_id)
        choices.append(Separator(f"--- {agent_name} ---"))
        for skill_info in all_trashed[agent_id]:
            skill_name = skill_info["skill_name"]
            deleted_at = skill_info["deleted_at"]
            timestamp = skill_info["timestamp_dir"]
            choices.append(
                Choice(
                    value=(agent_id, skill_name, timestamp),
                    name=f"{skill_name} (deleted: {deleted_at})",
                    enabled=False,
                )
            )

    selected_to_restore = inquirer.checkbox(
        message="Select skills to restore:",
        choices=choices,
        instruction="(Space to select, Enter to confirm)",
    ).execute()

    if not selected_to_restore:
        console.print("[yellow]No skills selected. Exiting.[/yellow]")
        return 0

    console.print()

    # Show summary
    console.print(f"[yellow]Will restore {len(selected_to_restore)} skills:[/yellow]")
    for agent_id, skill, _ in selected_to_restore:
        console.print(f"  • {get_agent_name(agent_id)}: {skill}")

    console.print()

    # Confirm
    confirm = inquirer.confirm(
        message="Confirm restoration?",
        default=True,
    ).execute()

    if not confirm:
        console.print("[yellow]Restoration cancelled.[/yellow]")
        return 0

    console.print()

    # Perform restoration
    success_count = 0
    fail_count = 0
    project_root = get_project_root() if deployment_type == "project" else None

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Restoring skills...", total=len(selected_to_restore))

        for agent_id, skill, timestamp in selected_to_restore:
            if restore_skill(skill, timestamp, agent_id, deployment_type, project_root):
                success_count += 1
            else:
                fail_count += 1
                console.print(f"[red]Failed to restore {skill} (may already exist)[/red]")
            progress.advance(task)

    # Show results
    console.print()
    if fail_count == 0:
        console.print(
            Panel.fit(
                f"[bold green]✓ Restoration successful![/bold green]\n\nRestored {success_count} skills",
                border_style="green",
            )
        )
    else:
        console.print(
            Panel.fit(
                f"[bold yellow]⚠ Restoration completed with errors[/bold yellow]\n\n"
                f"Success: {success_count} | Failed: {fail_count}",
                border_style="yellow",
            )
        )

    return 0 if fail_count == 0 else 1


def cmd_update() -> int:
    """
    Update command - Update skills from GitHub.

    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    # Check for --all flag
    update_all = len(sys.argv) > 2 and sys.argv[2] == "--all"

    console.print(
        Panel.fit(
            "[bold cyan]Update Skills[/bold cyan]\n"
            + ("Update all skills from GitHub" if update_all else "Update selected skills from GitHub"),
            border_style="cyan",
        )
    )

    # Detect agents
    existing_agents = detect_existing_agents()
    if not existing_agents:
        console.print("[red]No agents detected. Exiting.[/red]")
        return 1

    console.print(f"\n[green]✓[/green] Detected {len(existing_agents)} installed agents\n")

    # Select deployment type
    deployment_type = select_deployment_type()
    console.print()

    # Select agents
    selected_agents = select_agents(existing_agents)
    if not selected_agents:
        console.print("[yellow]No agents selected. Exiting.[/yellow]")
        return 0

    console.print()

    # Collect updatable skills from selected agents
    all_updatable = {}
    for agent_id in selected_agents:
        project_root = get_project_root() if deployment_type == "project" else None
        agent_path = get_agent_path(agent_id, deployment_type, project_root)
        updatable = list_updatable_skills(agent_path)
        if updatable:
            all_updatable[agent_id] = updatable

    if not all_updatable:
        console.print("[yellow]No updatable skills found (no GitHub metadata).[/yellow]")
        return 0

    # Select skills to update (unless --all flag)
    if update_all:
        skills_to_update = all_updatable
    else:
        # Build selection list
        choices = []
        for agent_id in sorted(all_updatable.keys()):
            agent_name = get_agent_name(agent_id)
            choices.append(Separator(f"--- {agent_name} ---"))
            for skill_info in all_updatable[agent_id]:
                skill_name = skill_info["skill_name"]
                metadata = skill_info["metadata"]
                updated_at = metadata.get("updated_at", "unknown")
                choices.append(
                    Choice(
                        value=(agent_id, skill_name),
                        name=f"{skill_name} (updated: {updated_at[:10]})",
                        enabled=False,
                    )
                )

        selected_to_update = inquirer.checkbox(
            message="Select skills to update:",
            choices=choices,
            instruction="(Space to select, Enter to confirm)",
        ).execute()

        if not selected_to_update:
            console.print("[yellow]No skills selected. Exiting.[/yellow]")
            return 0

        # Convert to dict format
        skills_to_update = {}
        for agent_id, skill_name in selected_to_update:
            if agent_id not in skills_to_update:
                skills_to_update[agent_id] = []
            skills_to_update[agent_id].append(skill_name)

    console.print()

    # Show summary
    total_count = sum(
        len(skills) if isinstance(skills, list) else len(all_updatable[agent_id])
        for agent_id, skills in skills_to_update.items()
    )
    console.print(f"[yellow]Will update {total_count} skills:[/yellow]")
    for agent_id in sorted(skills_to_update.keys()):
        agent_name = get_agent_name(agent_id)
        if isinstance(skills_to_update[agent_id], list):
            skill_list = skills_to_update[agent_id]
        else:
            skill_list = [s["skill_name"] for s in all_updatable[agent_id]]
        for skill in skill_list:
            console.print(f"  • {agent_name}: {skill}")

    console.print()

    # Confirm
    confirm = inquirer.confirm(
        message="Confirm update?",
        default=True,
    ).execute()

    if not confirm:
        console.print("[yellow]Update cancelled.[/yellow]")
        return 0

    console.print()

    # Perform updates
    total_success = 0
    total_failed = 0
    project_root = get_project_root() if deployment_type == "project" else None

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        for agent_id in skills_to_update.keys():
            if isinstance(skills_to_update[agent_id], list):
                # Specific skills selected
                skill_list = skills_to_update[agent_id]
                task = progress.add_task(f"Updating {get_agent_name(agent_id)}...", total=len(skill_list))

                for skill_name in skill_list:
                    if update_skill(skill_name, agent_id, deployment_type, project_root):
                        total_success += 1
                    else:
                        total_failed += 1
                    progress.advance(task)
            else:
                # Update all for this agent
                task = progress.add_task(f"Updating {get_agent_name(agent_id)}...", total=None)
                success, failed = update_all_skills(agent_id, deployment_type, project_root)
                total_success += success
                total_failed += failed
                progress.update(task, completed=True)

    # Show results
    console.print()
    if total_failed == 0:
        console.print(
            Panel.fit(
                f"[bold green]✓ Update successful![/bold green]\n\nUpdated {total_success} skills",
                border_style="green",
            )
        )
    else:
        console.print(
            Panel.fit(
                f"[bold yellow]⚠ Update completed with errors[/bold yellow]\n\n"
                f"Success: {total_success} | Failed: {total_failed}",
                border_style="yellow",
            )
        )

    return 0 if total_failed == 0 else 1


def cmd_list() -> int:
    """
    List command - List installed skills and versions.

    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    console.print(
        Panel.fit(
            "[bold cyan]List Installed Skills[/bold cyan]\nShow all installed skills with version information",
            border_style="cyan",
        )
    )

    # Detect agents
    existing_agents = detect_existing_agents()
    if not existing_agents:
        console.print("\n[red]No agents detected.[/red]")
        return 1

    console.print(f"\n[green]✓[/green] Detected {len(existing_agents)} installed agents\n")

    # Select deployment type
    deployment_type = select_deployment_type()
    console.print()

    project_root = get_project_root() if deployment_type == "project" else None

    # Collect all skills from all agents
    all_skills_data = {}
    for agent_id in sorted(existing_agents.keys()):
        agent_path = get_agent_path(agent_id, deployment_type, project_root)
        skills = list_installed_skills(agent_id, deployment_type, project_root)

        if skills:
            all_skills_data[agent_id] = []
            for skill_name in skills:
                skill_dir = agent_path / skill_name
                metadata = read_skill_metadata(skill_dir)

                if metadata:
                    # Has GitHub metadata
                    updated_at = metadata.get("updated_at", "unknown")
                    github_url = metadata.get("github_url", "")
                    version_info = updated_at[:19] if updated_at != "unknown" else "unknown"
                    source = "GitHub"
                else:
                    # No metadata, use file modification time
                    skill_md = skill_dir / "SKILL.md"
                    if skill_md.exists():
                        mtime = skill_md.stat().st_mtime
                        from datetime import datetime

                        version_info = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S")
                    else:
                        version_info = "unknown"
                    source = "Local"
                    github_url = ""

                all_skills_data[agent_id].append(
                    {
                        "name": skill_name,
                        "version": version_info,
                        "source": source,
                        "url": github_url,
                    }
                )

    if not all_skills_data:
        console.print("[yellow]No skills found in selected agents.[/yellow]")
        return 0

    # Display tables for each agent
    for agent_id in sorted(all_skills_data.keys()):
        agent_name = get_agent_name(agent_id)
        skills_list = all_skills_data[agent_id]

        table = Table(
            title=f"{agent_name} ({len(skills_list)} skills)",
            show_header=True,
            header_style="bold cyan",
        )
        table.add_column("Skill Name", style="green", no_wrap=True)
        table.add_column("Version/Updated", style="yellow")
        table.add_column("Source", style="blue")
        table.add_column("GitHub URL", style="dim", overflow="fold")

        for skill in sorted(skills_list, key=lambda x: x["name"]):
            table.add_row(
                skill["name"],
                skill["version"],
                skill["source"],
                skill["url"][:50] + "..." if len(skill["url"]) > 50 else skill["url"],
            )

        console.print(table)
        console.print()

    return 0


def cmd_discover(args: argparse.Namespace) -> int:
    """
    Discover command - Discover skills in a GitHub repository.

    Args:
        args: Parsed command line arguments

    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    console.print(
        Panel.fit(
            "[bold cyan]Discover Skills[/bold cyan]\nScan a GitHub repository for skills",
            border_style="cyan",
        )
    )

    # Get URL
    url = args.url
    if not url:
        url = inquirer.text(
            message="Enter GitHub URL to scan:",
            validate=lambda x: len(x) > 0,
            invalid_message="URL cannot be empty",
        ).execute()

    console.print()

    # Parse URL to show info
    try:
        owner, repo, branch, path = parse_github_url(url)
        console.print(f"[dim]Repository: {owner}/{repo}[/dim]")
        console.print(f"[dim]Branch: {branch}[/dim]")
        console.print(f"[dim]Path: {path or '(root)'}[/dim]\n")
    except ValueError as e:
        console.print(f"[red]Error: {e}[/red]")
        return 1

    # Discover skills
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Scanning repository for skills...", total=None)
            skills = discover_skills_in_repo(url)
            progress.update(task, completed=True)

        if not skills:
            console.print("[yellow]No skills found in the repository.[/yellow]")
            return 0

        # Display found skills
        table = Table(title=f"Found {len(skills)} Skills", show_header=True, header_style="bold cyan")
        table.add_column("Name", style="green", no_wrap=True)
        table.add_column("Path", style="yellow")
        table.add_column("URL", style="dim", overflow="fold")

        for skill in sorted(skills, key=lambda x: x["name"]):
            table.add_row(
                skill["name"],
                skill["path"],
                skill["url"][:60] + "..." if len(skill["url"]) > 60 else skill["url"],
            )

        console.print(table)
        console.print()

        console.print("[dim]Use 'sm install <url> --discover' to install all found skills[/dim]")
        return 0

    except Exception as e:
        console.print(f"[red]Discovery failed: {e}[/red]")
        return 1


def cmd_agents() -> int:
    """
    Agents command - List all supported agents.

    Returns:
        Exit code (0 for success)
    """
    console.print(
        Panel.fit(
            "[bold cyan]Supported Agents[/bold cyan]\nAll AI agents supported by skill-manager",
            border_style="cyan",
        )
    )

    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("Agent ID", style="green", no_wrap=True)
    table.add_column("Name", style="yellow")
    table.add_column("Project Path", style="dim")
    table.add_column("Global Path", style="dim")

    for agent_id in sorted(AGENTS.keys()):
        info = AGENTS[agent_id]
        global_path = info.get("global") or "N/A (project-only)"
        table.add_row(
            agent_id,
            info["name"],
            info["project"],
            global_path,
        )

    console.print(table)
    console.print(f"\n[dim]Total: {len(AGENTS)} agents supported[/dim]")
    return 0


def cmd_install_cli(args: argparse.Namespace) -> int:
    """
    Install command with CLI arguments - Download and deploy skills.

    Args:
        args: Parsed command line arguments

    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    # If no URL provided, fall back to interactive mode
    if not args.url:
        return cmd_install()

    console.print(
        Panel.fit(
            "[bold cyan]Install Skill[/bold cyan]\nDownload and deploy a skill from GitHub",
            border_style="cyan",
        )
    )

    url = args.url
    deployment_type = args.type
    use_symlink = not args.no_symlink
    skip_deploy = args.no_deploy
    # auto_confirm = args.yes  # Reserved for future use

    # Parse URL to show info
    try:
        owner, repo, branch, path = parse_github_url(url)
        console.print(f"[dim]Repository: {owner}/{repo}[/dim]")
        console.print(f"[dim]Branch: {branch}[/dim]")
        console.print(f"[dim]Path: {path or '(root)'}[/dim]\n")
    except ValueError as e:
        console.print(f"[red]Error: {e}[/red]")
        return 1

    # Determine destination directory
    if args.dest:
        dest_dir = args.dest
    else:
        dest_dir = get_system_temp_dir()

    dest_dir.mkdir(parents=True, exist_ok=True)
    console.print(f"[dim]Download location: {dest_dir}[/dim]\n")

    # Check symlink support
    if use_symlink and not is_symlink_supported():
        console.print("[yellow]Warning: Symlinks not supported on this system, will copy instead[/yellow]")
        use_symlink = False

    # Discover skills if requested
    if not args.no_discover:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Discovering skills...", total=None)
            skills_info = discover_skills_in_repo(url)
            progress.update(task, completed=True)

        if not skills_info:
            console.print("[yellow]No skills found in the repository.[/yellow]")
            return 0

        console.print(f"[green]✓[/green] Found {len(skills_info)} skills\n")

        # Download all skills
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Downloading skills...", total=None)
            downloaded = download_multiple_skills(skills_info, dest_dir)
            progress.update(task, completed=True)

        console.print(f"[green]✓[/green] Downloaded {len(downloaded)} skills\n")

        # Save metadata for each
        for skill_dir, metadata in downloaded:
            save_skill_metadata(
                skill_dir,
                metadata["url"],
                metadata["owner"],
                metadata["repo"],
                metadata["branch"],
                metadata["path"],
            )
    else:
        # Download single skill
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task("Downloading skill...", total=None)
                skill_dir, metadata = download_skill_from_github(url, dest_dir)
                progress.update(task, completed=True)

            save_skill_metadata(
                skill_dir,
                url,
                metadata["owner"],
                metadata["repo"],
                metadata["branch"],
                metadata["path"],
            )

            if not validate_skill(skill_dir):
                console.print(f"[yellow]Warning: {skill_dir} does not contain SKILL.md, may not be a valid skill[/yellow]")

            console.print(f"[green]✓[/green] Skill downloaded to: {skill_dir}\n")
            downloaded = [(skill_dir, metadata)]

        except Exception as e:
            console.print(f"[red]Download failed: {e}[/red]")
            return 1

    if skip_deploy:
        console.print("[dim]Skipping deployment (--no-deploy)[/dim]")
        return 0

    # Determine agents
    if args.agents:
        selected_agents = args.agents
        # Validate agents
        for agent_id in selected_agents:
            if agent_id not in AGENTS:
                console.print(f"[red]Unknown agent: {agent_id}[/red]")
                console.print(f"[dim]Available agents: {', '.join(sorted(AGENTS.keys()))}[/dim]")
                return 1
            if deployment_type == "global" and not supports_global_deployment(agent_id):
                console.print(f"[red]Agent '{agent_id}' does not support global deployment[/red]")
                return 1
    else:
        # Interactive selection
        existing_agents = detect_existing_agents()
        if existing_agents:
            console.print(f"[green]✓[/green] Detected {len(existing_agents)} installed agents\n")
        selected_agents = select_agents(existing_agents)
        if not selected_agents:
            console.print("[yellow]No agents selected.[/yellow]")
            return 0

    console.print()

    # Deploy
    project_root = get_project_root() if deployment_type == "project" else None
    total_success = 0
    total_fail = 0

    for skill_dir, _ in downloaded:
        success_count, fail_count = deploy_skill_to_agents(
            skill_dir, selected_agents, deployment_type, project_root, use_symlink
        )
        total_success += success_count
        total_fail += fail_count

    # Show results
    console.print()
    if total_fail == 0:
        link_type = "symlinked" if use_symlink else "deployed"
        console.print(
            Panel.fit(
                f"[bold green]✓ Installation successful![/bold green]\n\nSkills {link_type} to {total_success} agent(s)",
                border_style="green",
            )
        )
    else:
        console.print(
            Panel.fit(
                f"[bold yellow]⚠ Installation completed with errors[/bold yellow]\n\n"
                f"Success: {total_success} | Failed: {total_fail}",
                border_style="yellow",
            )
        )

    return 0 if total_fail == 0 else 1


def cmd_download_cli(args: argparse.Namespace) -> int:
    """
    Download command with CLI arguments.

    Args:
        args: Parsed command line arguments

    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    # If no URL provided, fall back to interactive mode
    if not args.url:
        return cmd_download()

    console.print(
        Panel.fit(
            "[bold cyan]Download Skill[/bold cyan]\nDownload a skill from GitHub",
            border_style="cyan",
        )
    )

    url = args.url

    # Parse URL to show info
    try:
        owner, repo, branch, path = parse_github_url(url)
        console.print(f"[dim]Repository: {owner}/{repo}[/dim]")
        console.print(f"[dim]Branch: {branch}[/dim]")
        console.print(f"[dim]Path: {path or '(root)'}[/dim]\n")
    except ValueError as e:
        console.print(f"[red]Error: {e}[/red]")
        return 1

    # Determine destination directory
    if args.dest:
        dest_dir = args.dest
    else:
        dest_dir = get_system_temp_dir()

    dest_dir.mkdir(parents=True, exist_ok=True)
    console.print(f"[dim]Download location: {dest_dir}[/dim]\n")

    # Discover skills if requested
    if not args.no_discover:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Discovering skills...", total=None)
            skills_info = discover_skills_in_repo(url)
            progress.update(task, completed=True)

        if not skills_info:
            console.print("[yellow]No skills found in the repository.[/yellow]")
            return 0

        console.print(f"[green]✓[/green] Found {len(skills_info)} skills\n")

        # Download all skills
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Downloading skills...", total=None)
            downloaded = download_multiple_skills(skills_info, dest_dir)
            progress.update(task, completed=True)

        console.print(f"[green]✓[/green] Downloaded {len(downloaded)} skills to {dest_dir}\n")

        # Save metadata for each
        for skill_dir, metadata in downloaded:
            save_skill_metadata(
                skill_dir,
                metadata["url"],
                metadata["owner"],
                metadata["repo"],
                metadata["branch"],
                metadata["path"],
            )

        return 0
    else:
        # Download single skill
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task("Downloading skill...", total=None)
                skill_dir, metadata = download_skill_from_github(url, dest_dir)
                progress.update(task, completed=True)

            save_skill_metadata(
                skill_dir,
                url,
                metadata["owner"],
                metadata["repo"],
                metadata["branch"],
                metadata["path"],
            )

            if not validate_skill(skill_dir):
                console.print(f"[yellow]Warning: {skill_dir} does not contain SKILL.md, may not be a valid skill[/yellow]")

            console.print(f"[green]✓[/green] Skill downloaded to: {skill_dir}\n")
            return 0

        except Exception as e:
            console.print(f"[red]Download failed: {e}[/red]")
            return 1


def main() -> int:
    """
    Main CLI entry point.

    Returns:
        Exit code
    """
    parser = create_parser()

    # Handle no arguments
    if len(sys.argv) < 2:
        console.print(
            Panel.fit(
                f"[bold cyan]Skill Manager[/bold cyan] [dim]v{__version__}[/dim]\n\n"
                "Usage:\n"
                "  sm install [url]   - Download and deploy skills\n"
                "  sm download [url]  - Download a skill from GitHub\n"
                "  sm deploy          - Deploy local skills to agents\n"
                "  sm discover [url]  - Discover skills in a repository\n"
                "  sm uninstall       - Remove skills from agents\n"
                "  sm restore         - Restore deleted skills from trash\n"
                "  sm update [--all]  - Update skills from GitHub\n"
                "  sm list            - List installed skills\n"
                "  sm agents          - List all supported agents\n"
                "  sm --version       - Show version information\n\n"
                "[bold]CLI Options:[/bold]\n"
                "  -a, --agent AGENT  - Target agent(s)\n"
                "  -t, --type TYPE    - Deployment type (global/project)\n"
                "  --no-symlink       - Disable symlinks, copy files instead\n"
                "  --no-discover      - Disable auto-discovery\n"
                "  -y, --yes          - Skip confirmation prompts\n\n"
                "[dim]Example: sm install https://github.com/cloudflare/skills -a windsurf -a cursor[/dim]",
                border_style="cyan",
            )
        )
        return 1

    args = parser.parse_args()

    try:
        if args.command == "download":
            return cmd_download_cli(args)
        elif args.command == "deploy":
            return cmd_deploy()
        elif args.command == "install":
            return cmd_install_cli(args)
        elif args.command == "discover":
            return cmd_discover(args)
        elif args.command == "uninstall":
            return cmd_uninstall()
        elif args.command == "restore":
            return cmd_restore()
        elif args.command == "update":
            return cmd_update()
        elif args.command == "list":
            return cmd_list()
        elif args.command == "agents":
            return cmd_agents()
        else:
            parser.print_help()
            return 1
    except KeyboardInterrupt:
        console.print("\n[yellow]Cancelled[/yellow]")
        return 130


if __name__ == "__main__":
    sys.exit(main())
