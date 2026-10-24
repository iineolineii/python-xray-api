from dataclasses import dataclass, field

from .repository import Repository
from .version import Version
from ..errors import NoSemanticVersionTagsError
from ..utils import peek


@dataclass
class ReleaseState:
    """
    Encapsulates the entire update decision logic and output formatting
    """
    local_repo:    Repository
    upstream_repo: Repository

    latest_upstream:   Version = field(init=False)
    latest_published:  Version = field(init=False)

    needs_update: bool = field(init=False)
    summary:      str  = field(init=False)

    def __post_init__(self) -> None:
        upstream = self.upstream_repo.name

        try:
            self.latest_upstream = peek(self.upstream_repo.versions)
        except StopIteration:
            raise NoSemanticVersionTagsError(upstream)

        latest_line = f"Latest {upstream} version: v{self.latest_upstream}"

        # 0.0.0 if local repository has no published releases yet
        self.latest_published = peek(self.local_repo.versions, default=Version(0, 0, 0))
        published_line = f"Latest published {upstream} version: v{self.latest_published}"

        # Is the latest upstream already published?
        if self.latest_upstream in self.local_repo.versions:
            self.needs_update = False
            update_status_line = f"✅ Update is not needed. Already published as v{self.latest_upstream}"
        else:
            self.needs_update = True
            update_status_line = f"🔄 Updating to {upstream} v{self.latest_upstream}"

        # Mirror the upstream prerelease flag
        if self.latest_upstream.is_prerelease:
            update_status_line += " (prerelease)"

        self.summary = published_line + "\n" + latest_line + "\n\n## " + update_status_line

    def print_summary(self, file: str) -> None:
        with open(file, "a") as f:
            print(self.summary, file=f)

    def print_result(self, file: str) -> None:
        with open(file, "a") as f:
            latest_upstream_version    = str(self.latest_upstream)
            latest_published_version   = str(self.latest_published)

            new_version = latest_upstream_version

            is_prerelease = str(self.latest_upstream.is_prerelease).lower()
            needs_update  = str(self.needs_update)

            print(f"latest_upstream_version="    + latest_upstream_version,    file=f)
            print(f"latest_published_version="   + latest_published_version,   file=f)
            print(f"new_version="                + new_version,                file=f)
            print(f"needs_update="               + needs_update,               file=f)
            print(f"is_prerelease="              + is_prerelease,              file=f)
