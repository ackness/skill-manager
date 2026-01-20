#!/usr/bin/env python3
"""
Skill deployment functionality.
Handles copying skills to agent directories.
"""

import shutil
from collections.abc import Callable
from pathlib import Path

from .agents import get_agent_path
from .github import download_skill_from_github
from .metadata import (
    list_updatable_skills,
    read_skill_metadata,
    save_skill_metadata,
    update_skill_metadata,
)


def deploy_skill(
    skill_path: Path,
    skills_dir: Path,
    agent_id: str,
    deployment_type: str = "global",
    project_root: Path | None = None,
) -> bool:
    """
    Deploy a single skill to an agent's directory.

    Args:
        skill_path: Relative path to the skill (relative to skills_dir)
        skills_dir: Base skills directory
        agent_id: Target agent identifier
        deployment_type: Either "global" or "project"
        project_root: Project root directory (required for project deployment)

    Returns:
        True if deployment succeeded, False otherwise
    """
    try:
        source = skills_dir / skill_path
        target_base = get_agent_path(agent_id, deployment_type, project_root)
        target = target_base / skill_path

        # Ensure target directory exists
        target.parent.mkdir(parents=True, exist_ok=True)

        # Remove existing skill if present
        if target.exists():
            shutil.rmtree(target)

        # Copy the skill directory
        shutil.copytree(source, target)
        return True
    except Exception:
        return False


def deploy_skill_to_agents(
    skill_dir: Path,
    agents: list[str],
    deployment_type: str = "global",
    project_root: Path | None = None,
) -> tuple[int, int]:
    """
    Deploy a skill directory to multiple agents.

    This is used when installing a skill directly from GitHub.

    Args:
        skill_dir: Path to the skill directory
        agents: List of agent IDs to deploy to
        deployment_type: Either "global" or "project"
        project_root: Project root directory (required for project deployment)

    Returns:
        Tuple of (success_count, failure_count)
    """
    skill_name = skill_dir.name
    success_count = 0
    fail_count = 0

    for agent_id in agents:
        try:
            target_base = get_agent_path(agent_id, deployment_type, project_root)
            target_dir = target_base / skill_name

            # Ensure target directory exists
            target_base.mkdir(parents=True, exist_ok=True)

            # Remove existing skill if present
            if target_dir.exists():
                shutil.rmtree(target_dir)

            # Copy the skill directory
            shutil.copytree(skill_dir, target_dir)
            success_count += 1
        except Exception:
            fail_count += 1

    return success_count, fail_count


def deploy_multiple_skills(
    skill_paths: list[Path],
    skills_dir: Path,
    agents: list[str],
    deployment_type: str = "global",
    project_root: Path | None = None,
    progress_callback: Callable | None = None,
) -> tuple[int, int]:
    """
    Deploy multiple skills to multiple agents.

    Args:
        skill_paths: List of relative skill paths (relative to skills_dir)
        skills_dir: Base skills directory
        agents: List of agent IDs to deploy to
        deployment_type: Either "global" or "project"
        project_root: Project root directory (required for project deployment)
        progress_callback: Optional callback for progress updates

    Returns:
        Tuple of (total_deployed, total_failed)
    """
    total_deployed = 0
    total_failed = 0

    for agent_id in agents:
        for skill_path in skill_paths:
            if progress_callback:
                progress_callback(agent_id, skill_path)

            if deploy_skill(skill_path, skills_dir, agent_id, deployment_type, project_root):
                total_deployed += 1
            else:
                total_failed += 1

    return total_deployed, total_failed


def update_skill(
    skill_name: str,
    agent_id: str,
    deployment_type: str = "global",
    project_root: Path | None = None,
    progress_callback: Callable | None = None,
) -> bool:
    """
    Update a single skill from its GitHub source.

    Args:
        skill_name: Name of the skill to update
        agent_id: Target agent identifier
        deployment_type: Either "global" or "project"
        project_root: Project root directory (required for project deployment)
        progress_callback: Optional callback for progress updates

    Returns:
        True if update succeeded, False otherwise
    """
    try:
        agent_path = get_agent_path(agent_id, deployment_type, project_root)
        skill_dir = agent_path / skill_name

        if not skill_dir.exists():
            return False

        # Read metadata
        metadata = read_skill_metadata(skill_dir)
        if not metadata or metadata.get("source") != "github":
            return False

        # Get GitHub info from metadata
        github_url = metadata["github_url"]

        if progress_callback:
            progress_callback(f"Updating {skill_name}...")

        # Download updated version to temporary location
        temp_dir = agent_path.parent / ".tmp_update"
        temp_dir.mkdir(exist_ok=True)

        try:
            updated_skill_dir, _ = download_skill_from_github(github_url, temp_dir)

            # Backup current version
            backup_dir = agent_path.parent / ".backup"
            backup_dir.mkdir(exist_ok=True)
            backup_path = backup_dir / skill_name

            if backup_path.exists():
                shutil.rmtree(backup_path)
            shutil.copytree(skill_dir, backup_path)

            # Remove old version
            shutil.rmtree(skill_dir)

            # Move updated version
            shutil.move(str(updated_skill_dir), str(skill_dir))

            # Update metadata timestamp
            update_skill_metadata(skill_dir)

            # Clean up
            shutil.rmtree(temp_dir, ignore_errors=True)
            shutil.rmtree(backup_dir, ignore_errors=True)

            return True

        except Exception:
            # Restore from backup if update failed
            backup_dir = agent_path.parent / ".backup"
            backup_path = backup_dir / skill_name
            if backup_path.exists():
                if skill_dir.exists():
                    shutil.rmtree(skill_dir)
                shutil.copytree(backup_path, skill_dir)
            shutil.rmtree(temp_dir, ignore_errors=True)
            shutil.rmtree(backup_dir, ignore_errors=True)
            return False

    except Exception:
        return False


def update_all_skills(
    agent_id: str,
    deployment_type: str = "global",
    project_root: Path | None = None,
    progress_callback: Callable | None = None,
) -> tuple[int, int]:
    """
    Update all skills from GitHub for an agent.

    Args:
        agent_id: Target agent identifier
        deployment_type: Either "global" or "project"
        project_root: Project root directory (required for project deployment)
        progress_callback: Optional callback for progress updates

    Returns:
        Tuple of (success_count, failure_count)
    """
    agent_path = get_agent_path(agent_id, deployment_type, project_root)
    updatable_skills = list_updatable_skills(agent_path)

    success_count = 0
    fail_count = 0

    for skill_info in updatable_skills:
        skill_name = skill_info["skill_name"]

        if update_skill(skill_name, agent_id, deployment_type, project_root, progress_callback):
            success_count += 1
        else:
            fail_count += 1

    return success_count, fail_count
