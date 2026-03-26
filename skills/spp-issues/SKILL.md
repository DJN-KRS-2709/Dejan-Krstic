---
name: spp-issues
description: "Analyze SPP support tickets with monthly reporting, classification (SOP/Feature/Bug), and alerts"
argument-hint: "[--monthly] [--refresh] [--since <date>] [--category <name>]"
allowed-tools: ["Bash", "Read", "Write", "Glob"]
---

## Prerequisites

Before running this command, verify the following are available:

1. **curl**: Run `which curl`. If missing, install via `brew install curl`
2. **jq**: Run `which jq`. If missing, install via `brew install jq`
3. **python3**: Run `which python3`. If missing, install via `brew install python3`
4. **Jira credentials**: Ensure `JIRA_EMAIL` and `JIRA_API_TOKEN` are set in `.env.local` at the workspace root. If missing, create the file with your Jira email and an API token from https://id.atlassian.com/manage-profile/security/api-tokens

If any prerequisite is missing, walk the user through setting it up before proceeding.

# SPP Issues Analysis

Analyze SPP (Spotify Payouts) support tickets to identify patterns, root causes, and trends over time. Generate actionable recommendations for SOPs vs feature development.

## Prerequisites

Ensure `.env.local` exists at workspace root with:
- `JIRA_EMAIL` - Your Jira email
- `JIRA_API_TOKEN` - Your Jira API token

If missing, create `.env.local`:
```bash
JIRA_EMAIL=your.email@spotify.com
JIRA_API_TOKEN=your_token_here
```

## Usage

```bash
/spp-issues                           # Standard analysis (use cached data if < 7 days old)
/spp-issues --monthly                 # Monthly report with alerts and classification
/spp-issues --refresh                 # Force re-fetch from Jira
/spp-issues --since 2026-01-01        # Fetch tickets since date (custom date range)
/spp-issues --category "EIN/TIN Update"  # Filter analysis to category
```

## What This Does

1. **Fetches tickets** from Jira (SPP project, all payment-related request types: ~600 tickets in last 6 months)
   - Amend Tax Details, Other (Vermilion), Payout Not Received, Onboarding, W8/W9, Bank Details, Unsupported Tax Classification
2. **Categorizes issues** by pattern (8 categories)
3. **Classifies tickets** as SOP Opportunity, Feature Investment, System Bug, or Mixed
4. **Detects alerts** (category spikes >30% MoM, bug patterns, SLA breaches, emerging issues)
5. **Tracks trends** relative to TaxBit launch (July 20, 2025) and month-over-month
6. **Generates reports**:
   - **Standard mode**: Detailed analysis with sample tickets
   - **Monthly mode**: Executive summary (1-page) + detailed appendix

## Arguments

### `--monthly`
Generate monthly report with executive summary, alerts, and classification breakdown.
- Analyzes last 6 months of tickets (rolling window)
- Compares current month vs previous month (MoM trends)
- Generates two files:
  - `YYYY-MM-executive-summary.md` - 1-page scannable summary
  - `YYYY-MM-detailed.md` - Full analysis with sample tickets
- Saves to `domains/spotify-payouts/cs_tickets/analysis/monthly/`

### `--refresh`
Force re-fetch from Jira even if cached data exists.
Default: Use cached data if less than 7 days old.

### `--since <date>`
Fetch only tickets created since this date (YYYY-MM-DD format).
Example: `--since 2026-01-01`
Default (standard mode): Fetch from 2025-01-01
Default (monthly mode): Last 6 months (auto-calculated)

### `--category <name>`
Filter analysis to specific category.
Example: `--category "EIN/TIN Update"`
Default: Show all categories

## Instructions

### Step 1: Check Prerequisites
- Verify `.env.local` exists and contains `JIRA_EMAIL` and `JIRA_API_TOKEN`
- If missing, display clear error message with setup instructions

### Step 2: Determine Data Freshness
- Check if `domains/spotify-payouts/cs_tickets/raw_data/spp_vm_tickets_*.json` exists
- If `--refresh` flag OR no cached data OR cached data > 7 days old:
  - Run fetch script
- Else:
  - Use cached data

### Step 3: Fetch Tickets (if needed)
- Run `scripts/fetch_spp_tickets.sh`
- Pass `--since` argument if provided (defaults to 6 months ago in monthly mode)
- Script will:
  - Source `.env.local` for credentials
  - Fetch tickets with pagination
  - Filter by payment-related request types:
    - "Amend Tax Details"
    - "Other (Vermilion)"
    - "Payout Not Received"
    - "Spotify Payouts Onboarding Issue"
    - "W8 or W9 tax certification questions"
    - "Issue Updating Bank Details"
    - "Unsupported Tax Classification"
  - Save to `domains/spotify-payouts/cs_tickets/raw_data/spp_vm_tickets_YYYYMMDD.json`

### Step 4: Run Analysis
- **Standard mode**: Run `scripts/analyze_spp_tickets.py`
- **Monthly mode**: Run `scripts/analyze_spp_tickets.py --monthly`
- Pass `--category` argument if provided
- Script will:
  - Categorize all tickets (8 categories)
  - Classify each ticket as SOP/Feature/Bug/Mixed with confidence level
  - Detect alerts (spikes, bugs, SLA breaches, emerging patterns)
  - Calculate month-over-month trends (if monthly mode)
  - Generate reports

### Step 4.5: Apply Payouts Domain Context

**Domain Background:**
- Spotify Payouts pays creators globally (184 markets, €11B+ annually)
- Tax information required for IRS compliance (W-9/W-8BEN forms)
- IRS penalties up to $280 per incorrect 1099 form
- Fraud risk: payment redirection via identity changes

**Red Flags (Cannot Self-Serve - Always Manual CS):**
- 🚫 **Country changes** → Changes tax jurisdiction, tax form type (W-9 vs W-8BEN)
- 🚫 **Individual ↔ Business changes** → Changes 1099 type (MISC vs NEC), entity structure
- 🚫 **Identity changes** → Fraud risk, IRS accuracy requirements, audit trail needed

**Potential for Controlled Automation (Requires Guardrails):**
- TIN typo corrections (with validation, fraud checks, thresholds)
- Bank account updates (no tax implications, fraud monitoring needed)
- Form validation improvements (prevent errors at submission)
- Pre-flight checks (catch issues before onboarding complete)

**Interpretation Rules:**

When analyzing categories, consider:

1. **SOP Opportunities:** Manual processes needing standardization
   - Focus: Clear approval criteria, decision trees, documentation
   - Target: Faster approvals + deflection via better guidance
   - Realistic reduction: 15-30%

2. **Feature Opportunities (Deflection):** UX preventing ticket creation
   - Validation, error messages, clear requirements at onboarding
   - Pre-flight checks before locking identity fields
   - Realistic reduction: 20-40%

3. **Feature Opportunities (Controlled Self-Serve):** Low-risk with guardrails
   - Identify changes that COULD be automated with proper controls
   - Flag required guardrails: thresholds, rate limits, fraud checks, audit trail
   - Be explicit about trade-offs and risks
   - Realistic reduction: 30-60% (depends on guardrails)

4. **Feature Opportunities (Safe Automation):** No compliance blockers
   - Bank accounts, payment methods, non-tax fields
   - Realistic reduction: 40-70%

5. **Disregarded Entity & Partnerships:** Platform gap — not self-serve fixable
   - These represent entity types the platform doesn't support yet (DRE, LLP, general/limited partnerships)
   - Creators with these classifications cannot complete onboarding or monetize
   - Rising volume = creators blocked from monetizing = revenue/growth risk
   - Action: Track volume trend; if growing, escalate as a platform gap to product/engineering
   - These tickets cannot be reduced by SOP or UX improvements — they require platform support for new entity types

**For each recommendation, explicitly state:**
- Why this is/isn't a red flag
- What guardrails would be needed for automation
- What compliance constraints exist
- Realistic reduction range with reasoning

### Step 5: Generate Domain-Aware Report
- **Standard mode**:
  - Create markdown report with categorization and classification
  - Apply compliance-aware recommendation templates
  - Flag constraints explicitly in each recommendation
  - Write to `domains/spotify-payouts/cs_tickets/analysis/spp_analysis_YYYYMMDD.md`
- **Monthly mode**:
  - Create executive summary (1-page) with top issues, SOP/Feature/Bug tables, alerts
  - Create detailed appendix with sample tickets
  - Write to `domains/spotify-payouts/cs_tickets/analysis/monthly/YYYY-MM-executive-summary.md` and `YYYY-MM-detailed.md`

### Step 6: Display Summary
- **Standard mode**: Show summary to user:
  - Total tickets analyzed
  - Top 5 issues by volume
  - Pre/post TaxBit trends
  - SOP recommendations with compliance constraints
  - Feature recommendations with required guardrails
- **Monthly mode**: Show monthly summary:
  - Total tickets and MoM change
  - Number of alerts detected (with emoji indicators)
  - Link to executive summary and detailed reports

## Output

### Files Created/Updated
- `domains/spotify-payouts/cs_tickets/raw_data/spp_vm_tickets_YYYYMMDD.json` - Raw ticket data (gitignored)
- `domains/spotify-payouts/cs_tickets/analysis/vm_vermilion_amend_tax_analysis_YYYYMMDD.md` - Analysis report (timestamped, history preserved)

### Console Output
```
✓ Fetched 355 VM/Vermilion/Amend Tax tickets
✓ Analysis complete

Top Issues:
1. EIN/TIN Update: 144 tickets (40.6%), +265% post-TaxBit
2. Individual ↔ Business Change: 72 tickets (20.3%), +88% post-TaxBit
3. Other: 98 tickets (27.6%), +72% post-TaxBit

Report with domain-aware recommendations: domains/spotify-payouts/cs_tickets/analysis/vm_vermilion_amend_tax_analysis_20260216.md
```

## Error Handling

### Missing Credentials
```
Error: JIRA credentials not found in .env.local

Please create .env.local at workspace root with:
JIRA_EMAIL=your.email@spotify.com
JIRA_API_TOKEN=your_token_here
```

### Jira API Errors
Display error message and suggest checking credentials or network.

### No Tickets Found
```
No tickets match criteria. Try:
- --since with earlier date
- --refresh to re-fetch from Jira
```

### Missing Dependencies
```
Error: Python 3 required. Install from python.org
Error: curl required. Install via Homebrew: brew install curl
Error: jq required. Install via Homebrew: brew install jq
```

## Categories

Tickets are categorized using pattern matching rules defined in `.claude/plugins/spp-issues/categories.json`.

### Current Categories

- **EIN/TIN Update**: Tax ID updates and corrections
- **Individual ↔ Business Change**: Entity type conversions
- **Tax Form Submission Issues**: W-8/W-9 form submission problems
- **Bank Account Issues**: Payment method and account setup issues
- **Payout On Hold/Disabled**: Payment suspensions and holds
- **Tax Country Change**: Requests to change tax residence country
- **Disregarded Entity & Partnerships**: Creators with DRE or Partnership tax classifications unable to onboard or monetize (NEW in v1.2.0)
- **Tax Cert Stuck/In Review**: Tax certification stuck in review state
- **Other**: Uncategorized tickets (analyzed for emerging patterns)

Each category now includes classification indicators:
- `sop_indicators`: Patterns suggesting manual process standardization opportunity
- `feature_indicators`: Patterns suggesting UX/validation improvements needed
- `bug_indicators`: Patterns suggesting system bugs (route to engineering)

### Emerging Pattern Detection

The skill automatically analyzes the "Other" bucket to detect new patterns:

1. **Similar to Existing Categories**: Patterns that match existing categories are flagged for addition
2. **Potential New Categories**: Completely new patterns are surfaced for review

When patterns are detected, the report includes:
- Frequency and percentage of "Other" tickets
- Sample tickets showing the pattern
- Suggested actions (add to existing category or create new)
- Similarity scores to existing categories

### Updating Categories

To add patterns or create new categories:

1. Edit `.claude/plugins/spp-issues/categories.json`
2. Add regex patterns to existing categories OR create new category with patterns
3. Run `/spp-issues --refresh` to re-analyze with new categories

**Example: Adding a pattern to existing category**
```json
{
  "EIN/TIN Update": {
    "patterns": [
      "\\bein\\b",
      "\\btin\\b",
      "tax.*id",
      "federal.*tax.*id"  // <- Add new pattern
    ]
  }
}
```

**Example: Creating a new category**
```json
{
  "Address Update Issues": {
    "description": "Artist address change requests",
    "patterns": [
      "change.*address",
      "update.*address",
      "wrong.*address"
    ],
    "created": "2026-02-16",
    "ticket_count_when_created": 0
  }
}
```

## Data Storage

- **Raw data**: `domains/spotify-payouts/cs_tickets/raw_data/spp_vm_tickets_*.json` (gitignored)
- **Analysis**: `domains/spotify-payouts/cs_tickets/analysis/vm_vermilion_amend_tax_analysis.md` (tracked)

## Monthly Analysis Features (v1.1.0)

### Secondary Classification System

Each ticket is automatically classified based on content patterns:

- **SOP Opportunity**: Manual process that can be standardized and handed to CS
  - Indicators: "manual review", "L3 escalation", "approval needed", "fraud check"
  - Action: Document decision trees, standardize approval criteria
  - Expected reduction: 15-40%

- **Feature Investment**: Product/UX changes needed to reduce ticket volume
  - Indicators: "confusing", "no option for", "unclear", "can't find", "wrong form type"
  - Action: Improve UX, add validation, better error messages
  - Expected reduction: 40-80%

- **System Bug**: Technical issue requiring engineering fix
  - Indicators: "stuck", "not working", "state mismatch", "submitted twice", "pop-up persists"
  - Action: Create engineering ticket, do NOT route to CS
  - Priority: High (user-impacting)

- **Mixed**: Category contains both SOP and Feature opportunities
  - Example: "Tax Profile Updates" might need approval SOP (40%) AND self-serve UX (40%)
  - Action: Split into two recommendations with separate reduction estimates

Each classification includes confidence level (high/medium/low).

### Alert System

Four alert types detect issues automatically:

1. **Category Spike** (>30% MoM growth)
   - Severity: High if >100% growth, Medium if 30-100%
   - Action: Investigate root cause, consider escalating to product/engineering
   - Example: "Tax Cert Stuck/In Review grew 375% MoM (8 → 38 tickets)"

2. **Bug Pattern Detection** (>5 tickets with bug indicators)
   - Severity: High
   - Action: Create engineering ticket immediately
   - Example: "14 tickets mention 'stuck in review' with valid submissions"

3. **SLA Breach Risk** (median ticket age increased >50%)
   - Severity: Medium
   - Action: Check manual review queue capacity
   - Example: "Tax Cert Stuck tickets staying open 3x longer than average (7d → 21d)"

4. **Emerging Pattern in Other** (>3 similar tickets in uncategorized bucket)
   - Severity: Low
   - Action: Review and update category taxonomy
   - Example: "'payout schedule' appears in 5 uncategorized tickets"

### Month-over-Month Trends

Monthly reports compare current month vs previous month:
- Ticket volume changes per category
- New categories appearing
- Categories disappearing or declining
- Fastest-growing issues (sorted by absolute change)

### Executive Summary Format

The 1-page monthly summary includes:
- **Top 3 Issues** with classification, impact, and recommended action
- **SOP Opportunities Table** (hand to CS)
- **Feature Investments Table** (add to product roadmap)
- **System Bugs Table** (route to engineering)
- **Alerts Section** with sample tickets and actions
- **MoM Trends Table** showing volume changes

## Portability

This skill works for any user who:
1. Clones the repo
2. Creates `.env.local` with Jira credentials
3. Adds `"spp-issues@local": true` to `.claude/settings.json`

All paths are workspace-relative using `git rev-parse --show-toplevel`.
