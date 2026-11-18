"""Copy the agent skills from agent-skills/ into the folders each agent reads.

Claude Code reads .claude/skills/, Antigravity reads .agents/skills/. The only
source of truth is agent-skills/: edit there, then run this script.

    uv run python scripts/sync_agent_skills.py           # copy
    uv run python scripts/sync_agent_skills.py --check   # exit 1 if copies differ
"""

import argparse
import filecmp
import shutil
import sys
from pathlib import Path

SOURCE_DIR = "agent-skills"
TARGET_DIRS = (".claude/skills", ".agents/skills")


def list_skills(root: Path) -> list[str]:
    """Return the sorted names of the skills in <root>/agent-skills/."""
    source = root / SOURCE_DIR
    if not source.is_dir():
        raise FileNotFoundError(f"{source} not found")
    return sorted(p.name for p in source.iterdir() if (p / "SKILL.md").is_file())


def sync(root: Path) -> None:
    """Replace every target copy of each source skill with a fresh copy.

    Skills that exist only in a target folder are left untouched.
    """
    for name in list_skills(root):
        for target in TARGET_DIRS:
            destination = root / target / name
            if destination.exists():
                shutil.rmtree(destination)
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(root / SOURCE_DIR / name, destination)


def _same_tree(left: Path, right: Path) -> bool:
    """Return True if the two folders hold the same files with the same content."""
    comparison = filecmp.dircmp(left, right)
    if comparison.left_only or comparison.right_only or comparison.funny_files:
        return False
    _, mismatch, errors = filecmp.cmpfiles(
        left, right, comparison.common_files, shallow=False
    )
    if mismatch or errors:
        return False
    return all(
        _same_tree(left / sub, right / sub) for sub in comparison.common_dirs
    )


def find_differences(root: Path) -> list[str]:
    """Describe each target copy that is missing or differs from its source."""
    differences = []
    for name in list_skills(root):
        for target in TARGET_DIRS:
            destination = root / target / name
            if not destination.is_dir() or not _same_tree(
                root / SOURCE_DIR / name, destination
            ):
                differences.append(f"{target}/{name} differs from {SOURCE_DIR}/{name}")
    return differences


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parent.parent,
        help="repository root (default: the folder above scripts/)",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="copy nothing; exit 1 if any copy differs from agent-skills/",
    )
    args = parser.parse_args(argv)

    try:
        if args.check:
            differences = find_differences(args.root)
            for line in differences:
                print(line)
            if differences:
                print("Run: uv run python scripts/sync_agent_skills.py")
                return 1
            print("Skills are in sync.")
            return 0
        sync(args.root)
    except FileNotFoundError as error:
        print(error, file=sys.stderr)
        return 1
    print(f"Copied {len(list_skills(args.root))} skills.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
