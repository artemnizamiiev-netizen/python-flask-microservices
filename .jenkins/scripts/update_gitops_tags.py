#!/usr/bin/env python3
import argparse
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None


SERVICES = {
    "frontend": "frontend",
    "user-service": "user-service",
    "product-service": "product-service",
    "order-service": "order-service",
}


def update_values_file_with_yaml(path: Path, repository: str, tag: str) -> None:
    if not path.exists():
        raise FileNotFoundError(f"Missing values file: {path}")

    with path.open("r", encoding="utf-8") as handle:
        values = yaml.safe_load(handle) or {}

    image = values.setdefault("image", {})
    image["repository"] = repository
    image["tag"] = tag

    with path.open("w", encoding="utf-8") as handle:
        yaml.safe_dump(values, handle, sort_keys=False)


def update_values_file_without_yaml(path: Path, repository: str, tag: str) -> None:
    if not path.exists():
        raise FileNotFoundError(f"Missing values file: {path}")

    lines = path.read_text(encoding="utf-8").splitlines()
    image_start = None

    for index, line in enumerate(lines):
        if line == "image:":
            image_start = index
            break

    if image_start is None:
        lines.extend(["", "image:", f"  repository: {repository}", f"  tag: {tag}"])
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return

    image_end = len(lines)
    for index in range(image_start + 1, len(lines)):
        if lines[index] and not lines[index].startswith((" ", "-")):
            image_end = index
            break

    repository_updated = False
    tag_updated = False

    for index in range(image_start + 1, image_end):
        stripped = lines[index].strip()
        if stripped.startswith("repository:"):
            lines[index] = f"  repository: {repository}"
            repository_updated = True
        elif stripped.startswith("tag:"):
            lines[index] = f"  tag: {tag}"
            tag_updated = True

    insert_at = image_end
    additions = []
    if not repository_updated:
        additions.append(f"  repository: {repository}")
    if not tag_updated:
        additions.append(f"  tag: {tag}")

    if additions:
        lines[insert_at:insert_at] = additions

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def update_values_file(path: Path, repository: str, tag: str) -> None:
    if yaml is not None:
        update_values_file_with_yaml(path, repository, tag)
    else:
        update_values_file_without_yaml(path, repository, tag)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Update GitOps Helm values with ECR image repositories and tags."
    )
    parser.add_argument("--gitops-dir", required=True, type=Path)
    parser.add_argument("--environment", required=True)
    parser.add_argument("--registry", required=True)
    parser.add_argument("--tag", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    registry = args.registry.rstrip("/")

    for service_name, repository_name in SERVICES.items():
        values_path = (
            args.gitops_dir
            / "environments"
            / args.environment
            / service_name
            / "values.yaml"
        )
        repository = f"{registry}/{repository_name}"
        update_values_file(values_path, repository, args.tag)
        print(f"updated {values_path}: {repository}:{args.tag}")


if __name__ == "__main__":
    main()
