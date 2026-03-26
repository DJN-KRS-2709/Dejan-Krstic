# systems-inventory

Create or audit a systems inventory for any domain. Discovers repos, maps dependencies, and tracks technical readiness.

## Install

```bash
claude plugin marketplace add git@ghe.spotify.net:pm-os/plugins.git
claude plugin marketplace update pm-os-plugins
claude plugin install systems-inventory@pm-os-plugins
```

## Usage

```
/systems-inventory <domain>
/systems-inventory spotify-payouts --audit
/systems-inventory spotify-payouts --repo celadon/payout
/systems-inventory spotify-payouts --check-only
```

## What It Does

Discovers and catalogs all repos and services owned by a domain's team, then assesses their technical readiness against best practices.

In **create mode** (default), discovers repos via code-search-mcp and Bandmanager, auto-detects tech stacks (Java/Apollo, Java/Spring, Python, TypeScript/React), and builds an inventory with dependency mappings. Saves to `domains/<domain>/systems/inventory.md`.

In **audit mode** (`--audit`), re-checks an existing inventory against best-practice checklists. Checks vary by stack: Java version, build system, ORM, communication patterns, quality gates, CODEOWNERS, service-info.yaml, agentic readiness (AGENTS.md, CLAUDE.md), and more. Flags gaps and rates each repo's readiness.

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `<domain>` | Yes | Domain name (e.g., spotify-payouts, booking) |
| `--audit` | No | Audit an existing inventory |
| `--repo <slug>` | No | Audit a single repo |
| `--check-only` | No | Report gaps without modifying files |

## Output

Inventory file at `domains/<domain>/systems/inventory.md` with repo catalog, tech stack, dependency map, and readiness ratings.

## Category

`core`
