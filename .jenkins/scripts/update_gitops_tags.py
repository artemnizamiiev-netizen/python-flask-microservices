#!/usr/bin/env python3
import argparse
from pathlib import Path

import yaml


SERVICES = [
    "frontend",
    "user-service",
    "product-service",
    "order-service",
]


parser = argparse.ArgumentParser(
    description="Update GitOps Helm values with ECR image repositories and tags."
)
parser.add_argument("--gitops-dir", required=True, type=Path)
parser.add_argument("--environment", required=True)
parser.add_argument("--registry", required=True)
parser.add_argument("--tag", required=True)
args = parser.parse_args()

registry = args.registry.rstrip("/")

for service in SERVICES:
    values_path = (
        args.gitops_dir
        / "environments"
        / args.environment
        / service
        / "values.yaml"
    )

    if not values_path.exists():
        raise FileNotFoundError(f"Missing values file: {values_path}")

    with values_path.open("r", encoding="utf-8") as handle:
        values = yaml.safe_load(handle) or {}

    values.setdefault("image", {})
    values["image"]["repository"] = f"{registry}/{service}"
    values["image"]["tag"] = args.tag

    with values_path.open("w", encoding="utf-8") as handle:
        yaml.safe_dump(values, handle, sort_keys=False)

    print(f"updated {values_path}: {registry}/{service}:{args.tag}")
