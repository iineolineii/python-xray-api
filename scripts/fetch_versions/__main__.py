import argparse
import sys

from .models import Repository, ReleaseState


def main(
    upstream_name:  str,
    summary_output: str = "/dev/stdout",
    result_output:  str = "/dev/null",
    target_version: str | None = None
) -> None:
    local_repo = Repository(name="local")

    upstream_repo = Repository(
        name=upstream_name,
        remote_url=f"https://github.com/{upstream_name}.git"
    )

    state = ReleaseState(
        local_repo=local_repo,
        upstream_repo=upstream_repo,
        _target_version=target_version
    )

    state.print_summary(summary_output)
    state.print_result(result_output)


def error(message: str) -> int:
    print(f"❌ ERROR: {message}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch and check version updates")
    parser.add_argument(
        "upstream_name",
        help="Upstream repository name"
    )
    parser.add_argument(
        "summary_output",
        nargs="?",
        default="/dev/stdout",
        help="Summary output file"
    )
    parser.add_argument(
        "result_output",
        nargs="?",
        default="/dev/null",
        help="Result output file"
    )
    parser.add_argument(
        "--target-version",
        help="Target upstream version (e.g., 1.2.3). Leave empty for latest."
    )

    args = parser.parse_args()

    try:
        main(
            upstream_name=args.upstream_name,
            summary_output=args.summary_output,
            result_output=args.result_output,
            target_version=args.target_version
        )
    except Exception as exc:
        sys.exit(error(str(exc)))
