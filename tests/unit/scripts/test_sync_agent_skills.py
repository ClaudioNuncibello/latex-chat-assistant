"""Unit tests for scripts/sync_agent_skills.py."""

import importlib.util
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[3] / "scripts" / "sync_agent_skills.py"
spec = importlib.util.spec_from_file_location("sync_agent_skills", SCRIPT)
assert spec is not None
assert spec.loader is not None
sync_agent_skills = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sync_agent_skills)

TARGETS = (".claude/skills", ".agents/skills")


def make_skill(root: Path, name: str, files: dict[str, str] | None = None) -> None:
    """Create agent-skills/<name>/ with a SKILL.md and optional extra files."""
    skill = root / "agent-skills" / name
    for rel, text in {"SKILL.md": f"# {name}", **(files or {})}.items():
        path = skill / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")


def test_list_skills_returns_only_folders_with_skill_md(tmp_path):
    make_skill(tmp_path, "tdd")
    make_skill(tmp_path, "handoff")
    (tmp_path / "agent-skills" / "not-a-skill").mkdir()
    (tmp_path / "agent-skills" / "README.md").write_text("x", encoding="utf-8")

    assert sync_agent_skills.list_skills(tmp_path) == ["handoff", "tdd"]


def test_list_skills_fails_when_source_folder_is_missing(tmp_path):
    with pytest.raises(FileNotFoundError):
        sync_agent_skills.list_skills(tmp_path)


def test_sync_copies_each_skill_to_every_target_with_subfolders(tmp_path):
    make_skill(tmp_path, "tdd", {"agents/openai.yaml": "a: 1", "tests.md": "t"})

    sync_agent_skills.sync(tmp_path)

    for target in TARGETS:
        skill = tmp_path / target / "tdd"
        assert (skill / "SKILL.md").read_text(encoding="utf-8") == "# tdd"
        assert (skill / "agents" / "openai.yaml").read_text(encoding="utf-8") == "a: 1"
        assert (skill / "tests.md").is_file()


def test_sync_removes_files_deleted_from_the_source(tmp_path):
    make_skill(tmp_path, "tdd", {"old.md": "old"})
    sync_agent_skills.sync(tmp_path)
    (tmp_path / "agent-skills" / "tdd" / "old.md").unlink()

    sync_agent_skills.sync(tmp_path)

    for target in TARGETS:
        assert not (tmp_path / target / "tdd" / "old.md").exists()


def test_sync_leaves_skills_outside_the_source_untouched(tmp_path):
    make_skill(tmp_path, "tdd")
    personal = tmp_path / ".claude" / "skills" / "personal"
    personal.mkdir(parents=True)
    (personal / "SKILL.md").write_text("mine", encoding="utf-8")

    sync_agent_skills.sync(tmp_path)

    assert (personal / "SKILL.md").read_text(encoding="utf-8") == "mine"


def test_find_differences_is_empty_right_after_sync(tmp_path):
    make_skill(tmp_path, "tdd", {"agents/openai.yaml": "a: 1"})
    sync_agent_skills.sync(tmp_path)

    assert sync_agent_skills.find_differences(tmp_path) == []


def test_find_differences_reports_a_skill_that_was_never_copied(tmp_path):
    make_skill(tmp_path, "tdd")

    differences = sync_agent_skills.find_differences(tmp_path)

    assert len(differences) == len(TARGETS)
    assert all("tdd" in d for d in differences)


def test_find_differences_reports_modified_and_extra_files(tmp_path):
    make_skill(tmp_path, "tdd")
    sync_agent_skills.sync(tmp_path)
    copy = tmp_path / ".claude" / "skills" / "tdd"
    (copy / "SKILL.md").write_text("edited by hand", encoding="utf-8")
    (copy / "extra.md").write_text("x", encoding="utf-8")

    differences = sync_agent_skills.find_differences(tmp_path)

    assert len(differences) == 1
    assert ".claude" in differences[0]


def test_main_check_returns_0_when_aligned_and_1_when_not(tmp_path, capsys):
    make_skill(tmp_path, "tdd")
    args = ["--root", str(tmp_path), "--check"]

    assert sync_agent_skills.main(args) == 1
    sync_agent_skills.sync(tmp_path)
    assert sync_agent_skills.main(args) == 0
    assert "tdd" in capsys.readouterr().out


def test_main_without_check_syncs_and_returns_0(tmp_path):
    make_skill(tmp_path, "tdd")

    assert sync_agent_skills.main(["--root", str(tmp_path)]) == 0
    assert (tmp_path / ".agents" / "skills" / "tdd" / "SKILL.md").is_file()


def test_main_returns_1_when_source_folder_is_missing(tmp_path, capsys):
    assert sync_agent_skills.main(["--root", str(tmp_path)]) == 1
    assert "agent-skills" in capsys.readouterr().err
