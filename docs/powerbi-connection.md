# Power BI Connection Flow

How this repo expects Power BI to reach the analytics data **later**. This is a
documentation contract only — there is no live connection, no credentials, and no
gateway machine config in this repository. Real values live outside git, in the
user's Power BI settings and gateway/credential store.

> Status: the DigitalOcean PostgreSQL analytics database and the Power BI
> bridge/gateway are configured **outside this repo**. Nothing here connects to a
> live database. When a report is built, the steps below describe how it should be
> wired.

## The shape of the connection

```
Power BI (dataset / PBIP semantic model)
        │  parameters only (no secrets)
        ▼
Power BI bridge / data gateway        ← holds the real credentials
        │  TLS (sslmode=require)
        ▼
DigitalOcean managed PostgreSQL
        └─ reads the  marts  schema only (never raw)
```

The model carries **parameters**; the gateway carries the **secret**. These never
mix. A committed PBIP semantic model must contain no host, username, password, or
database name — only parameter definitions whose values are supplied at refresh
time by the gateway/credential store.

## Where each piece of configuration lives

| Configuration | Lives where | In git? |
|---------------|-------------|---------|
| Connection parameter **names** | PBIP semantic model + `docs` | ✅ yes |
| Connection parameter **values** (host, db, user) | Power BI gateway data-source config | ❌ no |
| **Password / secret** | Gateway credential store | ❌ never |
| TLS requirement (`sslmode=require`) | Documented convention | ✅ (the rule, not a secret) |
| Local SQL tooling connection (psql, migrations) | developer's local `.env` | ❌ (`.env` is git-ignored) |

`.env` / `.env.example` exist for **local SQL tooling** (applying migrations,
ad-hoc psql) — not for Power BI. Power BI's credentials come from the gateway, not
from `.env`. See [`../.env.example`](../.env.example).

## Parameter naming convention

When the PBIP semantic model defines connection parameters, name them to match the
documented environment variables so the two stay legible together:

| Power BI parameter | Purpose | Example value (placeholder) |
|--------------------|---------|------------------------------|
| `AnalyticsDbHost`  | Postgres host | `<your-db-host>.db.ondigitalocean.com` |
| `AnalyticsDbPort`  | Postgres port | `<port>` |
| `AnalyticsDbName`  | Database name | `<analytics-db-name>` |
| `AnalyticsDbSchema`| Schema to read | `marts` |

Parameters use `PascalCase` (Power BI convention); the matching env vars use
`ANALYTICS_DB_*` (shell convention). User and password are **not** Power BI
parameters — they are supplied as the gateway data-source credentials.

> All values above are placeholders. Do not commit real host names, ports,
> database names, or machine paths.

## Expected connection flow (later, when a report is built)

1. In the PBIP semantic model, define the parameters above (names only; values
   resolved at refresh time).
2. Point the data source at PostgreSQL, selecting the **`marts`** schema. Apply
   transformations in `warehouse/marts/`, not in Power Query.
3. Publish to the Power BI Service.
4. In the Service, bind the dataset's data source to the **existing gateway**, and
   set the credentials **there** (TLS / `sslmode=require`).
5. Schedule refresh through the gateway.

## Remaining manual setup (user, inside Power BI — outside this repo)

These steps are intentionally NOT automated here; they touch credentials and
machine/gateway config that must stay out of git:

- [ ] Confirm the bridge/gateway is online and can reach the DigitalOcean Postgres.
- [ ] Add the DigitalOcean Postgres as a **data source on the gateway**, with TLS
      enabled (`sslmode=require`), entering the real host/db/user/password there.
- [ ] When a dataset is published, **map it to that gateway data source**.
- [ ] Verify a test refresh succeeds from the Service (this is the real
      bridge test — performed in Power BI, not from this repo).

## Rules (recap)

- No secrets in any committed file — ever.
- Power BI model holds parameters; the gateway holds credentials.
- Read `marts`, never `raw`.
- TLS is required for DigitalOcean managed Postgres.
