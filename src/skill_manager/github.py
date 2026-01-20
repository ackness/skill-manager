#!/usr/bin/env python3
"""
GitHub download functionality for skills.
Handles URL parsing and downloading files/directories from GitHub.
"""

from collections.abc import Callable
from pathlib import Path
from urllib.parse import urlparse

import httpx


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


def download_directory(
    owner: str, repo: str, path: str, dest_dir: Path, branch: str = "main"
) -> None:
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


def download_skill_from_github(
    url: str, dest_dir: Path, progress_callback: Callable | None = None
) -> tuple[Path, dict]:
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
