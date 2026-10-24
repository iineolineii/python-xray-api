import re
from dataclasses import dataclass
from typing import Any, Self

from ..errors import InvalidVersionFormatError, MissingPrereleaseStatusError, ReleaseNotFoundError
from ..utils import github


@dataclass
class Version:
    major: int
    minor: int
    patch: int
    is_prerelease: bool = False

    @classmethod
    def parse(cls, text: str) -> "Self":
        major, minor, patch = cls._parse(text)
        return cls(major=major, minor=minor, patch=patch)

    @classmethod
    def _parse(cls, text):
        match = re.match(r"^v?(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)$", text)
        if not match:
            raise InvalidVersionFormatError(text)

        return int(match.group("major")), int(match.group("minor")), int(match.group("patch"))

    def fetch_prerelease_status(self, repository_name: str) -> None:
        """
        Fetches the prerelease status from the specified GitHub repository.
        """
        print(f"Fetching corresponding release for tag 'v{self}' of GitHub repository '{repository_name}'")
        release = github(f"/repos/{repository_name}/releases/tags/v{self}")

        if release is None:
            raise ReleaseNotFoundError(repository_name, str(self))

        if "prerelease" not in release:
            raise MissingPrereleaseStatusError(repository_name, str(self))

        self.is_prerelease = bool(release["prerelease"])

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, Version):
            return str(self) == str(other)

        return False

    def __hash__(self) -> int:
        return hash(str(self))


__all__ = ["Version"]
