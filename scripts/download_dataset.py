from __future__ import annotations

import argparse
from pathlib import Path

from huggingface_hub import snapshot_download


DEFAULT_REPO_ID = "lerobot/pusht"


def repo_id_to_dir(repo_id: str) -> str:
    return repo_id.replace("/", "__")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Download a LeRobot dataset snapshot from Hugging Face Hub.",
    )
    parser.add_argument("--repo-id", default=DEFAULT_REPO_ID, help="Hugging Face dataset repo id.")
    parser.add_argument(
        "--local-dir",
        default=None,
        help="Where to place the dataset. Default: data/<repo-id-with-__>.",
    )
    parser.add_argument(
        "--allow-pattern",
        action="append",
        default=None,
        help="Optional Hugging Face allow pattern. Repeat for multiple patterns.",
    )
    parser.add_argument(
        "--ignore-pattern",
        action="append",
        default=None,
        help="Optional Hugging Face ignore pattern. Repeat for multiple patterns.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    local_dir = Path(args.local_dir or Path("data") / repo_id_to_dir(args.repo_id))
    local_dir.mkdir(parents=True, exist_ok=True)

    print(f"Downloading dataset: {args.repo_id}")
    print(f"Local directory: {local_dir.resolve()}")
    if args.allow_pattern:
        print(f"Allow patterns: {args.allow_pattern}")
    if args.ignore_pattern:
        print(f"Ignore patterns: {args.ignore_pattern}")

    path = snapshot_download(
        repo_id=args.repo_id,
        repo_type="dataset",
        local_dir=str(local_dir),
        allow_patterns=args.allow_pattern,
        ignore_patterns=args.ignore_pattern,
    )

    print(f"Done: {Path(path).resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
