import logging
import os
import re
import shutil
import subprocess
import tempfile
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

_DEFAULT_KEY_PATH = os.path.expanduser("~/.ssh/memo_deploy_key")


def ensure_deploy_key() -> str:
    """
    Ensures an SSH deploy key exists on disk.

    Uses the path from GITHUB_DEPLOY_KEY_PATH env var, falling back to
    ~/.ssh/memo_deploy_key. Generates an ed25519 key pair if the private
    key file does not already exist.

    Returns the path to the private key and logs the public key so it can
    be added to GitHub as a deploy key.
    """
    key_path = os.getenv("GITHUB_DEPLOY_KEY_PATH", _DEFAULT_KEY_PATH)

    if os.path.isfile(key_path):
        logger.info("SSH deploy key already exists at %s", key_path)
        return key_path

    os.makedirs(os.path.dirname(key_path), exist_ok=True)

    result = subprocess.run(
        ["ssh-keygen", "-t", "ed25519", "-f", key_path, "-N", "", "-C", "memo-core-deploy"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"ssh-keygen failed: {result.stderr.strip()}")

    os.chmod(key_path, 0o600)

    pub_key_path = f"{key_path}.pub"
    try:
        with open(pub_key_path, "r") as f:
            pub_key = f.read().strip()
        logger.info(
            "Generated new SSH deploy key at %s\n"
            "Add this public key as a read-only deploy key in each GitHub repo "
            "(Settings -> Deploy keys):\n\n%s\n",
            key_path,
            pub_key,
        )
    except OSError:
        logger.warning("Could not read public key at %s", pub_key_path)

    return key_path


def get_public_deploy_key() -> str:
    key_path = os.getenv("GITHUB_DEPLOY_KEY_PATH", _DEFAULT_KEY_PATH)
    pub_key_path = f"{key_path}.pub"

    with open(pub_key_path, "r", encoding="utf-8") as file_handle:
        return file_handle.read().strip()


def _parse_repo_url(url: str):
    """Extract owner and repo name from a GitHub URL."""
    match = re.match(
        r"https?://github\.com/([^/]+)/([^/]+?)(?:\.git)?(?:/.*)?$",
        url.strip()
    )
    if not match:
        raise ValueError(f"Invalid GitHub URL: {url}")
    return match.group(1), match.group(2)


def load_from_github(
    repo_url: str,
    branch: Optional[str] = None,
    file_extensions: Optional[List[str]] = None,
) -> List[Dict[str, str]]:
    """
    Loads files from a GitHub repository using an SSH deploy key.

    The deploy key private key path must be set via the GITHUB_DEPLOY_KEY_PATH
    environment variable. Add the corresponding public key as a read-only deploy
    key in the target repo's Settings → Deploy keys.

    Args:
        repo_url: Full GitHub URL, e.g. https://github.com/owner/repo
        branch: Branch to clone. Defaults to the remote's default branch.
        file_extensions: Extensions to include. Defaults to [".md"].

    Returns:
        List of dicts with 'path' and 'content'.
    """
    if file_extensions is None:
        file_extensions = [".md"]

    key_path = os.getenv("GITHUB_DEPLOY_KEY_PATH", _DEFAULT_KEY_PATH)
    if not os.path.isfile(key_path):
        raise ValueError(f"Deploy key file not found: {key_path}")

    owner, repo_name = _parse_repo_url(repo_url)
    ssh_url = f"git@github.com:{owner}/{repo_name}.git"

    tmp_dir = tempfile.mkdtemp(prefix="memo_github_")
    try:
        ssh_cmd = f"ssh -i {key_path} -o StrictHostKeyChecking=no -o BatchMode=yes"
        env = {**os.environ, "GIT_SSH_COMMAND": ssh_cmd}

        clone_cmd = ["git", "clone", "--depth=1", "--quiet"]
        if branch:
            clone_cmd += ["--branch", branch]
        clone_cmd += [ssh_url, tmp_dir]

        result = subprocess.run(
            clone_cmd,
            env=env,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            raise ValueError(
                f"git clone failed for '{owner}/{repo_name}': {result.stderr.strip()}"
            )

        documents = []
        for root, _, files in os.walk(tmp_dir):
            # Skip .git directory
            if ".git" in root.split(os.sep):
                continue
            for file in files:
                if not any(file.endswith(ext) for ext in file_extensions):
                    continue
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, tmp_dir)
                try:
                    with open(full_path, "r", encoding="utf-8", errors="replace") as f:
                        content = f.read()
                except OSError:
                    continue
                documents.append({
                    "path": f"{owner}/{repo_name}/{rel_path}",
                    "content": content,
                })

        return documents
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)