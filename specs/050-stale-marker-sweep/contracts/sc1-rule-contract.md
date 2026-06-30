# Contract: SC1 rule input/output

SC1 is a pure function in the existing rule contract:

```text
check_status_claims(ctx: RuleContext) -> Iterable[Finding]
```

registered via `@register("SC1", "<title>")` in `src/retail/rules/status_claims.py`.
Importing the module fires the decorator (the only wiring; the module is added to
`src/retail/rules/__init__.py`).

## Input

`ctx: RuleContext` (frozen, read-only) providing:
- `ctx.tracked_files: tuple[str, ...]` -- repo-relative POSIX paths (from `git ls-files`).
- `ctx.repo_root: Path` -- repository root, for reading committed text.

The manifest path is a module constant: `_MANIFEST = "docs/quality/status-claims.yaml"`.

## Output

An iterable of `Finding`. Every finding has `rule_id="SC1"`,
`severity=Severity.ERROR`. SC1 emits no WARNING/INFO findings. An empty iterable
means every listed claim is honest (no contradiction). An empty iterable is
returned ONLY after the manifest was read and every entry checked -- never as a
silent skip.

## Behavioral contract (ordered)

1. **Manifest presence (fail loud)**: if `_MANIFEST not in ctx.tracked_files` ->
   return exactly one ERROR ("manifest missing or untracked; SC1 cannot verify
   status claims"). Stop.
2. **Lazy parse**: `import yaml` inside the handler; read
   `(ctx.repo_root / _MANIFEST).read_text(encoding="utf-8")`; `yaml.safe_load`.
   On `yaml.YAMLError` -> one ERROR ("manifest is not valid YAML: <exc>"). Stop.
3. **Shape guard**: if the parsed value is not a mapping, or `claims` is not a list
   -> one ERROR ("manifest must be a mapping with a 'claims' list"). Stop.
4. **Per entry** (preserving order; accumulate findings, do not stop on first):
   a. Entry not a mapping -> ERROR (`claim #<index> is not a mapping`); continue.
   b. Read `id`, `doc`, `anchor`, `claimed-artifact`, `claimed-status`. Any missing
      required field -> ERROR naming the missing field; continue.
   c. `claimed-status` not in `{built, planned}` -> ERROR (invalid status); continue.
   d. `doc` not in tracked set -> ERROR ("claiming document <doc> is missing or
      untracked"); continue.
   e. Read `doc` text; if `anchor` not a substring -> ERROR ("anchor for claim <id>
      is not present in <doc> -- the claim is stale or misplaced"); continue.
   f. Resolve `claimed-artifact` against the tracked set:
      - `built` and NOT resolved -> ERROR ("claim <id> says <artifact> is built, but
        it is not a tracked file").
      - `planned` and resolved -> ERROR ("claim <id> marks <artifact> planned, but it
        now exists -- update the prose / flip to built (stale marker)").
      - otherwise -> no finding for this entry.
5. Return the accumulated findings.

## Non-behaviors (explicit)

- SC1 does NOT infer status from prose, scan for status words, parse markdown, or
  use line/offset positions. The anchor check is a literal substring presence test.
- SC1 does NOT compute or emit any numeric confidence/readiness value.
- SC1 does NOT verify the manifest is complete (no coverage check).
- SC1 does NOT write any file or open any DB/network/Power BI connection.
- SC1 does NOT special-case or hardcode any C086/pharmacy path or value.

## Locator convention

`docs/quality/status-claims.yaml:<id>` for entry-level findings (fall back to
`...:claim[<index>]` when `id` is missing); `_MANIFEST` for whole-manifest failures.
