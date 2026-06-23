"""Hand-rolled TMDL (Tabular Model Definition Language) parser.

PARSER DECISION (search-first; full rationale in
docs/decisions/0001-tmdl-pbir-parser.md):
  - TMDL is parsed by THIS hand-rolled indentation/block tokenizer. No PyPI TMDL
    parser is mature enough to depend on (surveyed 2026-06); TOM and sempy read TMDL
    only via the Windows/.NET or Fabric live path, which defeats headless CI, so both
    are disqualified for the static checker.
  - PBIR / report JSON is parsed with the stdlib ``json`` module opened
    ``encoding="utf-8-sig"`` because Power BI writes UTF-8-with-BOM and ``json.load``
    chokes on a leading BOM.

REGRESSION ANCHOR (token literals observed in tests/fixtures/golden_pbip/; M4/M5 pin
their regexes to these. If a fixture edit drops one, tests/unit/test_tmdl.py fails):
  - measure block shape:        ``measure 'TotalSales' = SUM(Sales[Amount])``
                                (single-quoted name; ``measure <name> = <expr>``)
  - display folder:             ``displayFolder: Sales``
  - relationship cross-filter:  ``crossFilteringBehavior: bothDirections``
  - implicit aggregation:       ``summarizeBy: sum``
  - gold-only M source schema:  ``Schema="gold"``
  - parameterized M source:     ``PostgreSQL.Database(Server, Database)``  (identifiers)
  - date-table marker:          ``annotation PBI_DateTable = true``  (table-level)
    *** PROVISIONAL ***  This is the table-level annotation form that M4.1's
    ``DATE_TABLE_MARKER`` constant consumes, used here so M0 and M4 agree. The exact
    "Mark as Date Table" TMDL literal is NOT yet confirmed against a real Power BI
    capture (spec §5.2 D7 note / §13 flag it may differ). RE-VERIFY against the real
    PBIP captured in Task M0.3 before M4 builds D7. If the captured real fixture shows
    a different marker literal, update BOTH M0 and M4.1's DATE_TABLE_MARKER together.
"""

from __future__ import annotations


def top_level_blocks(text: str) -> list[str]:
    """Return the stripped header line of each indentation-level-0 block, in order.

    A "top-level block" is any non-blank line that starts at column 0 (no leading
    whitespace) and is not a continuation. This is the smallest honest slice of the
    hand-rolled parser; M4 extends it with nested-block descent.
    """
    headers: list[str] = []
    for raw_line in text.splitlines():
        if not raw_line.strip():
            continue
        if raw_line[0] in (" ", "\t"):
            continue
        headers.append(raw_line.strip())
    return headers
