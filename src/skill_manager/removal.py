#!/usr/bin/env python3
"""
Skill removal and recovery functionality.
Handles safe deletion (move to trash), hard deletion, and restoration.
"""

import shutil
from datetime import UTC, datetime
from pathlib import Path

from .agents import get_agent_path


def get_trash_dir(agent_id: str, deployment_type: str = "global", project_root: Path | None = None) -> Path:
    """
    Get the trash directory for an agent.

    Args:
        agent_id: Target agent identifier
        deployment_type: Either "global" or "project"
        project_root: Project root directory (required for project deployment)

    Returns:
        Path to the trash directory
    """
    agent_path = get_agent_path(agent_id, deployment_type, project_root)
    return agent_path.parent / ".trash"


def soft_delete_skill(
    skill_name: str,
    agent_id: str,
    deployment_type: str = "global",
    project_root: Path | None = None,
) -> bool:
    """
    Safely delete a skill by moving it to trash.

    Args:
        skill_name: Name of the skill to delete
        agent_id: Target agent identifier
        deployment_type: Either "global" or "project"
        project_root: Project root directory (required for project deployment)

    Returns:
        True if deletion succeeded, False otherwise
    """
    try:
        agent_path = get_agent_path(agent_id, deployment_type, project_root)
        skill_dir = agent_path / skill_name

        if not skill_dir.exists():
            return False

        # Create trash directory with timestamp subdirectory
        trash_dir = get_trash_dir(agent_id, deployment_type, project_root)
        timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
        trash_subdir = trash_dir / timestamp
        trash_subdir.mkdir(parents=True, exist_ok=True)

        # Move skill to trash
        trash_dest = trash_subdir / skill_name
        shutil.move(str(skill_dir), str(trash_dest))

        # Create metadata file
        metadata_file = trash_dest / ".trash_metadata"
        metadata_file.write_text(
            f"deleted_at: {timestamp}\n"
            f"original_path: {skill_dir}\n"
            f"agent_id: {agent_id}\n"
            f"deployment_type: {deployment_type}\n"
        )

        return True
    except Exception:
        return False


def hard_delete_skill(
    skill_name: str,
    agent_id: str,
    deployment_type: str = "global",
    project_root: Path | None = None,
) -> bool:
    """
    Permanently delete a skill.

    Args:
        skill_name: Name of the skill to delete
        agent_id: Target agent identifier
        deployment_type: Either "global" or "project"
        project_root: Project root directory (required for project deployment)

    Returns:
        True if deletion succeeded, False otherwise
    """
    try:
        agent_path = get_agent_path(agent_id, deployment_type, project_root)
        skill_dir = agent_path / skill_name

        if not skill_dir.exists():
            return False

        shutil.rmtree(skill_dir)
        return True
    except Exception:
        return False


def list_trashed_skills(
    agent_id: str,
    deployment_type: str = "global",
    project_root: Path | None = None,
) -> list[dict]:
    """
    List all skills in trash for an agent.

    Args:
        agent_id: Target agent identifier
        deployment_type: Either "global" or "project"
        project_root: Project root directory (required for project deployment)

    Returns:
        List of dictionaries containing skill information
    """
    trash_dir = get_trash_dir(agent_id, deployment_type, project_root)

    if not trash_dir.exists():
        return []

    trashed_skills = []

    # Iterate through timestamp directories
    for timestamp_dir in sorted(trash_dir.iterdir(), reverse=True):
        if not timestamp_dir.is_dir():
            continue

        # Each timestamp directory can contain multiple skills
        for skill_dir in timestamp_dir.iterdir():
            if not skill_dir.is_dir():
                continue

            # Read metadata if available
            metadata_file = skill_dir / ".trash_metadata"
            deleted_at = timestamp_dir.name
            if metadata_file.exists():
                metadata = metadata_file.read_text()
                for line in metadata.splitlines():
                    if line.startswith("deleted_at:"):
                        deleted_at = line.split(":", 1)[1].strip()

            trashed_skills.append({
                "skill_name": skill_dir.name,
                "deleted_at": deleted_at,
                "trash_path": skill_dir,
                "timestamp_dir": timestamp_dir.name,
            })

    return trashed_skills


def restore_skill(
    skill_name: str,
    timestamp: str,
    agent_id: str,
    deployment_type: str = "global",
    project_root: Path | None = None,
) -> bool:
    """
    Restore a skill from trash.

    Args:
        skill_name: Name of the skill to restore
        timestamp: Timestamp directory name
        agent_id: Target agent identifier
        deployment_type: Either "global" or "project"
        project_root: Project root directory (required for project deployment)

    Returns:
        True if restoration succeeded, False otherwise
    """
    try:
        trash_dir = get_trash_dir(agent_id, deployment_type, project_root)
        trashed_skill = trash_dir / timestamp / skill_name

        if not trashed_skill.exists():
            return False

        agent_path = get_agent_path(agent_id, deployment_type, project_root)
        restore_dest = agent_path / skill_name

        # Check if destination already exists
        if restore_dest.exists():
            return False

        # Move back from trash
        shutil.move(str(trashed_skill), str(restore_dest))

        # Remove metadata file if it exists
        metadata_file = restore_dest / ".trash_metadata"
        if metadata_file.exists():
            metadata_file.unlink()

        # Clean up empty timestamp directory
        timestamp_dir = trash_dir / timestamp
        if timestamp_dir.exists() and not any(timestamp_dir.iterdir()):
            timestamp_dir.rmdir()

        return True
    except Exception:
        return False


def clean_trash(
    agent_id: str,
    deployment_type: str = "global",
    project_root: Path | None = None,
) -> int:
    """
    Permanently delete all skills in trash for an agent.

    Args:
        agent_id: Target agent identifier
        deployment_type: Either "global" or "project"
        project_root: Project root directory (required for project deployment)

    Returns:
        Number of skills deleted
    """
    trash_dir = get_trash_dir(agent_id, deployment_type, project_root)

    if not trash_dir.exists():
        return 0

    count = 0
    for timestamp_dir in trash_dir.iterdir():
        if timestamp_dir.is_dir():
            for skill_dir in timestamp_dir.iterdir():
                if skill_dir.is_dir():
                    count += 1
            shutil.rmtree(timestamp_dir)

    return count


def list_installed_skills(
    agent_id: str,
    deployment_type: str = "global",
    project_root: Path | None = None,
) -> list[str]:
    """
    List all installed skills for an agent.

    Args:
        agent_id: Target agent identifier
        deployment_type: Either "global" or "project"
        project_root: Project root directory (required for project deployment)

    Returns:
        List of skill names
    """
    try:
        agent_path = get_agent_path(agent_id, deployment_type, project_root)

        if not agent_path.exists():
            return []

        skills = []
        for item in agent_path.iterdir():
            # Skip trash directory and non-directories
            if item.is_dir() and item.name != ".trash" and not item.name.startswith("."):
                # Check if it contains SKILL.md
                if (item / "SKILL.md").exists():
                    skills.append(item.name)

        return sorted(skills)
    except Exception:
        return []
