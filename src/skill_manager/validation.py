#!/usr/bin/env python3
"""
Skill validation utilities.
Validates skill directories and metadata.
"""

from pathlib import Path


def validate_skill(skill_dir: Path) -> bool:
    """
    Check if a directory contains a valid skill.

    A valid skill must contain a SKILL.md file.

    Args:
        skill_dir: Path to the skill directory

    Returns:
        True if the directory contains a valid skill, False otherwise
    """
    skill_md = skill_dir / "SKILL.md"
    return skill_md.exists()


def get_skill_name(skill_dir: Path) -> str:
    """
    Extract the skill name from a directory path.

    Args:
        skill_dir: Path to the skill directory

    Returns:
        The skill name (directory name)
    """
    return skill_dir.name


def get_project_root() -> Path:
    """
    Find the project root directory.

    Searches for a parent directory containing a 'skills' subdirectory.
    Falls back to the current working directory if not found.

    Returns:
        Path to the project root directory
    """
    current = Path.cwd()

    # Look for a parent directory containing 'skills'
    while current != current.parent:
        if (current / "skills").is_dir():
            return current
        current = current.parent

    # If not found, return current directory
    return Path.cwd()


def scan_available_skills(skills_dir: Path) -> list[Path]:
    """
    Scan a directory for available skills.

    A skill is identified by the presence of a SKILL.md file.

    Args:
        skills_dir: Path to the skills directory

    Returns:
        List of relative paths to skill directories (relative to skills_dir)
    """
    if not skills_dir.exists():
        return []

    skills = []
    for skill_path in skills_dir.rglob("SKILL.md"):
        skill_dir = skill_path.parent
        # Calculate path relative to skills directory
        rel_path = skill_dir.relative_to(skills_dir)
        skills.append(rel_path)

    return sorted(skills)
