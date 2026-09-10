# ---------------------------------------------------------------------------
# Still under development
# ---------------------------------------------------------------------------

#!/usr/bin/env python3
"""
Rescile cloud authorization adapter.

Translates the provider-neutral Rescile service administrator model into
provider-specific permissions. The AWS adapter emits an AWS IAM policy.

Usage:
    python rescile_iam_adapter.py roles.json --provider aws --role network-admin
    python rescile_iam_adapter.py roles.json --provider aws --all
    python rescile_iam_adapter.py roles.json --provider aws --role network-admin \
        --resource-arn "arn:aws:ec2:eu-central-1:123456789012:vpc/*"
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# Generic operation -> provider action mapping
#
# The generic JSON remains the authoritative model. Provider mappings are
# adapter implementation details and should be versioned independently.
# ---------------------------------------------------------------------------

# Reference missing
# AWS_OPERATION_ACTIONS: dict[str, list[str]] =


@dataclass
class TranslationResult:
    role: str
    actions: list[str]
    dependencies: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


class Adapter:
    """Base class for provider adapters."""

    provider: str

    def translate(self, role_name: str, role: dict[str, Any]) -> TranslationResult:
        raise NotImplementedError


class AwsIamAdapter(Adapter):
    provider = "aws"

    def __init__(self, mapping: dict[str, list[str]] | None = None):
        self.mapping = mapping or AWS_OPERATION_ACTIONS

    def translate(self, role_name: str, role: dict[str, Any]) -> TranslationResult:
        actions: set[str] = set()
        warnings: list[str] = []

        for operation in role.get("operations", []):
            mapped = self.mapping.get(operation)
            if mapped is None:
                warnings.append(
                    f"No AWS mapping exists for generic operation '{operation}'."
                )
                continue
            actions.update(mapped)

        # Generic capabilities are intentionally not translated directly.
        # The adapter maps semantic operations to concrete provider actions.
        dependencies = []
        if role_name in {"compute-admin", "container-admin", "kubernetes-admin"}:
            dependencies.append("iam:PassRole")

        if role_name == "iam-admin":
            warnings.append(
                "iam-admin is critical. Generated permissions should normally "
                "be constrained by SCPs, permission boundaries, resource scope "
                "and JIT/approval controls."
            )

        return TranslationResult(
            role=role_name,
            actions=sorted(actions),
            dependencies=dependencies,
            warnings=warnings,
        )

    def policy(
        self,
        role_name: str,
        role: dict[str, Any],
        resource_arn: str = "*",
        include_dependencies: bool = False,
    ) -> dict[str, Any]:
        result = self.translate(role_name, role)

        statements = [{
            "Sid": f"Rescile{_pascal(role_name)}",
            "Effect": "Allow",
            "Action": result.actions,
            "Resource": resource_arn,
        }]

        if include_dependencies and result.dependencies:
            statements.append({
                "Sid": "RescileDependencies",
                "Effect": "Allow",
                "Action": result.dependencies,
                "Resource": "*",
                "Condition": {
                    "StringLike": {
                        "iam:PassedToService": [
                            "ec2.amazonaws.com",
                            "ecs-tasks.amazonaws.com",
                            "eks.amazonaws.com",
                        ]
                    }
                },
            })

        return {
            "Version": "2012-10-17",
            "Statement": statements,
            "_rescile": {
                "provider": "aws",
                "role": role_name,
                "source_operations": role.get("operations", []),
                "warnings": result.warnings,
            },
        }


def _pascal(value: str) -> str:
    return "".join(part.capitalize() for part in value.replace("_", "-").split("-"))


def load_document(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Translate Rescile generic roles to provider IAM permissions."
    )
    parser.add_argument("input", type=Path, help="Rescile generic role JSON")
    parser.add_argument("--provider", default="aws", choices=["aws"])
    parser.add_argument("--role", help="Role to translate")
    parser.add_argument("--all", action="store_true", help="Translate all roles")
    parser.add_argument(
        "--resource-arn",
        default="*",
        help="Resource ARN for generated policy. Default: *",
    )
    parser.add_argument(
        "--include-dependencies",
        action="store_true",
        help="Include dependencies such as iam:PassRole",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Write JSON to this file instead of stdout",
    )

    args = parser.parse_args()
    document = load_document(args.input)

    if args.provider != "aws":
        raise SystemExit(f"Unsupported provider: {args.provider}")

    adapter = AwsIamAdapter()
    roles = document.get("roles", {})

    if args.all:
        output = {
            "Version": "2012-10-17",
            "Policies": {
                name: adapter.policy(
                    name,
                    role,
                    args.resource_arn,
                    args.include_dependencies,
                )
                for name, role in roles.items()
            },
        }
    elif args.role:
        if args.role not in roles:
            available = ", ".join(sorted(roles))
            raise SystemExit(
                f"Unknown role '{args.role}'. Available roles: {available}"
            )
        output = adapter.policy(
            args.role,
            roles[args.role],
            args.resource_arn,
            args.include_dependencies,
        )
    else:
        raise SystemExit("Specify --role ROLE or --all")

    serialized = json.dumps(output, indent=2) + "\n"

    if args.output:
        args.output.write_text(serialized, encoding="utf-8")
    else:
        print(serialized)


if __name__ == "__main__":
    main()
