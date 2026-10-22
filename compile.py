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

    for module in destination_dir.rglob("*.py"):
        with open(module, "r") as file:
            code = file.read()
            code = re.sub(rf"^import\s+((?:{packages_regex}).*)",        r"from xray import \1", code, flags=re.MULTILINE)
            code = re.sub(rf"^from\s+((?:{packages_regex}).*)\s+import", r"from xray.\1 import", code, flags=re.MULTILINE)

        with open(module, "w") as file:
            file.write(code)

    for package in destination_dir.rglob("*"):
        init_module = package / "__init__.py"
        if package.is_dir() and not init_module.exists():
            init_module.touch()

    init_module = destination_dir / "__init__.py"
    if not init_module.exists():
        init_module.touch()


def main(source_dir: str | Path, destination_dir: str | Path) -> None:
    source_dir = Path(source_dir).resolve()

    if not source_dir.exists():
        raise FileNotFoundError(f"Source directory {source_dir} does not exist")

    if not source_dir.is_dir():
        raise NotADirectoryError(f"Source path {source_dir} is not a directory")

    if not list(source_dir.iterdir()):
        raise FileNotFoundError(f"Source directory {source_dir} is empty")

    destination_dir = Path(destination_dir)
    destination_dir.mkdir(exist_ok=True)
    destination_dir = destination_dir.resolve()

    for proto in source_dir.rglob("*.proto"):
        compile(source_dir, destination_dir, proto)

    fix_imports(destination_dir)


if __name__ == "__main__":
    main(*sys.argv[1:])
