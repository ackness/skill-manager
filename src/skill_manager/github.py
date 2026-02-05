#!/usr/bin/env python3
"""
GitHub download functionality for skills.
Handles URL parsing and downloading files/directories from GitHub.
"""

import tempfile
from collections.abc import Callable
from pathlib import Path
from urllib.parse import urlparse

import httpx


def get_system_temp_dir() -> Path:
    """
    Get the system temporary directory (cross-platform).

    Returns:
        Path to the system temp directory
    """
    return Path(tempfile.gettempdir()) / "skill-manager"


def parse_github_url(url: str) -> tuple[str, str, str, str]:
    """
    Parse GitHub URL to extract repository information.

    Examples:
        https://github.com/owner/repo/tree/main/path/to/dir
        https://github.com/owner/repo/blob/main/path/to/file.py

    Args:
        url: GitHub URL

    Returns:
        Tuple of (owner, repo, branch, path)

    Raises:
        ValueError: If the URL is invalid
    """
    parsed = urlparse(url)
    parts = parsed.path.strip("/").split("/")

    if len(parts) < 2:
        raise ValueError("Invalid GitHub URL")

    owner = parts[0]
    repo = parts[1]
    branch = "main"
    path = ""

    if len(parts) > 3:
        # parts[2] is 'tree' or 'blob'
        # parts[3] is the branch name
        branch = parts[3]
        if len(parts) > 4:
            path = "/".join(parts[4:])

    return owner, repo, branch, path


def get_github_content(owner: str, repo: str, path: str, branch: str = "main") -> dict:
    """
    Fetch file or directory content using GitHub API.

    Args:
        owner: Repository owner
        repo: Repository name
        path: Path within the repository
        branch: Branch name (default: "main")

    Returns:
        JSON response from GitHub API

    Raises:
        httpx.HTTPStatusError: If the request fails
    """
    api_url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
    params = {"ref": branch}

    with httpx.Client() as client:
        response = client.get(api_url, params=params, follow_redirects=True)
        response.raise_for_status()
        return response.json()


def download_file(url: str, dest_path: Path) -> None:
    """
    Download a single file from a URL.

    Args:
        url: File download URL
        dest_path: Local destination path

    Raises:
        httpx.HTTPStatusError: If the download fails
    """
    with httpx.Client() as client:
        response = client.get(url, follow_redirects=True)
        response.raise_for_status()
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        dest_path.write_bytes(response.content)


def download_directory(owner: str, repo: str, path: str, dest_dir: Path, branch: str = "main") -> None:
    """
    Recursively download an entire directory from GitHub.

    Args:
        owner: Repository owner
        repo: Repository name
        path: Path to directory in the repository
        dest_dir: Local destination directory
        branch: Branch name (default: "main")

    Raises:
        httpx.HTTPStatusError: If the download fails
    """
    content = get_github_content(owner, repo, path, branch)

    for item in content:
        item_name = item["name"]
        item_path = item["path"]
        item_type = item["type"]

        if item_type == "file":
            download_url = item["download_url"]
            file_dest = dest_dir / item_name
            download_file(download_url, file_dest)
        elif item_type == "dir":
            subdir_dest = dest_dir / item_name
            download_directory(owner, repo, item_path, subdir_dest, branch)


def download_skill_from_github(url: str, dest_dir: Path, progress_callback: Callable | None = None) -> tuple[Path, dict]:
    """
    Download a skill from GitHub to a local directory.

    Args:
        url: GitHub URL (can be a directory or file)
        dest_dir: Destination directory
        progress_callback: Optional callback for progress updates

    Returns:
        Tuple of (path to downloaded skill directory, metadata dict with owner/repo/branch/path)

    Raises:
        ValueError: If the URL doesn't point to a directory
        httpx.HTTPStatusError: If the download fails
    """
    # Parse the URL
    owner, repo, branch, path = parse_github_url(url)

    # Get content information
    content = get_github_content(owner, repo, path, branch)

    # Must be a directory
    if not isinstance(content, list):
        raise ValueError("The provided URL does not point to a directory")

    # Determine skill name from path
    skill_name = path.split("/")[-1] if path else repo
    skill_dest = dest_dir / skill_name

    # Create destination directory
    skill_dest.mkdir(parents=True, exist_ok=True)

    # Download the directory
    if progress_callback:
        progress_callback(f"Downloading {skill_name}...")

    download_directory(owner, repo, path, skill_dest, branch)

    # Return path and metadata
    metadata = {
        "owner": owner,
        "repo": repo,
        "branch": branch,
        "path": path,
        "url": url,
    }

    return skill_dest, metadata


def discover_skills_in_repo(url: str, progress_callback: Callable | None = None) -> list[dict]:
    """
    Discover all SKILL.md files in a GitHub repository or directory.

    This function scans a GitHub URL to find all directories containing SKILL.md files,
    which conform to the skill specification.

    Args:
        url: GitHub URL (can be repo root or a subdirectory)
        progress_callback: Optional callback for progress updates

    Returns:
        List of dictionaries containing skill information:
        - name: skill directory name
        - path: path within the repository
        - url: full GitHub URL to the skill directory

    Raises:
        httpx.HTTPStatusError: If the API request fails
    """
    owner, repo, branch, path = parse_github_url(url)

    if progress_callback:
        progress_callback(f"Scanning {owner}/{repo}...")

    skills = []
    _scan_for_skills(owner, repo, branch, path, skills, progress_callback)
    return skills


def _scan_for_skills(
    owner: str,
    repo: str,
    branch: str,
    path: str,
    skills: list[dict],
    progress_callback: Callable | None = None,
) -> None:
    """
    Recursively scan a directory for SKILL.md files.

    Args:
        owner: Repository owner
        repo: Repository name
        branch: Branch name
        path: Current path being scanned
        skills: List to append found skills to
        progress_callback: Optional callback for progress updates
    """
    try:
        content = get_github_content(owner, repo, path, branch)
    except httpx.HTTPStatusError:
        return

    if not isinstance(content, list):
        return

    has_skill_md = False
    subdirs = []

    for item in content:
        item_name = item["name"]
        item_path = item["path"]
        item_type = item["type"]

        if item_type == "file" and item_name == "SKILL.md":
            has_skill_md = True
        elif item_type == "dir":
            subdirs.append(item_path)

    if has_skill_md:
        skill_name = path.split("/")[-1] if path else repo
        skill_url = f"https://github.com/{owner}/{repo}/tree/{branch}/{path}" if path else f"https://github.com/{owner}/{repo}"
        skills.append(
            {
                "name": skill_name,
                "path": path,
                "url": skill_url,
                "owner": owner,
                "repo": repo,
                "branch": branch,
            }
        )
        if progress_callback:
            progress_callback(f"Found skill: {skill_name}")

    # Recursively scan subdirectories
    for subdir in subdirs:
        _scan_for_skills(owner, repo, branch, subdir, skills, progress_callback)


def download_multiple_skills(
    skill_infos: list[dict],
    dest_dir: Path,
    progress_callback: Callable | None = None,
) -> list[tuple[Path, dict]]:
    """
    Download multiple skills from GitHub.

    Args:
        skill_infos: List of skill info dictionaries (from discover_skills_in_repo)
        dest_dir: Destination directory
        progress_callback: Optional callback for progress updates

    Returns:
        List of tuples (skill_path, metadata)
    """
    results = []
    dest_dir.mkdir(parents=True, exist_ok=True)

    for skill_info in skill_infos:
        owner = skill_info["owner"]
        repo = skill_info["repo"]
        branch = skill_info["branch"]
        path = skill_info["path"]
        skill_name = skill_info["name"]

        if progress_callback:
            progress_callback(f"Downloading {skill_name}...")

        skill_dest = dest_dir / skill_name
        skill_dest.mkdir(parents=True, exist_ok=True)

        try:
            download_directory(owner, repo, path, skill_dest, branch)

            metadata = {
                "owner": owner,
                "repo": repo,
                "branch": branch,
                "path": path,
                "url": skill_info["url"],
            }
            results.append((skill_dest, metadata))
        except Exception:
            # Skip failed downloads
            if progress_callback:
                progress_callback(f"Failed to download {skill_name}")

    return results
