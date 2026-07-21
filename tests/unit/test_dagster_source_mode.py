"""Unit tests for the driver-free source-mode + source-adapter seam (#404/#405).

Parent-environment tests: no dagster, no psycopg2. They pin the closed mode
vocabulary, the fail-closed normalization, the Protocol shape, the
non-destruction flag, and the source-map contract reader.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from seshat.dagster_adapter import source_contract, source_mode
from seshat.dagster_adapter.source_adapter import (
    SourceAdapter,
    SourcePrepared,
    is_destructive_mode,
)

pytestmark = pytest.mark.unit


class TestSourceModeVocabulary:
    def test_default_is_csv_unchanged(self) -> None:
        assert source_mode.DEFAULT_SOURCE_MODE == "csv"
        assert source_mode.CSV == "csv"
        assert source_mode.EXISTING_BRONZE == "existing-bronze"

    def test_closed_set_is_exactly_two_modes(self) -> None:
        assert source_mode.SOURCE_MODES == frozenset({"csv", "existing-bronze"})

    def test_env_var_name_matches_the_tables_seam_family(self) -> None:
        assert source_mode.SOURCE_MODE_ENV == "SESHAT_DAGSTER_SOURCE_MODE"

    @pytest.mark.parametrize("value", [None, "", "   "])
    def test_absent_or_empty_resolves_to_default_csv(self, value) -> None:
        # Byte-identity guard: no selection => the unchanged CSV path.
        assert source_mode.normalize_source_mode(value) == "csv"

    def test_known_modes_normalize_to_themselves(self) -> None:
        assert source_mode.normalize_source_mode("csv") == "csv"
        assert source_mode.normalize_source_mode("existing-bronze") == "existing-bronze"
        assert source_mode.normalize_source_mode("  existing-bronze  ") == (
            "existing-bronze"
        )

    def test_unknown_mode_fails_closed_with_named_set(self) -> None:
        with pytest.raises(ValueError, match="source mode must be one of"):
            source_mode.normalize_source_mode("truncate-everything")


class TestSourceAdapterContract:
    def test_source_prepared_is_immutable(self) -> None:
        prepared = SourcePrepared(source_mode="csv", outcome="materialized")
        with pytest.raises(Exception):  # frozen dataclass
            prepared.outcome = "failed"  # type: ignore[misc]

    def test_a_fake_adapter_satisfies_the_protocol(self) -> None:
        class FakeAdapter:
            source_mode = "csv"

            def prepare_bronze(self, table: str) -> SourcePrepared:
                return SourcePrepared(
                    source_mode="csv",
                    outcome="materialized",
                    measured={"rows_loaded": 3},
                    mutated_bronze=True,
                )

        adapter: SourceAdapter = FakeAdapter()
        assert isinstance(adapter, SourceAdapter)  # runtime_checkable
        result = adapter.prepare_bronze("demo_table")
        assert result.outcome == "materialized"
        assert result.mutated_bronze is True

    def test_only_csv_is_a_destructive_mode(self) -> None:
        assert is_destructive_mode("csv") is True
        assert is_destructive_mode("existing-bronze") is False
        # Unknown modes are treated as destructive (never a false safety claim).
        assert is_destructive_mode("mystery") is True


class TestSourceContractReader:
    def _write_map(self, root: Path, table: str, body: str) -> None:
        table_dir = root / "mappings" / table
        table_dir.mkdir(parents=True, exist_ok=True)
        (table_dir / "source-map.yaml").write_text(body, encoding="utf-8")

    def test_reads_source_name_from_columns(self, tmp_path: Path) -> None:
        self._write_map(
            tmp_path,
            "demo",
            "columns:\n"
            "  - source_name: transaction_id\n"
            "    decision: keep\n"
            "  - source_name: total_spent\n"
            "    decision: keep\n",
        )
        assert source_contract.referenced_source_columns(tmp_path, "demo") == frozenset(
            {"transaction_id", "total_spent"}
        )

    def test_absent_map_is_empty_set_not_an_error(self, tmp_path: Path) -> None:
        result = source_contract.referenced_source_columns(tmp_path, "nope")
        assert result == frozenset()

    def test_map_without_columns_list_is_empty_set(self, tmp_path: Path) -> None:
        self._write_map(tmp_path, "demo", "table: demo\n")
        result = source_contract.referenced_source_columns(tmp_path, "demo")
        assert result == frozenset()

    def test_malformed_yaml_is_empty_set(self, tmp_path: Path) -> None:
        self._write_map(tmp_path, "demo", "columns: [ : : broken")
        result = source_contract.referenced_source_columns(tmp_path, "demo")
        assert result == frozenset()
