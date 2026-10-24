from collections.abc import Iterable
from enum import Enum, auto
import json
import os
import subprocess
import urllib.error
import urllib.request
from typing import TypeVar

from more_itertools import peekable


def git(*arguments: str, repo: str | None = None, timeout: int = 120) -> str:
    command = ["git"]

    if repo is not None:
        command += ["--git-dir", repo]

    command += arguments

    try:
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False,
            timeout=timeout
        )

    except subprocess.TimeoutExpired as exc:
        raise RuntimeError(f"{' '.join(command)} timed out") from exc

    if completed.returncode != 0:
        detail = completed.stderr.strip() or completed.stdout.strip()
        raise RuntimeError(f"{' '.join(command)} failed: {detail}")

    return completed.stdout


def github(path: str) -> dict | None:
    """
    Performs an authenticated GitHub API GET request

    :param path: API path, e.g. /repos/Author/Repo/releases/tags/v1.2.3
    :type path: str

    :return: Decoded JSON payload, or None on HTTP 404.
    :rtype: dict | None

    :raises RuntimeError: On network errors or non-404 HTTP errors.
    """
    request = urllib.request.Request(f"https://api.github.com{path}")

    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token:
        request.add_header("Authorization", f"Bearer {token}")

    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.load(response)

    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return None

        detail = exc.read().decode("utf-8", errors="replace").strip()
        raise RuntimeError(f"GitHub API {path} failed: {exc.code} {detail}") from exc

    except urllib.error.URLError as exc:
        raise RuntimeError(f"GitHub API {path} failed: {exc.reason}") from exc

__all__ = ["git", "github"]
