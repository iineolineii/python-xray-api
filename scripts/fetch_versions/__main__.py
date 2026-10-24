import sys

from .models import Repository, ReleaseState


def main(
    upstream_name: str,
    summary_output: str = "/dev/stdout",
    result_output: str = "/dev/null"
) -> None:
    local_repo = Repository(name="local")

    upstream_repo = Repository(
        name=upstream_name,
        remote_url=f"https://github.com/{upstream_name}.git"
    )

    state = ReleaseState(local_repo=local_repo, upstream_repo=upstream_repo)

    state.print_summary(summary_output)
    state.print_result(result_output)


def error(message: str) -> int:
    print(f"❌ ERROR: {message}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    try:
        main(*sys.argv[1:])
    except Exception as exc:
        raise
        sys.exit(error(str(exc)))
