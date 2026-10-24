class ReleaseNotFoundError(ValueError):
    def __init__(self, repository_name: str, tag_name: str) -> None:
        tag_name = tag_name.lstrip("v")
        message = f"Could not find GitHub release for the {repository_name!r} repository tag v{tag_name}"
        super().__init__(message)

class NoSemanticVersionTagsError(ValueError):
    def __init__(self, repository_name: str) -> None:
        message = f"Could not find any semantic version tags in the {repository_name!r} repository"
        super().__init__(message)


class InvalidVersionFormatError(ValueError):
    def __init__(self, text: str) -> None:
        message = f"Invalid version format: {text!r}"
        super().__init__(message)


class MissingPrereleaseStatusError(ValueError):
    def __init__(self, repository_name: str, tag_name: str) -> None:
        tag_name = tag_name.lstrip("v")
        message = f"Could not get prerelease status for tag v{tag_name} of GitHub repository {repository_name!r}"
        super().__init__(message)


__all__ = [
    "ReleaseNotFoundError",
    "NoSemanticVersionTagsError",
    "InvalidVersionFormatError",
    "MissingPrereleaseStatusError"
]
