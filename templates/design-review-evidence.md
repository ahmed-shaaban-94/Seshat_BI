# Design-Review Evidence -- `<page_or_report_name>`

> **GENERIC TEMPLATE.** This is the blank a reviewer fills to RECORD a design
> review of a built dashboard page, so a `dashboard_ready: pass` can cite a
> well-formed evidence artifact (checked by rule `DL4`). Copy it per page,
> replace every `<placeholder>`, and record the review. It is a verify-slot
> artifact: it PACKAGES the review evidence and leaves the approval for a named
> human to sign -- it never grants the pass and never redesigns the page.
>
> It carries the SAME field shape `DL4` enforces on filled instances:
> `page_id`, `anti_patterns_checked[]`, `contrast_pairs[]`, `reviewer`, `date`.
> A field left as a `<placeholder>` means the record is incomplete.
>
> This template is GENERIC to retail BI (roadmap rule 7). Do NOT copy any
> subject-area specifics (real page names, tenant brand, PII columns, worked
> measure names) into it -- those belong only in a per-subject-area working set.

---

## What this evidence is (and is not)

This RECORDS that a human reviewed how a built page reads -- hierarchy,
readability, the design anti-patterns checked, and the text/background contrast
pairs inspected. It is EVIDENCE for the `dashboard_ready` gate; it does NOT
decide whether the design is good (the reviewer does), redesign the page, define
a metric, or grant `dashboard_ready: pass` (the readiness verdict + a named human
do that -- see `docs/readiness/dashboard-ready.md`).

## Record

- **page_id:** `<page_or_visual_id>`
- **reviewer:** `<named_human>`
- **date:** `<YYYY-MM-DD>`

### anti_patterns_checked

> Each anti-pattern the reviewer confirmed the page does NOT commit (from the
> design anti-pattern catalog). One row per checked pattern.

| anti_pattern | not_present? | note |
|--------------|--------------|------|
| `<anti_pattern_id>` | `<yes / reason>` | `<optional note>` |

### contrast_pairs

> The text/background color pairs the reviewer inspected for legibility (the
> computed WCAG ratio is `CT1`'s job; this records WHICH pairs were reviewed).

| pair | reviewed? |
|------|-----------|
| `<foreground_vs_background>` | `<yes>` |

## Approval (a named human signs -- this template never fills it)

- **design_review_approved_by:** `<named_human, or leave blank until signed>`
- **approval_date:** `<YYYY-MM-DD, or leave blank until signed>`

> This slot is intentionally EMPTY in the template. `DL4` checks the record above
> is well-formed; it never fills, reads, or grants this approval. Recording the
> approval and promoting `dashboard_ready` to `pass` is the named human's action,
> gated by `RS1` (which requires a matching `approvals[]` entry).
