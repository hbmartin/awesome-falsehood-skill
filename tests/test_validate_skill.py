import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import validate_skill


def test_repository_skill_passes_validation():
    # Integration check: the checked-in skill must always validate.
    assert validate_skill.main() == 0


def test_frontmatter_parser_handles_missing_terminator():
    assert validate_skill.parse_frontmatter("---\nname: x\nno terminator") is None


def test_frontmatter_parser_reads_fields():
    fields = validate_skill.parse_frontmatter("---\nname: a\ndescription: b c\n---\nbody")
    assert fields == {"name": "a", "description": "b c"}
