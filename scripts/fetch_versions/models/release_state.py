from dataclasses import InitVar, dataclass, field

from .repository import Repository
from .version import Version
from ..errors import NoSemanticVersionTagsError


@dataclass
class ReleaseState:
    """
    Encapsulates the entire update decision logic and output formatting
    """
    local_repo:    Repository
    upstream_repo: Repository

    _target_version: InitVar[str | Version | None] = None

    target_version:   Version = field(init=False)
    latest_published: Version = field(init=False)

    needs_update: bool = field(init=False)
    summary:      str  = field(init=False)

    def __post_init__(self, _target_version: str | Version | None) -> None:
        upstream = self.upstream_repo.name

        # If the target upstream version is not specified,
        # Use the latest available one
        if _target_version is None:
            try:
                self.target_version = self.upstream_repo.versions[-1]
            except StopIteration:
                raise NoSemanticVersionTagsError(upstream)

        elif isinstance(_target_version, Version):
            self.target_version = _target_version

        else:
            self.target_version = Version.parse(_target_version)

        self.target_version.fetch_prerelease_status(upstream)
        target_line = f"Target {upstream} version: v{self.target_version}"

        # 0.0.0 if local repository has no published releases yet
        if not self.local_repo.versions:
            self.latest_published = Version(0, 0, 0)
        else:
            self.latest_published = self.local_repo.versions[-1]

        published_line = f"Latest published {upstream} version: v{self.latest_published}"

        # Is the target upstream version already published?
        if self.target_version not in self.local_repo.versions:
            self.needs_update = True
            update_status_line = f"🔄 Updating to {upstream} v{self.target_version}"

            # Mirror the upstream prerelease flag
            if self.target_version.is_prerelease:
                update_status_line += " (prerelease)"
        else:
            self.needs_update = False
            update_status_line = f"✅ Update is not needed"

        self.summary = published_line + "\n" + target_line + "\n\n## " + update_status_line

    def print_summary(self, file: str) -> None:
        with open(file, "a") as f:
            print(self.summary, file=f)

    def print_result(self, file: str) -> None:
        with open(file, "a") as f:
            latest_upstream_version    = str(self.target_version)
            latest_published_version   = str(self.latest_published)

            new_version = latest_upstream_version

            is_prerelease = str(self.target_version.is_prerelease).lower()
            needs_update  = str(self.needs_update)

            print(f"latest_upstream_version="    + latest_upstream_version,    file=f)
            print(f"latest_published_version="   + latest_published_version,   file=f)
            print(f"new_version="                + new_version,                file=f)
            print(f"needs_update="               + needs_update,               file=f)
            print(f"is_prerelease="              + is_prerelease,              file=f)
