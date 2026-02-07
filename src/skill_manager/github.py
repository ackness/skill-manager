#!/usr/bin/env python3
"""
GitHub download functionality for skills.
Handles URL parsing and downloading files/directories from GitHub.
Supports proxy, GitHub token, and GitHub mirrors.
"""

import os
import shutil
import subprocess
import sys
import tempfile
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

_git_available: bool | None = None


def _is_git_available() -> bool:
    """Check if git is available on the system. Caches the result."""
    global _git_available  # noqa: PLW0603
    if _git_available is None:
        try:
            creationflags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
            subprocess.run(
                ["git", "--version"],
                capture_output=True,
                timeout=5,
                creationflags=creationflags,
            )
            _git_available = True
        except Exception:
            _git_available = False
    return _git_available


def _build_clone_url(owner: str, repo: str) -> str:
    """Build HTTPS clone URL with optional token auth and mirror support."""
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    mirror = _get_github_mirror()

    if mirror:
        mirror = mirror.rstrip("/")
        # For proxy-style mirrors, construct URL through the mirror
        base = f"{mirror}/https://github.com/{owner}/{repo}.git"
    elif token:
        base = f"https://x-access-token:{token}@github.com/{owner}/{repo}.git"
    else:
        base = f"https://github.com/{owner}/{repo}.git"

    return base


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


def _get_git_env() -> dict[str, str]:
    """Build environment dict for git subprocess, inheriting proxy settings."""
    env = os.environ.copy()
    proxy = _get_proxy_config()
    if proxy:
        if "https://" in proxy:
            env.setdefault("HTTPS_PROXY", proxy["https://"])
        if "http://" in proxy:
            env.setdefault("HTTP_PROXY", proxy["http://"])
    return env


def _download_via_git(
    owner: str,
    repo: str,
    branch: str,
    skill_paths: list[str],
    dest_dir: Path,
    progress_callback: Callable | None = None,
) -> list[tuple[Path, dict]]:
    """Download multiple skills via git sparse-checkout (single network operation)."""
    clone_url = _build_clone_url(owner, repo)
    tmpdir = tempfile.mkdtemp(prefix="skill-git-")
    creationflags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
    env = _get_git_env()

    try:
        subprocess.run(
            ["git", "clone", "--depth", "1", "--filter=blob:none", "--sparse", "--branch", branch, clone_url, tmpdir],
            capture_output=True,
            check=True,
            timeout=60,
            creationflags=creationflags,
            env=env,
        )
        subprocess.run(
            ["git", "-C", tmpdir, "sparse-checkout", "set", *skill_paths],
            capture_output=True,
            check=True,
            timeout=30,
            creationflags=creationflags,
            env=env,
        )

        results = []
        for skill_path in skill_paths:
            skill_name = skill_path.split("/")[-1] if skill_path else repo
            src = Path(tmpdir) / skill_path
            if not src.is_dir():
                continue
            skill_dest = dest_dir / skill_name
            if skill_dest.exists():
                shutil.rmtree(skill_dest)
            shutil.copytree(src, skill_dest)

            metadata = {
                "owner": owner,
                "repo": repo,
                "branch": branch,
                "path": skill_path,
                "url": f"https://github.com/{owner}/{repo}/tree/{branch}/{skill_path}",
            }
            results.append((skill_dest, metadata))
            if progress_callback:
                progress_callback(f"Downloaded {skill_name}")

        return results
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def _download_via_raw_urls(
    owner: str,
    repo: str,
    branch: str,
    skill_path: str,
    dest_dir: Path,
    client: httpx.Client,
) -> None:
    """Download a single skill using Tree API + raw.githubusercontent.com URLs."""
    tree, truncated = get_repo_tree(owner, repo, branch)
    if truncated:
        raise ValueError("Tree is truncated, cannot use raw URL download")

    prefix = skill_path + "/" if skill_path else ""
    headers = get_github_headers()
    found = False

    for entry in tree:
        entry_path = entry.get("path", "")
        if entry.get("type") != "blob":
            continue
        if not entry_path.startswith(prefix):
            continue

        found = True
        relative = entry_path[len(prefix) :]
        raw_url = f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{entry_path}"
        raw_url = _apply_mirror_to_url(raw_url)

        file_dest = dest_dir / relative
        file_dest.parent.mkdir(parents=True, exist_ok=True)
        response = client.get(raw_url, headers=headers)
        response.raise_for_status()
        file_dest.write_bytes(response.content)

    if not found:
        raise ValueError(f"No files found under path: {skill_path}")


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


def download_file(url: str, dest_path: Path, client: httpx.Client | None = None) -> None:
    """
    Download a single file from a URL.
    Applies mirror and proxy settings automatically.

    Args:
        url: File download URL
        dest_path: Local destination path
        client: Optional shared httpx.Client to reuse connections

    Raises:
        httpx.HTTPStatusError: If the download fails
    """
    mirrored_url = _apply_mirror_to_url(url)
    headers = get_github_headers()

    def _do_download(c: httpx.Client) -> None:
        response = c.get(mirrored_url, headers=headers)
        response.raise_for_status()
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        dest_path.write_bytes(response.content)

    if client:
        _do_download(client)
    else:
        with create_http_client() as c:
            _do_download(c)


def download_directory(
    owner: str,
    repo: str,
    path: str,
    dest_dir: Path,
    branch: str = "main",
    client: httpx.Client | None = None,
) -> None:
    """
    Recursively download an entire directory from GitHub.

    Args:
        owner: Repository owner
        repo: Repository name
        path: Path to directory in the repository
        dest_dir: Local destination directory
        branch: Branch name (default: "main")
        client: Optional shared httpx.Client to reuse connections

    Raises:
        httpx.HTTPStatusError: If the download fails
    """
    if client:
        api_url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
        params = {"ref": branch}
        headers = get_github_headers()
        response = client.get(api_url, params=params, headers=headers)
        response.raise_for_status()
        content = response.json()
    else:
        content = get_github_content(owner, repo, path, branch)

    for item in content:
        item_name = item["name"]
        item_path = item["path"]
        item_type = item["type"]

        if item_type == "file":
            download_url = item["download_url"]
            file_dest = dest_dir / item_name
            download_file(download_url, file_dest, client)
        elif item_type == "dir":
            subdir_dest = dest_dir / item_name
            download_directory(owner, repo, item_path, subdir_dest, branch, client)


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

    Uses a 2-tier strategy:
    1. Tree API + raw URLs (one API call + parallel file downloads)
    2. Contents API recursive (current, slow but always works)

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
    owner, repo, branch, path = parse_github_url(url)
    skill_name = path.split("/")[-1] if path else repo
    skill_dest = dest_dir / skill_name
    metadata = {
        "owner": owner,
        "repo": repo,
        "branch": branch,
        "path": path,
        "url": url,
    }

    if progress_callback:
        progress_callback(f"Downloading {skill_name}...")

    # Tier 1: Tree API + raw URLs
    try:
        skill_dest.mkdir(parents=True, exist_ok=True)
        with create_http_client() as client:
            _download_via_raw_urls(owner, repo, branch, path, skill_dest, client)
        return skill_dest, metadata
    except Exception:
        # Clean up partial download before fallback
        if skill_dest.exists():
            shutil.rmtree(skill_dest, ignore_errors=True)

    # Tier 2: Contents API fallback
    content = get_github_content(owner, repo, path, branch)
    if not isinstance(content, list):
        raise ValueError("The provided URL does not point to a directory")

    skill_dest.mkdir(parents=True, exist_ok=True)
    with create_http_client() as client:
        download_directory(owner, repo, path, skill_dest, branch, client)

    return skill_dest, metadata


def get_repo_tree(owner: str, repo: str, branch: str = "main") -> tuple[list[dict], bool]:
    """
    Fetch the entire repository file tree using the Git Trees API.

    Args:
        owner: Repository owner
        repo: Repository name
        branch: Branch name (default: "main")

    Returns:
        Tuple of (tree entries list, truncated flag)

    Raises:
        httpx.HTTPStatusError: If the request fails
    """
    api_url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/{branch}"
    params = {"recursive": "1"}
    headers = get_github_headers()

    with create_http_client() as client:
        response = client.get(api_url, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()
        return data.get("tree", []), data.get("truncated", False)


def _discover_via_tree(
    owner: str,
    repo: str,
    branch: str,
    path: str,
    progress_callback: Callable | None = None,
) -> list[dict]:
    """
    Discover skills using the Git Trees API (single API call).

    Args:
        owner: Repository owner
        repo: Repository name
        branch: Branch name
        path: Path prefix to filter (empty string for repo root)
        progress_callback: Optional callback for progress updates

    Returns:
        List of skill info dicts

    Raises:
        httpx.HTTPStatusError: If the request fails
        ValueError: If the tree is truncated (caller should fall back)
    """
    tree, truncated = get_repo_tree(owner, repo, branch)
    if truncated:
        raise ValueError("Tree is truncated, falling back to recursive scan")

    skills = []
    for entry in tree:
        entry_path = entry.get("path", "")
        if not entry_path.endswith("/SKILL.md") and entry_path != "SKILL.md":
            continue
        # If a path prefix is specified, only include entries under that prefix
        if path and not entry_path.startswith(path + "/") and entry_path != path + "/SKILL.md":
            continue

        # Parent directory is the skill directory
        if "/" in entry_path:
            skill_dir = entry_path.rsplit("/", 1)[0]
        else:
            skill_dir = ""

        skill_name = skill_dir.split("/")[-1] if skill_dir else repo
        skill_url = (
            f"https://github.com/{owner}/{repo}/tree/{branch}/{skill_dir}"
            if skill_dir
            else f"https://github.com/{owner}/{repo}"
        )
        skills.append(
            {
                "name": skill_name,
                "path": skill_dir,
                "url": skill_url,
                "owner": owner,
                "repo": repo,
                "branch": branch,
            }
        )
        if progress_callback:
            progress_callback(f"Found skill: {skill_name}")

    return skills


def discover_skills_in_repo(url: str, progress_callback: Callable | None = None) -> list[dict]:
    """
    Discover all SKILL.md files in a GitHub repository or directory.

    Uses the Git Trees API for a single-call scan of the entire repo.
    Falls back to recursive Contents API scanning if the tree is truncated
    or the Trees API fails.

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

    # Try fast path: single API call via Git Trees
    try:
        return _discover_via_tree(owner, repo, branch, path, progress_callback)
    except Exception:
        pass

    # Fallback: recursive Contents API scan with shared HTTP client
    skills: list[dict] = []
    with create_http_client() as client:
        _scan_for_skills(owner, repo, branch, path, skills, progress_callback, client)
    return skills


def _scan_for_skills(
    owner: str,
    repo: str,
    branch: str,
    path: str,
    skills: list[dict],
    progress_callback: Callable | None = None,
    client: httpx.Client | None = None,
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
        client: Optional shared httpx.Client to reuse connections

    Raises:
        httpx.HTTPStatusError: If the request fails (including rate limiting)
    """
    api_url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
    params = {"ref": branch}
    headers = get_github_headers()

    if client:
        response = client.get(api_url, params=params, headers=headers)
        response.raise_for_status()
        content = response.json()
    else:
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
        _scan_for_skills(owner, repo, branch, subdir, skills, progress_callback, client)


def download_multiple_skills(
    skill_infos: list[dict],
    dest_dir: Path,
    progress_callback: Callable | None = None,
) -> list[tuple[Path, dict]]:
    """
    Download multiple skills from GitHub.

    Uses a 3-tier strategy:
    1. git sparse-checkout (fastest, single network operation for all skills)
    2. Tree API + raw URLs (one API call + file downloads per skill)
    3. Contents API recursive (slow but always works)

    Args:
        skill_infos: List of skill info dictionaries (from discover_skills_in_repo)
        dest_dir: Destination directory
        progress_callback: Optional callback for progress updates

    Returns:
        List of tuples (skill_path, metadata)
    """
    if not skill_infos:
        return []

    dest_dir.mkdir(parents=True, exist_ok=True)

    # Extract common repo info (all skills should be from the same repo)
    first = skill_infos[0]
    owner, repo, branch = first["owner"], first["repo"], first["branch"]
    skill_paths = [s["path"] for s in skill_infos]

    # Tier 1: git sparse-checkout (all skills at once)
    if _is_git_available():
        try:
            if progress_callback:
                progress_callback("Downloading via git sparse-checkout...")
            return _download_via_git(owner, repo, branch, skill_paths, dest_dir, progress_callback)
        except Exception:
            if progress_callback:
                progress_callback("Git download failed, trying raw URLs...")

    # Tier 2: Tree API + raw URLs (per skill, shared client)
    try:
        results: list[tuple[Path, dict]] = []
        with create_http_client() as client:
            for skill_info in skill_infos:
                path = skill_info["path"]
                skill_name = skill_info["name"]

                if progress_callback:
                    progress_callback(f"Downloading {skill_name}...")

                skill_dest = dest_dir / skill_name
                skill_dest.mkdir(parents=True, exist_ok=True)

                _download_via_raw_urls(owner, repo, branch, path, skill_dest, client)

                metadata = {
                    "owner": owner,
                    "repo": repo,
                    "branch": branch,
                    "path": path,
                    "url": skill_info["url"],
                }
                results.append((skill_dest, metadata))
        return results
    except Exception:
        if progress_callback:
            progress_callback("Raw URL download failed, using Contents API...")
        # Clean up any partial downloads from tier 2
        for skill_info in skill_infos:
            partial = dest_dir / skill_info["name"]
            if partial.exists():
                shutil.rmtree(partial, ignore_errors=True)

    # Tier 3: Contents API fallback (original logic with shared client)
    results = []
    with create_http_client() as client:
        for skill_info in skill_infos:
            path = skill_info["path"]
            skill_name = skill_info["name"]

            if progress_callback:
                progress_callback(f"Downloading {skill_name}...")

            skill_dest = dest_dir / skill_name
            skill_dest.mkdir(parents=True, exist_ok=True)

            try:
                download_directory(owner, repo, path, skill_dest, branch, client)

                metadata = {
                    "owner": owner,
                    "repo": repo,
                    "branch": branch,
                    "path": path,
                    "url": skill_info["url"],
                }
                results.append((skill_dest, metadata))
            except Exception:
                if progress_callback:
                    progress_callback(f"Failed to download {skill_name}")

    return results
