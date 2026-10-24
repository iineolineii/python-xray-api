from collections.abc import Iterator
from dataclasses import dataclass, field
from datetime import datetime, timezone
from tempfile import TemporaryDirectory

from .tag import Tag
from .version import Version
from ..utils import git


@dataclass
class Repository:
    name:           str
    git_dir:        str | None = None
    remote_url:     str | None = None

    temp_dir: "TemporaryDirectory | None" = field(init=False, default=None)

    def __post_init__(self):
        self.__temp_dir = None

        if self.remote_url:
            dir_name = self.name.replace("/", "-")
            self.__temp_dir = TemporaryDirectory(prefix=f"repo-{dir_name}-")
            self.git_dir = self.__temp_dir.name

            print(f"Initializing bare git repository at {self.git_dir!r}")
            git("init", "--bare", "--quiet", self.git_dir)
            print(f"Fetching tags from {self.remote_url!r}...")
            git(
                "fetch", "--quiet", "--depth=1", "--tags", "--force",
                self.remote_url, "refs/tags/*:refs/tags/*",
                repo=self.git_dir,
                timeout=300
            )

    @property
    def tags(self) -> Iterator["Tag"]:
        print(f"Sorting tags from git repository {self.name!r}...")
        output = git(
            "for-each-ref",
            "--sort=-creatordate",
            "--format=%(refname:short)%09%(creatordate:unix)",
            "refs/tags/",
            repo=self.git_dir
        )

        for line in output.splitlines():
            name, _, timestamp = line.partition("\t")
            if not name:
                continue

            date = datetime.fromtimestamp(int(timestamp), tz=timezone.utc)
            yield Tag(name=name, date=date)

    @property
    def versions(self) -> Iterator["Version"]:
        for tag in self.tags:
            version = Version.parse(tag.name)

            if self.remote_url:
                version.fetch_prerelease_status(self.name)

            yield version

    def __del__(self) -> None:
        if self.__temp_dir is not None:
            self.__temp_dir.cleanup()


__all__ = ["Repository"]
