#!/usr/bin/env python3
"""
GitHub download functionality for skills.
Handles URL parsing and downloading files/directories from GitHub.
Supports proxy, GitHub token, and GitHub mirrors.
"""

import os
from collections.abc import Callable
from pathlib import Path
from urllib.parse import urlparse

import httpx

# --- Environment variable keys ---
# GITHUB_TOKEN / GH_TOKEN: GitHub personal access token
# HTTP_PROXY / HTTPS_PROXY / ALL_PROXY: Proxy URL (e.g. http://127.0.0.1:7890)
# GITHUB_MIRROR: GitHub mirror base URL (e.g. https://ghproxy.com/https://github.com)
#                or API mirror (e.g. https://api.github.com replacement)

# Known GitHub mirror prefixes (prepend to raw github URLs)
_KNOWN_MIRRORS = [
    "https://mirror.ghproxy.com",
    "https://ghproxy.com",
    "https://gh-proxy.com",
    "https://github.moeyy.xyz",
]


def _get_proxy_config() -> dict[str, str] | None:
    """
    Get proxy configuration from environment variables.
    Supports HTTP_PROXY, HTTPS_PROXY, ALL_PROXY (case-insensitive).

    Returns:
        Proxy mapping dict or None
    """
    http_proxy = os.environ.get("HTTP_PROXY") or os.environ.get("http_proxy")
    https_proxy = os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy")
    all_proxy = os.environ.get("ALL_PROXY") or os.environ.get("all_proxy")

    proxies = {}
    if http_proxy:
        proxies["http://"] = http_proxy
    if https_proxy:
        proxies["https://"] = https_proxy
    if all_proxy:
        if "http://" not in proxies:
            proxies["http://"] = all_proxy
        if "https://" not in proxies:
            proxies["https://"] = all_proxy

    return proxies if proxies else None


def _get_github_mirror() -> str | None:
    """
    Get GitHub mirror URL from environment variable GITHUB_MIRROR.

    Returns:
        Mirror base URL or None
    """
    return os.environ.get("GITHUB_MIRROR") or os.environ.get("github_mirror")


def get_github_headers() -> dict[str, str]:
    """
    Get headers for GitHub API requests, including token if available.

    Returns:
        Dictionary of headers
    """
    headers = {"Accept": "application/vnd.github.v3+json"}
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token:
        headers["Authorization"] = f"token {token}"
    return headers


def create_http_client(timeout: float = 30.0) -> httpx.Client:
    """
    Create an httpx.Client with proxy and auth configuration.

    Args:
        timeout: Request timeout in seconds

    Returns:
        Configured httpx.Client
    """
    proxies = _get_proxy_config()
    return httpx.Client(
        proxy=proxies.get("https://") or proxies.get("http://") if proxies else None,
        timeout=timeout,
        follow_redirects=True,
    )


def _apply_mirror_to_url(url: str) -> str:
    """
    Apply GitHub mirror prefix to a URL if GITHUB_MIRROR is set.

    Args:
        url: Original GitHub URL

    Returns:
        Mirrored URL or original URL
    """
    mirror = _get_github_mirror()
    if not mirror:
        return url

    mirror = mirror.rstrip("/")

    # If mirror ends with a github.com URL prefix, it's a proxy-style mirror
    # e.g. https://ghproxy.com/https://github.com -> prepend to raw URLs
    if mirror.endswith("github.com") or mirror.endswith("raw.githubusercontent.com"):
        return url  # Don't double-wrap

    # Proxy-style: prepend mirror to the full URL
    # e.g. https://ghproxy.com/ + https://raw.githubusercontent.com/...
    return f"{mirror}/{url}"


def get_default_skills_dir() -> Path:
    """
    Get the default skills directory (~/.skill-manager/).
    Cross-platform compatible.

    Returns:
        Path to the default skills directory
    """
    return Path.home() / ".skill-manager" / "skills"


def get_system_temp_dir() -> Path:
    """
    Get the system temporary directory (cross-platform).
    Deprecated: Use get_default_skills_dir() instead.

    Returns:
        Path to the system temp directory
    """
    return get_default_skills_dir()


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
    headers = get_github_headers()

    with create_http_client() as client:
        response = client.get(api_url, params=params, headers=headers)
        if response.status_code == 403:
            remaining = response.headers.get("X-RateLimit-Remaining", "0")
            if remaining == "0":
                raise httpx.HTTPStatusError(
                    "GitHub API rate limit exceeded. Set GITHUB_TOKEN environment variable to increase limits.",
                    request=response.request,
                    response=response,
                )
        response.raise_for_status()
        return response.json()


def download_file(url: str, dest_path: Path) -> None:
    """
    Download a single file from a URL.
    Applies mirror and proxy settings automatically.

    Args:
        url: File download URL
        dest_path: Local destination path

    Raises:
        httpx.HTTPStatusError: If the download fails
    """
    mirrored_url = _apply_mirror_to_url(url)
    headers = get_github_headers()

    with create_http_client() as client:
        response = client.get(mirrored_url, headers=headers)
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


def discover_local_skills(local_path: Path) -> list[dict]:
    """
    Discover skills in a local directory by scanning for SKILL.md files.

    Args:
        local_path: Path to local directory to scan

    Returns:
        List of dicts with keys: name, path (absolute), url (empty)
    """
    skills = []
    if not local_path.is_dir():
        return skills

    # Check if the directory itself contains SKILL.md
    if (local_path / "SKILL.md").exists():
        skills.append(
            {
                "name": local_path.name,
                "path": str(local_path),
                "url": "",
                "local": True,
            }
        )
        return skills

    # Scan subdirectories
    for child in sorted(local_path.iterdir()):
        if child.is_dir() and (child / "SKILL.md").exists():
            skills.append(
                {
                    "name": child.name,
                    "path": str(child),
                    "url": "",
                    "local": True,
                }
            )

    return skills


def get_network_info() -> dict[str, str | None]:
    """
    Get current network configuration info for display.

    Returns:
        Dict with proxy, mirror, token status
    """
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    proxy = _get_proxy_config()
    mirror = _get_github_mirror()

    return {
        "token": "***" + token[-4:] if token and len(token) > 4 else ("set" if token else None),
        "proxy": (proxy.get("https://") or proxy.get("http://")) if proxy else None,
        "mirror": mirror,
    }


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

    Raises:
        httpx.HTTPStatusError: If the request fails (including rate limiting)
    """
    content = get_github_content(owner, repo, path, branch)

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
