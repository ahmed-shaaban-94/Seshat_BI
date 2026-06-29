# Feature Specification: Customer Domain KPI Overview (domains/customer.md)

**Feature**: none (no roadmap F-number -- this idea is from the exploratory idea-bank `docs/roadmap/idea-backlog.md`, which is "not a roadmap and not a commitment"; promotion + F-numbering is a human decision. Content-family lineage is the F009 Retail KPI Knowledge pack, but F009 is SHIPPED and shipped WITHOUT customer.md, so this work is NOT tagged F009 -- doing so would falsely assert it re-opens/advances F009.) | **Spec directory**: `042-customer-domain-kpi-contracts-missing` (next free on-disk slot; the create-new-feature script numbered from current max `041`)

**Feature Branch**: `042-customer-domain-kpi-contracts-missing` (located via `.specify/feature.json`)

**Created**: 2026-06-29

**Status**: Ratified (Ahmed Shaaban, 2026-06-29)

**Input**: User description: "Customer Domain KPI Contracts + missing domains/customer.md"

**Readiness stage advanced**: none. This is read-only / reasoning-layer KPI knowledge content (layer-5). Authoring a domain-overview file grants NO readiness stage in the 7-stage spine -- it has no per-table F-row, it routes only to seeded contracts or honest Planned markers, and it explicitly ends a `[planned]` route on a deferred note (INDEX stop rule). It MUST NOT self-grant any readiness or dashboard-readiness (Principle I).

## Clarifications

This block records the load-bearing ambiguities. Items marked Principle-V are deliberate
judgment calls the agent did NOT answer (constitution Principle V). At ratification (Ahmed
Shaaban, 2026-06-29) the owner DEFERRED all four: they remain unmade rulings, carried into
`domains/customer.md` verbatim as explicit stop-and-ask markers, and every customer KPI stays a
Planned marker until the relevant ruling is later made and recorded by the named owner. The owner
did NOT answer them and the agent did NOT fabricate an answer -- the deferral itself is the ruling.
Items resolved by the advisor in clarification are recorded under the dated session below.

### Owner judgment calls (Principle V -- RESOLVED at ratification: DEFERRED, carried as stop-and-ask markers)

These four are reserved human rulings. The owner ruled at ratification to DEFER each (keep it
unmade and carried into the domain file as a stop-and-ask marker); the domain file carries each
verbatim and never decides it. No customer KPI may become more than a Planned marker until the
relevant ruling is made and recorded by the named owner.

- **[RESOLVED -- DEFERRED by owner 2026-06-29; Principle V -- customer identity / grain]** What
  field(s) uniquely identify a customer (loyalty id? phone? card? account?), and at what grain are
  retention, frequency, and lifetime value defined? No identity key is confirmed anywhere in the
  repo today. This is a grain-ambiguity ruling reserved for a human (constitution Principle V);
  the agent surfaces it, never decides it. Deferred: carried as a stop-and-ask marker.
- **[RESOLVED -- DEFERRED by owner 2026-06-29; Principle V -- PII publish-safety]** Are customer
  identifiers / name / contact details publishable, or default-drop? Per constitution Principle V
  the DEFAULT IS DROP and governance MUST sign off before any customer identifier is published.
  The agent must not decide publish-safety. Deferred: default-drop stands until governance rules.
- **[RESOLVED -- DEFERRED by owner 2026-06-29; Principle V -- business-segment rollups]** Any
  customer segmentation (new-vs-returning, tier, cohort) requires an analyst-supplied value->group
  table. The playbook NEVER invents segments (constitution Principle V); the agent must not author
  one. Deferred: carried as a stop-and-ask marker; no segment authored.
- **[RESOLVED -- DEFERRED by owner 2026-06-29; Principle V -- product identity]** Where a customer
  KPI leans on product identity (e.g. category affinity, repeat-product purchase), the stable
  product key is itself a reserved identity ruling and is not confirmed here. Deferred: carried as
  a stop-and-ask marker.

### Session 2026-06-29

These are the answerable ambiguities (NOT Principle-V carve-outs). Each was resolved by the
advisor against the constitution, the readiness spine, and the 11-sibling template precedent, and
integrated into the spec below.

- Q: Which readiness stage does authoring a knowledge-layer domain-overview file advance?
  -> A: None. Reasoning-layer (layer-5) content; grants no readiness (Principle I). [reversible:
  easy -- a future human ruling could re-scope it, but the conservative default commits nothing.]
- Q: What `## Owner` should the generic Customer domain name (siblings name a business function)?
  -> A: "Marketing / CRM and Finance (with Governance for any PII publish ruling)" -- generic
  retail functions only, no named person, no C086 specifics. [reversible: easy.]
- Q: Does adding a PII/identity owner-ruling section (absent from all 11 siblings) set a precedent
  the other domain files must follow? -> A: No -- keep it customer-only for now. Customer is the
  domain whose KPIs are PII/identity-bound; retrofitting 11 files is out of this first-step scope
  (YAGNI) and would itself be a separate human-ruled decision. [reversible: easy -- a later spec
  can generalize it.]
- Q: Which customer KPIs are listed as Planned in the KPIs table? -> A: Customer Retention Rate,
  Purchase Frequency, Customer Lifetime Value (CLV), and New-vs-Returning Customer split -- all
  Status Planned, each blocked on the unmade identity ruling; no Seeded rows. [reversible: easy --
  the list is illustrative, not a contract.]
- Q: What text replaces the INDEX `[planned]` Customer route label? -> A: Point the row at
  `domains/customer.md` with status "[seeded] -- overview; per-KPI contracts [planned]" (mirrors
  how INDEX section 3 already describes domain overviews as seeded summaries with planned deep
  contracts). [reversible: easy.]

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Customer domain has an honest, navigable overview (Priority: P1)

A KPI analyst routing through the retail-kpi-knowledge skill asks a customer question (retention,
frequency, lifetime value). Today the INDEX Customer row resolves only to a meta-reference note.
After this work, the Customer route opens a dedicated `domains/customer.md` that mirrors the 11
sibling domain files: a short summary, a KPIs table with honest Planned markers, a
decision-questions table routing only to seeded contracts or honest Planned markers, key
ambiguities, owner, and notes -- plus an explicit PII/identity owner-ruling section.

**Why this priority**: This is the entire first-step deliverable -- one generic domain-overview
file plus the two INDEX edits that resolve the route to it. Without it the customer route is the
only domain row in the router without a dedicated file.

**Independent Test**: Open the Customer route from `INDEX.md`; confirm it lands on
`domains/customer.md`; confirm every KPI and every decision-question row carries either a seeded
contract reference or an honest Planned marker (never a fabricated formula or invented contract);
confirm the PII/identity section restates the Principle-V stops verbatim and answers none of them.

**Acceptance Scenarios**:

1. **Given** the retail-kpi-knowledge skill, **When** a reader follows the INDEX Customer route,
   **Then** they reach `domains/customer.md` (no longer a `[planned]` meta-reference deferral).
2. **Given** `domains/customer.md`, **When** a reader scans the KPIs table, **Then** every KPI is
   marked Planned (none Seeded) because no customer metric contract exists, and each names the
   prerequisite ruling/field it is blocked on.
3. **Given** `domains/customer.md`, **When** a reader reaches the PII/identity section, **Then** it
   restates the Principle-V stop-and-ask points (identity/grain, PII default-drop, segment rollups)
   and decides none of them.

### User Story 2 - The router file-map and route status stay accurate (Priority: P2)

A maintainer reading `INDEX.md` sees the Customer route resolved to a seeded overview and the
file-map domain count updated from 11 to 12, so the router does not misrepresent what exists.

**Why this priority**: The router is the navigation contract; a stale count or a still-`[planned]`
route after the file lands would be a self-inconsistency.

**Independent Test**: Diff `INDEX.md`; confirm line ~59 Customer row points at
`domains/customer.md` (status seeded-as-overview), and the file-map line that read "(11 files)"
now reads "(12 files)".

**Acceptance Scenarios**:

1. **Given** `INDEX.md`, **When** the Customer route is read, **Then** it names
   `domains/customer.md` and no longer says "no dedicated domains/customer.md file yet".
2. **Given** `INDEX.md` file-map, **When** the domains line is read, **Then** the count is 12.

### Edge Cases

- A reader expects seeded customer metric contracts because the idea title says "KPI Contracts".
  The file MUST set the expectation explicitly: no customer contract is seeded; each future
  contract needs the F009 contract-template + review process AND a confirmed identity/PII ruling
  first.
- A reader tries to read a number or formula from a Planned KPI. There is none by design; the row
  is a deferred marker, not a contract (Principle VIII -- static-first, no fabricated metric).
- The C086 pharmacy worked example sits beside this content. The file MUST use only generic retail
  placeholders -- no patient identifier, no insurance/payer segment, no prescription-loyalty
  concept may leak in (Principle VII).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The deliverable MUST be exactly one new committed-text file
  `skills/retail-kpi-knowledge/domains/customer.md`, mirroring the structure of the 11 sibling
  domain files: H1 title; a 1-2 line summary; a "## KPIs in this domain" table (KPI | Contract |
  Status); a "## Decision questions this domain answers" table (Decision question | Routes to |
  Status); a "## Key ambiguities" section; a "## Owner" section; a "## Notes" section.
- **FR-002**: Every KPI row MUST carry the Status `Planned` (never `Seeded`) and name the
  prerequisite it is blocked on, because no customer metric contract exists in `contracts/`.
  Customer KPIs to list as Planned (clarified 2026-06-29): Customer Retention Rate, Purchase
  Frequency, Customer Lifetime Value (CLV), and New-vs-Returning Customer split -- each Planned and
  blocked on the unmade customer-identity ruling. The list is illustrative, not a contract.
- **FR-003**: Every Decision-questions row MUST route to a seeded contract reference OR an honest
  Planned marker -- never imply a formula and never invent a contract (the INDEX routing invariant).
- **FR-004**: The file MUST add a section (absent from the 11 siblings) that carries the
  Principle-V stop-and-ask VERBATIM for: customer identity/grain; PII publish-safety (default =
  drop, governance signs off); and business-segment rollups (analyst supplies the value->group
  table). This section states the stops and decides none of them. (Clarified 2026-06-29: this
  section stays customer-only; it does NOT retrofit the 11 sibling files -- generalizing it is a
  separate human-ruled decision, out of this first-step scope.)
- **FR-004a**: The `## Owner` section MUST name generic retail functions only -- "Marketing / CRM
  and Finance (with Governance for any PII publish ruling)" -- with no named person and no C086
  specifics (clarified 2026-06-29).
- **FR-005**: The file MUST contain NO seeded customer metric contract and MUST NOT author any file
  under `contracts/`. It MUST state that each future customer contract requires the F009
  contract-template + review process plus a confirmed PII/identity ruling first.
- **FR-006**: The file MUST stay generic retail. It MUST NOT contain any C086 / pharmacy-specific
  identifier, business segment, insurance/payer concept, or prescription-loyalty concept
  (Principle VII). Examples MUST use generic placeholders.
- **FR-007**: `INDEX.md` MUST be edited at the Customer domain route (around line 59) to resolve it
  from `[planned]` to pointing at `domains/customer.md`, with status text "[seeded] -- overview;
  per-KPI contracts [planned]" (clarified 2026-06-29; mirrors how INDEX section 3 already describes
  domain overviews as seeded summaries with planned deep contracts). The file-map line that reads
  "per-domain KPI overviews (11 files)" MUST be updated to "(12 files)".
- **FR-008**: The work MUST NOT advance or self-grant any readiness or dashboard-readiness stage,
  MUST NOT include any executor / query / live-data step, and MUST NOT emit any fabricated
  confidence or readiness score (Principles I and VIII; repo hard rule #9).
- **FR-009**: All authored text MUST be ASCII, UTF-8 without BOM (use `--` and `->`, no Unicode
  glyphs; constitution rule IX / repo encoding rule).
- **FR-010**: The four Principle-V judgment calls (identity/grain, PII publish-safety,
  business-segment rollup, product identity) MUST be left as explicit human-owner stops in the
  file and MUST NOT be answered by the authoring agent.

### Key Entities *(include if feature involves data)*

- **Customer domain overview**: the new `domains/customer.md` markdown file -- a navigation +
  reasoning artifact, not a data artifact. Attributes: summary, KPI table (all Planned),
  decision-questions table, ambiguities, owner, notes, PII/identity stop section.
- **INDEX router entries**: the Customer route row (status) and the file-map domain count -- the
  two edit points that keep the router consistent with what exists.
- **Seeded contracts (referenced, not created)**: the 10 existing non-customer contracts in
  `contracts/` -- the decision-questions table may route to these only when genuinely applicable;
  it invents none.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Following the INDEX Customer route lands on `domains/customer.md` in one hop; zero
  `[planned]`-without-file deferrals remain for the Customer domain in the router.
- **SC-002**: 100% of KPI rows and decision-question rows in `domains/customer.md` resolve to a
  seeded contract reference or an honest Planned marker; zero fabricated formulas or invented
  contracts.
- **SC-003**: Zero customer metric contract files are created under `contracts/` (the count stays
  at 10).
- **SC-004**: Zero C086 / pharmacy-specific tokens appear in `domains/customer.md` (generic-retail
  scan passes).
- **SC-005**: The `retail check` static gate exits 0 over the changed text (no new rule violation,
  no fabricated readiness/score), and the four Principle-V stops remain unanswered in the file.
- **SC-006**: The INDEX file-map domain count reads 12 and the Customer route names the new file.

## Assumptions

- The 11 sibling domain files are the authoritative template shape; `domains/inventory.md` (an
  all-Planned domain deferred on an unmade prerequisite) is the closest mirror for the customer
  case (all KPIs Planned pending the identity ruling).
- "KPI Contracts" in the idea title is aspirational; the first-step scope is ONE domain-overview
  file with Planned markers, not seeded contracts (the grounder's realist scope).
- This work advances no readiness stage (advisor-recommended ruling; carried in the front-matter
  "Readiness stage advanced: none"); it is reasoning-layer content under Principle I.
- The `[planned]` Customer route in INDEX is a deliberate by-design deferral (INDEX stop rule), not
  a broken/dangling link; this work UPGRADES it to a seeded overview, it does not repair a defect.
- No live database, no F016 Power BI Execution Adapter, and no F031-F033 spec-only runtimes are
  assumed to exist or are touched (YAGNI / static-first).
