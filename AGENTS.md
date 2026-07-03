# revenue-optimizer — AGENTS.md

## Overview
Multi-channel revenue optimization engine — scans 6 channels (affiliate, content, SEO, competitor, email, social), scores opportunities by ROI impact/effort, generates week-by-week action plans, and simulates 6-month revenue impact. Pure Python stdlib, no external deps. MIT licensed.

## Quick Start
```bash
# Generate demo data
python main.py generate-data

# Scan all channels for opportunities
python main.py scan

# Scan specific channel
python main.py scan --channel affiliate

# Generate monthly optimization plan
python main.py plan

# Generate reports (console/json/csv/all)
python main.py report --format all --output ./output

# Simulate revenue impact
python main.py simulate --top 10
```

## Commands
| Command | Description |
|---------|-------------|
| `scan` | Scan channels for optimization opportunities |
| `plan` | Generate week-by-week monthly optimization plan |
| `report` | Generate reports (console/json/csv/all) |
| `simulate` | Simulate revenue impact of optimizations |
| `generate-data` | Generate synthetic demo data |

## Options
| Option | Description |
|--------|-------------|
| `--channel/-c` | Specific channel: affiliate, content, seo, email, social, competitor |
| `--format/-f` | Report format: console, json, csv, all |
| `--output/-o` | Output directory for reports |
| `--top/-n` | Number of top opportunities to show |
| `--data-dir` | Directory containing CSV data files |

## Development
```bash
# Install dev dependencies (pytest, ruff)
pip install pytest ruff

# Run tests
python -m pytest tests/ -v --tb=short

# Lint
ruff check .

# CI runs: Python 3.10, 3.11, 3.12, 3.13
```

## CI/CD
- GitHub Actions: `.github/workflows/ci.yml` (lint + test matrix)

## Structure
```
revenue-optimizer/
├── main.py              # CLI entry point (argparse)
├── optimizer.py         # Core engine: scanning, scoring, planning, simulation
├── channels.py          # 6 channel analyzers (Affiliate, Content, SEO, Competitor, Email, Social)
├── reporter.py          # Output generation (console, JSON, CSV)
├── data_generator.py    # Synthetic demo data generator
├── data_models.py       # Shared data models and enums
├── requirements.txt     # (empty - pure stdlib)
├── data/                # Input CSV files (gitignored)
├── output/              # Generated reports (gitignored)
└── tests/               # pytest tests
```

## Channel Analyzers
Each channel class in `channels.py` implements:
- `analyze(data)` → returns `List[Opportunity]`
- Opportunity: `channel`, `title`, `description`, `impact_score`, `effort_score`, `roi_score`, `metadata`

### AffiliateChannelAnalyzer
- EPC analysis, conversion rate optimization, under-monetized affiliates

### ContentChannelAnalyzer
- Unmonetized high-traffic pages, high bounce pages, stale content

### SEOChannelAnalyzer
- Page 2 keywords, low CTR high impressions, high CPC keywords

### CompetitorChannelAnalyzer
- Backlink gaps, content gaps, weak rankings

### EmailChannelAnalyzer
- Open rate, CTR, unsubscribe rate, revenue per subscriber

### SocialChannelAnalyzer
- Engagement rate, CTR, platform-specific recommendations

## Data Format
CSV files in `data/` directory (gitignored):
- `affiliate_performance.csv`: date, affiliate_id, affiliate_name, niche, clicks, conversions, conversion_rate, epc, revenue, commission
- `content_performance.csv`: date, page_id, page_title, content_type, sessions, bounce_rate, avg_time_min, monetized, revenue
- `seo_performance.csv`: date, keyword, position, impressions, clicks, ctr, search_volume, cpc
- `email_performance.csv`: date, list_id, list_name, subscribers, open_rate, click_rate, unsub_rate, revenue
- `competitor_metrics.csv`: date, competitor_id, competitor_name, domain, est_traffic, domain_authority, backlinks, content_pieces, avg_position
- `social_performance.csv`: date, platform_id, platform_name, followers, posts, impressions, engagements, clicks, revenue

## Integration
Complements:
- **revenue-forecaster** — baseline projections
- **affiliate-funnel-optimizer** — funnel bottlenecks
- **affiliate-dashboard** — live tracking data
- **competitor-analysis** — real-time monitoring
- **content-pipeline** — publishing workflow

Replace synthetic data with CSV exports from these tools for production use.

## License
MIT