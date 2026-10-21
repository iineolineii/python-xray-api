import re
import sys
from pathlib import Path

from grpc_tools import protoc

PROTO_INCLUDE = protoc._get_resource_file_name("grpc_tools", "_proto")


def compile(source_dir: str | Path, destination_dir: str | Path, file: str | Path) -> None:
    args = [
        protoc.__file__,
        f"-I={source_dir}",
        f"--python_out={destination_dir}",
        f"--grpc_python_out={destination_dir}",
        str(file),
        "-I{}".format(PROTO_INCLUDE)
    ]
    protoc.main(args)


def fix_imports(destination_dir: Path) -> None:
    packages: list[str] = [
        package.name
        for package in destination_dir.iterdir()
        if package.is_dir() and not package.name.startswith(".")
    ]

    packages_regex = "|".join(packages)
    print(packages_regex)

    for module in destination_dir.resolve().rglob("*.py"):
        with open(module, "r") as file:
            code = file.read()
            code = re.sub(rf"^import\s+((?:{packages_regex}).*)",        r"from xray import \1", code, flags=re.MULTILINE)
            code = re.sub(rf"^from\s+((?:{packages_regex}).*)\s+import", r"from xray.\1 import", code, flags=re.MULTILINE)

        with open(module, "w") as file:
            file.write(code)


def main(source_dir: str | Path, destination_dir: str | Path) -> None:
    source_dir      = Path(source_dir)
    destination_dir = Path(destination_dir)
    destination_dir.mkdir(exist_ok=True)

    for proto in source_dir.rglob("*.proto"):
        compile(source_dir, destination_dir, proto)

    fix_imports(destination_dir)


if __name__ == "__main__":
    main(*sys.argv[1:])
