# Product-direction decision: CLI verbs (A) vs skill-driven packaging (B)

> **Status: RATIFIED — Option B (skill-driven packaging), by Ahmed Shaaban (owner)
> 2026-07-07.** The owner directed "ratify all recommended" by name; this records that
> decision (the agent records an owner-directed ruling; it does not self-grant —
> Principle V, same pattern as ADR 0015/0016). This decision gated roadmap milestones
> **M4, M6, M7, M9, M10** in `seshat-bi-agent-controlled-user-tool-roadmap.md`; they are
> now unblocked and specced under B. M1/M2 (built) and M3/M11 (specs) did not depend on it.

## The fork

The agent-controlled-user-tool roadmap wants Seshat BI to become an installable,
agent-controlled tool. Several milestones (M4 agent-control protocol, M6 source
onboarding, M7 mapping review, M9 evidence pack, M10 BI delivery) can be delivered two
different ways, and the roadmap draft silently assumes the first:

- **Option A — add CLI verbs.** Wrap each capability as a new `seshat <verb>` command
  (`seshat source profile`, `seshat mapping review`, `seshat evidence build`,
  `seshat status`, `seshat next-action`, …). The agent (or a user) invokes verbs.

- **Option B — package the skills, stay skill-driven.** The capabilities already exist
  as **agent skills** under `.claude/skills/` (`first-hour-compass`, `readiness-viewer`,
  `run-next-readiness`, `source-mapping`, `retail-onboard-table`,
  `evidence-pack-generator`, …). Option B gives them an **install/packaging/discovery
  story** for a new user, while the agent+skills remain the interface. The CLI stays the
  narrow gate surface it is today (`check`, `validate`, `semantic-check`, the `pbir-*`
  writers).

## Why this is a real fork, not a style choice

Hard rule #1 (see `AGENTS.md`, `docs/roadmap/roadmap.md`): **Seshat BI is agent-first —
the agent + skills are the product interface; the CLI is deliberately a narrow set of
gates the agent calls.** Option A grows the CLI into a broad verb surface that *duplicates*
capabilities already shipped as skills. That is a genuine change to the product's stated
identity, which is why it is an owner decision and not the agent's to make.

## Tradeoffs

| Dimension | A — CLI verbs | B — skill-driven packaging |
|-----------|---------------|-----------------------------|
| Fit with hard rule #1 | Cuts against it (broadens CLI beyond a gate) | Aligned (CLI stays a gate; agent+skills stay the interface) |
| Duplication | Re-implements shipped skills as verbs (two surfaces to maintain) | Reuses shipped skills; one surface |
| New-user discoverability | High — `seshat --help` lists everything | Needs a packaging/index story (the actual M2/M-work) so skills are found |
| Non-agent / scripting use (CI, cron) | Strong — verbs are scriptable without an agent | Weaker — skill invocation assumes an agent host |
| Maintenance surface | Larger (verbs + skills drift apart) | Smaller (skills are the single source) |
| Testing | Each verb needs CLI tests | Skills already exist/tested |
| Reversibility | Harder (a shipped public verb is a compatibility contract) | Easier (packaging is additive) |

## Advisor recommendation (input only — NOT a ratification)

**Lean: Option B (skill-driven packaging).** Rationale: it is what hard rule #1 actually
points to; it avoids proliferating a CLI verb surface that duplicates capabilities already
shipped and tested as skills; and it is the more reversible, lower-maintenance path. The
one real argument *for* A — scriptable, agent-less invocation (CI/cron) — is worth weighing
if non-agent automation is a genuine target user; if it is, a **hybrid** is possible: keep
the interface skill-driven (B) but expose a *small* machine-readable status surface
(`seshat status --format json`, the M4 schema part) as the one deliberate CLI addition,
without turning every skill into a verb.

## What each choice unblocks

- **If B:** M4 becomes "package + a JSON status schema"; M6/M7/M9/M10 become
  "install/discovery story over the existing skills" — mostly docs/packaging, little new
  runtime.
- **If A:** M4/M6/M7/M9/M10 each become a new CLI verb with its own spec, parser, handler,
  and tests — substantially more build, and a larger permanent CLI surface.

## Ratification (Principle V — recorded from an owner-directed decision)

- **decision:** **B — skill-driven packaging.** The interface stays agent+skills (hard
  rule #1); the CLI stays a narrow gate. M4/M6/M7/M9/M10 are delivered as an
  install/discovery/packaging story over the already-shipped skills, with the one
  deliberate CLI addition being a small machine-readable status surface
  (`status --format json`, the M4 schema part) — NOT a broad verb surface.
- **ratified_by:** Ahmed Shaaban (owner)
- **ratified_on:** 2026-07-07
- **notes:** Owner directed "ratify all recommended" by name (2026-07-07); the agent
  recorded the owner-directed ruling, it did not self-ratify (Principle V; same pattern
  as ADR 0015/0016). B was the advisor-recommended option (aligns hard rule #1, less
  duplication, more reversible).

M4/M6/M7/M9/M10 are now specced under B (see specs 109–113). Per the "safe subset"
discipline, the docs/packaging pieces are built and any net-new runtime / JSON-schema /
CI piece is spec-and-held for review.
