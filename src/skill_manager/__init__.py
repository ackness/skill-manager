"""
Skill Manager - Tool for managing AI agent skills.

This package provides functionality to download, deploy, and manage
skills across different AI agent platforms.
"""

__version__ = "0.1.0"

from .agents import AGENTS, detect_existing_agents, get_agent_name, get_agent_path
from .deployment import (
    deploy_multiple_skills,
    deploy_skill,
    deploy_skill_to_agents,
    update_all_skills,
    update_skill,
)
from .github import (
    download_skill_from_github,
    parse_github_url,
)
from .metadata import (
    has_github_source,
    list_updatable_skills,
    read_skill_metadata,
    save_skill_metadata,
    update_skill_metadata,
)
from .removal import (
    clean_trash,
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

__all__ = [
    # Version
    "__version__",
    # Agents
    "AGENTS",
    "detect_existing_agents",
    "get_agent_name",
    "get_agent_path",
    # Deployment
    "deploy_skill",
    "deploy_skill_to_agents",
    "deploy_multiple_skills",
    "update_skill",
    "update_all_skills",
    # GitHub
    "download_skill_from_github",
    "parse_github_url",
    # Metadata
    "save_skill_metadata",
    "read_skill_metadata",
    "update_skill_metadata",
    "list_updatable_skills",
    "has_github_source",
    # Removal
    "soft_delete_skill",
    "hard_delete_skill",
    "restore_skill",
    "list_installed_skills",
    "list_trashed_skills",
    "clean_trash",
    # Validation
    "validate_skill",
    "get_skill_name",
    "get_project_root",
    "scan_available_skills",
]
