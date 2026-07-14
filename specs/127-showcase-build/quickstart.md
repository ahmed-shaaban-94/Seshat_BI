# Quickstart: Shareable Seshat Proof (Showcase Bundle)

This shows how to generate and open the showcase bundle. It is a local, offline,
read-only operation: nothing is published, uploaded, or approved, and no source
artifact is modified.

## Prerequisites

- A Seshat workspace with committed readiness artifacts (e.g. the worked example under `docs/worked-examples/`).
- Python 3.11+ with the shipped `seshat` package importable.
- No database, no Power BI Desktop, no network required.

## 1. Generate the bundle (via the skill)

Ask the agent (the `showcase-build` skill) for a shareable proof of the current
workspace. The skill:

1. Composes the bundle from committed evidence (reusing the readiness/Explorer projection).
2. Runs the disclosure scan and **stops fail-closed** if any secret / DSN / PII / absolute path is present -- writing nothing and listing the findings.
3. Writes the offline bundle under the contained output root `.seshat-output/` (refusing any path that escapes it).

Optional inputs: an RTL/Arabic render mode; two Passport snapshot files to drive
a before/after section.

## 2. What you get

Under `.seshat-output/` (or your contained output path):

- A landing page with a **truthful badge / project card** -- the highest contiguous passed stage and the passed-stage count (e.g. "3/7 stages ready -- Gold: blocked"), never a percentage or grade.
- Per-table readiness detail: stages, evidence (available / missing / deferred), blockers, approvals, next action, and metric lineage -- all carried from the shipped projection.
- A **disclosure manifest** listing every item under exactly one of: included, redacted, omitted, unavailable.
- A **before/after** section only if you supplied two comparable snapshots; otherwise it is omitted with a short note.

## 3. Open it offline

Open the generated HTML in any browser with the network disabled. Confirm:

- All styles, scripts, badge, and brand mark render (everything is inlined / data-URI; no external request).
- In RTL mode, the document reads right-to-left (`dir="rtl"`) with Arabic labels and mirrored layout.
- At a narrow window width, content reflows without a horizontal body scrollbar; wide tables/lineage scroll inside their own container.

## 4. Verify it changed nothing

- `git status` shows only the new files under `.seshat-output/` (which is typically git-ignored) -- no source readiness artifact is modified.
- The shipped `src/seshat/explorer/assets/explorer.css` and `explorer.js` are byte-unchanged (the showcase renders its own shell).

## 5. Sharing (a separate, explicit human action)

The bundle is a local file. Publishing or sending it anywhere is a deliberate
human step you take after reviewing the disclosure manifest. The feature never
publishes, uploads, tracks users, or grants any approval.
