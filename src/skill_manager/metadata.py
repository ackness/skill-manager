#!/usr/bin/env python3
"""
Skill metadata management.
Tracks installation source and update information for skills.
"""

import json
from datetime import UTC, datetime
from pathlib import Path


METADATA_FILENAME = ".skill_metadata.json"


def save_skill_metadata(
    skill_dir: Path,
    github_url: str,
    owner: str,
    repo: str,
    branch: str,
    path: str,
) -> None:
    """
    Save metadata for a skill installed from GitHub.

    Args:
        skill_dir: Path to the skill directory
        github_url: Original GitHub URL
        owner: Repository owner
        repo: Repository name
        branch: Branch name
        path: Path within the repository
    """
    metadata = {
        "source": "github",
        "github_url": github_url,
        "owner": owner,
        "repo": repo,
        "branch": branch,
        "path": path,
        "installed_at": datetime.now(UTC).isoformat(),
        "updated_at": datetime.now(UTC).isoformat(),
    }

    metadata_file = skill_dir / METADATA_FILENAME
    metadata_file.write_text(json.dumps(metadata, indent=2))


def read_skill_metadata(skill_dir: Path) -> dict | None:
    """
    Read metadata for a skill.

    Args:
        skill_dir: Path to the skill directory

    Returns:
        Metadata dictionary or None if not found
    """
    metadata_file = skill_dir / METADATA_FILENAME
    if not metadata_file.exists():
        return None

    try:
        return json.loads(metadata_file.read_text())
    except Exception:
        return None


def update_skill_metadata(skill_dir: Path) -> bool:
    """
    Update the 'updated_at' timestamp for a skill.

    Args:
        skill_dir: Path to the skill directory

    Returns:
        True if updated successfully, False otherwise
    """
    metadata = read_skill_metadata(skill_dir)
    if not metadata:
        return False

    metadata["updated_at"] = datetime.now(UTC).isoformat()

    metadata_file = skill_dir / METADATA_FILENAME
    try:
        metadata_file.write_text(json.dumps(metadata, indent=2))
        return True
    except Exception:
        return False


def list_updatable_skills(
    agent_path: Path,
) -> list[dict]:
    """
    List all skills that have GitHub metadata and can be updated.

    Args:
        agent_path: Path to the agent's skills directory

    Returns:
        List of dictionaries containing skill info and metadata
    """
    if not agent_path.exists():
        return []

    updatable_skills = []

    for skill_dir in agent_path.iterdir():
        if not skill_dir.is_dir() or skill_dir.name.startswith("."):
            continue

        # Check for SKILL.md
        if not (skill_dir / "SKILL.md").exists():
            continue

        # Check for metadata
        metadata = read_skill_metadata(skill_dir)
        if metadata and metadata.get("source") == "github":
            updatable_skills.append({
                "skill_name": skill_dir.name,
                "skill_path": skill_dir,
                "metadata": metadata,
            })

    return sorted(updatable_skills, key=lambda x: x["skill_name"])


def has_github_source(skill_dir: Path) -> bool:
    """
    Check if a skill was installed from GitHub.

    Args:
        skill_dir: Path to the skill directory

    Returns:
        True if the skill has GitHub metadata, False otherwise
    """
    metadata = read_skill_metadata(skill_dir)
    return metadata is not None and metadata.get("source") == "github"
