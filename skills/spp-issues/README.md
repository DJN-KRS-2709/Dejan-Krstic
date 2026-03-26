# SPP Issues Analysis Plugin

Analyze SPP (Spotify Payouts) support tickets to identify patterns, root causes, and trends over time.

## Installation

This plugin is automatically registered in `.claude/settings.json` and ready to use.

## Prerequisites

Create `.env.local` at workspace root with your Jira credentials:

```bash
JIRA_EMAIL=your.email@spotify.com
JIRA_API_TOKEN=your_api_token_here
```

## Usage

```bash
/spp-issues                           # Use cached data if < 7 days old
/spp-issues --refresh                 # Force re-fetch from Jira
/spp-issues --since 2026-01-01        # Fetch tickets since date
/spp-issues --category "EIN/TIN Update"  # Filter analysis to category
```

## What It Does

1. Fetches SPP tickets from Jira (request types: VM/Vermilion/Amend Tax Details)
2. Categorizes issues by pattern (EIN/TIN updates, Individual↔Business changes, etc.)
3. Tracks pre/post TaxBit trends (TaxBit launch: July 20, 2025)
4. Generates SOP vs Feature recommendations
5. Updates analysis report at `domains/spotify-payouts/cs_tickets/analysis/vm_vermilion_amend_tax_analysis.md`

## Categories

Tickets are categorized using configurable pattern matching rules defined in `categories.json`.

### Predefined Categories

- **EIN/TIN Update** - Tax ID updates
- **Individual ↔ Business Change** - Entity type conversions
- **Tax Form Submission Issues** - W-8/W-9 form problems
- **Bank Account Issues** - Hyperwallet/IBAN issues
- **Payout On Hold/Disabled** - Payment suspensions
- **Other** - Uncategorized issues

### Emerging Pattern Detection

The skill analyzes the "Other" bucket to detect new patterns:

- **Similar to existing categories**: Suggests adding patterns to existing categories
- **Potential new categories**: Surfaces completely new patterns for review

The report includes actionable recommendations:
- Add patterns to existing categories in `categories.json`
- Create new categories when patterns warrant it
- Similarity scores show how closely new patterns match existing categories

### Managing Categories

Edit `.claude/plugins/spp-issues/categories.json` to:
- Add regex patterns to existing categories
- Create new categories with custom patterns
- Track when categories were created and their impact

See the command documentation (`/spp-issues --help`) for examples.

## Output

### Files Created/Updated

- `domains/spotify-payouts/cs_tickets/raw_data/spp_vm_tickets_YYYYMMDD.json` - Raw ticket data (gitignored via root .gitignore)
- `domains/spotify-payouts/cs_tickets/analysis/vm_vermilion_amend_tax_analysis_YYYYMMDD.md` - Analysis report (timestamped, history preserved)

### Console Summary

```
✓ Fetched 355 VM/Vermilion/Amend Tax tickets
✓ Analysis complete

Top Issues:
1. EIN/TIN Update: 144 tickets (40.6%), +265% post-TaxBit
2. Individual ↔ Business Change: 72 tickets (20.3%), +88% post-TaxBit
3. Other: 98 tickets (27.6%), +72% post-TaxBit

Top SOP Opportunities:
1. EIN/TIN Update Process (144 tickets) - 30-40% reduction expected
2. Individual ↔ Business Change (72 tickets) - 20-30% reduction expected

Top Feature Opportunities:
1. Self-Serve Tax Profile Corrections (144 tickets) - 60-80% reduction expected
2. Enhanced Form Validation (14 tickets) - Already improved 73% with TaxBit

Report: domains/spotify-payouts/cs_tickets/analysis/vm_vermilion_amend_tax_analysis_20260216.md
```

## Architecture

- `fetch_spp_tickets.sh` - Fetches tickets from Jira Service Desk API with pagination
- `analyze_spp_tickets.py` - Categorizes tickets and generates recommendations
- All paths are workspace-relative for portability

## Dependencies

- `bash` - For fetch script
- `curl` - For Jira API calls
- `jq` - For JSON processing
- `python3` - For analysis script (uses standard library only)
