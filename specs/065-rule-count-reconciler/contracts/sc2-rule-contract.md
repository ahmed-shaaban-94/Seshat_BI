# Contract: SC2 rule (input -> output)

SC2 is a pure function in the existing rule contract:
`check_rule_count_claims(ctx: RuleContext) -> Iterable[Finding]`. It reads only
committed repository text and the tracked-files set; it writes nothing and opens
no connection. This contract fixes the ordered evaluation and the exact
fail-loud/finding behaviour for every input class.

## Inputs

- `ctx.repo_root` (`Path`): root to read committed text (the manifest, each
  claiming `doc`, the count-source JSON).
- `ctx.tracked_files` (iterable of repo-relative POSIX path strings): the set used
  to confirm the manifest, the count source, and each `doc` are tracked.
- `docs/quality/rule-count-claims.yaml`: the manifest (see data-model.md).
- `docs/rules/rules-manifest.json`: the authoritative count source (array length =
  authoritative count).

## Output

An iterable of `Finding`, each with `rule_id="SC2"`, `severity=Severity.ERROR`, a
human-readable `message`, and a `locator`. An honest, fully-reconciled manifest
yields an empty iterable. SC2 NEVER emits a non-ERROR severity and NEVER emits a
numeric confidence/score.

## Ordered evaluation contract

1. **Manifest tracked-file guard**: if `docs/quality/rule-count-claims.yaml` is not
   in `ctx.tracked_files` -> ONE ERROR ("manifest missing/untracked; SC2 cannot
   reconcile count claims"); stop (verify nothing further). Never vacuous-green.
2. **Manifest parse guard**: read the manifest text (UTF-8); lazy `import yaml`;
   `yaml.safe_load`. On a YAML error -> ONE ERROR ("manifest is not valid YAML").
   If the result is not a mapping with a `claims` list -> ONE ERROR ("manifest must
   be a mapping with a 'claims' list").
3. **Count-source guard**: if `docs/rules/rules-manifest.json` is not tracked, or
   cannot be read, or does not parse (stdlib `json`) into a list from which a count
   can be derived -> ONE ERROR ("authoritative rule-count source cannot be read; no
   count claim can be reconciled"); stop. Never vacuous-green. Derive
   `authoritative_count = len(parsed_list)`.
4. **Per claim record** (in manifest order), accumulate findings:
   a. If the record is not a mapping, or is missing any required field
      (`id`/`doc`/`anchor`/`claimed-count`) -> ERROR for that entry; skip its
      remaining checks (never guess a field).
   b. If `doc` is not in `ctx.tracked_files` -> ERROR ("claiming document
      missing/untracked") for that entry; skip its remaining checks.
   c. If `claimed-count` is not a parseable non-negative integer -> ERROR
      ("claimed count is malformed") for that entry; skip its remaining checks.
   d. Read `(ctx.repo_root / doc)` text (UTF-8). If `anchor` is not a substring ->
      ERROR ("anchor stale or misplaced") for that entry; skip the comparison.
   e. If `claimed-count != authoritative_count` -> ERROR naming both the claimed
      integer and the authoritative count ("prose claims K rules; authoritative
      count is M"). Otherwise no finding for that entry.
5. Return the accumulated findings (empty if every entry reconciled clean).

## Invariants (assertable)

- **INV-1 (fail-loud)**: every bad-input class in steps 1-4 produces at least one
  ERROR; no bad input ever yields an empty result via a silent skip.
- **INV-2 (categorical)**: findings contain no percentage/score; the only integers
  are the claimed and authoritative counts.
- **INV-3 (read-only / stdlib-core)**: the module has no module-scope DB/network
  import, no module-scope import of the rules package; `yaml` is imported lazily
  inside the handler and `json` is stdlib. (B1 / the never-execute rule is the
  guard.)
- **INV-4 (manifest-only)**: SC2 checks only records listed in the manifest; it
  never scans the repo for "N rules" strings, so dated snapshots are never touched.
- **INV-5 (declared-integer only)**: the reconciled integer comes from
  `claimed-count`, never from parsing the `anchor` text.

## Message/locator conventions

- `message`: names the offending `id` and `doc`, and either the specific fault
  (missing field / untracked doc / malformed count / stale anchor / unreadable
  manifest or count source) or, for a mismatch, both the claimed and authoritative
  integers.
- `locator`: points at the manifest entry (and/or the claiming `doc`) so the
  maintainer can find it -- mirrors SC1's locator convention.
