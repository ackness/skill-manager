"""
Skill Manager - Tool for managing AI agent skills.

This package provides functionality to download, deploy, and manage
skills across different AI agent platforms.
"""

__version__ = "0.3.0"

from .agents import AGENTS, detect_existing_agents, get_agent_name, get_agent_path, supports_global_deployment
from .deployment import (
    create_symlink,
    deploy_multiple_skills,
    deploy_skill,
    deploy_skill_to_agents,
    is_skill_symlink,
    is_symlink_supported,
    remove_symlink,
    update_all_skills,
    update_skill,
)
from .github import (
    discover_local_skills,
    discover_skills_in_repo,
    download_multiple_skills,
    download_skill_from_github,
    get_default_skills_dir,
    get_network_info,
    get_system_temp_dir,
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
    "supports_global_deployment",
    # Deployment
    "deploy_skill",
    "deploy_skill_to_agents",
    "deploy_multiple_skills",
    "update_skill",
    "update_all_skills",
    "is_symlink_supported",
    "create_symlink",
    "remove_symlink",
    "is_skill_symlink",
    # GitHub
    "download_skill_from_github",
    "download_multiple_skills",
    "discover_skills_in_repo",
    "discover_local_skills",
    "get_default_skills_dir",
    "get_network_info",
    "get_system_temp_dir",
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
