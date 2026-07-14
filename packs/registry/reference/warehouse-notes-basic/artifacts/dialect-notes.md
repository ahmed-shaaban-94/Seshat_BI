# Postgres dialect notes

Generic notes for authors writing silver/gold migration SQL against
DigitalOcean Postgres. Guidance only: the migration author still decides
whether a note applies to a given table, and nothing here changes the
committed medallion contract.

- Prefer `snake_case` identifiers; quote only when a source name cannot be
  renamed during mapping.
- `INSERT ... ON CONFLICT DO UPDATE` is the standard idempotent-upsert idiom
  for numbered migrations in this repo.
- Generated columns and `CHECK` constraints are evaluated server-side; do not
  duplicate that logic in application code.
- Timestamps are stored `timestamptz`; a business date column is a separate,
  explicit decision the mapping gate records.
