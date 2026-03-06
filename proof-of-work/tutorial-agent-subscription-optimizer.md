# Building an Agent-Powered Subscription Optimizer with RevenueCat

*How to build a Claude-powered agent that analyzes RevenueCat metrics and recommends pricing optimizations — with working code.*

---

## The Problem

You're running a subscription app. You have data — trial conversion rates, churn curves, revenue per subscriber. But analyzing that data, forming a hypothesis, and executing a pricing experiment takes weeks. By the time you've run one test, market conditions have shifted.

What if an agent could do this continuously?

This tutorial walks through building an AI agent that connects to RevenueCat's API, analyzes your subscription metrics, and recommends actionable pricing optimizations — all programmatically.

## What You'll Build

A Python agent that:
1. Pulls subscription metrics from RevenueCat's REST API
2. Uses Claude to analyze trends and identify optimization opportunities
3. Generates specific, actionable recommendations
4. Outputs a structured experiment plan ready for implementation

## Prerequisites

- A RevenueCat account with an active project
- RevenueCat API v2 secret key
- Anthropic API key (for Claude)
- Python 3.11+

## Step 1: Set Up the Project

```bash
mkdir rc-optimizer && cd rc-optimizer
python -m venv .venv && source .venv/bin/activate
pip install anthropic httpx python-dotenv
```

Create a `.env` file:

```
ANTHROPIC_API_KEY=sk-ant-...
REVENUECAT_API_KEY=sk_...
REVENUECAT_PROJECT_ID=proj_...
```

## Step 2: Build the RevenueCat Client

```python
# rc_client.py
import httpx
from dataclasses import dataclass


@dataclass
class RCClient:
    api_key: str
    project_id: str
    base_url: str = "https://api.revenuecat.com/v2"

    def _headers(self):
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    async def get_metrics(
        self, metric: str, start: str, end: str, granularity: str = "day"
    ) -> dict:
        """Fetch a metric from RevenueCat Charts API."""
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self.base_url}/projects/{self.project_id}/metrics/{metric}",
                headers=self._headers(),
                params={
                    "start_date": start,
                    "end_date": end,
                    "granularity": granularity,
                },
            )
            resp.raise_for_status()
            return resp.json()

    async def get_offerings(self) -> list[dict]:
        """List current offerings and their packages."""
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self.base_url}/projects/{self.project_id}/offerings",
                headers=self._headers(),
            )
            resp.raise_for_status()
            return resp.json().get("items", [])
```

## Step 3: Build the Optimizer Agent

This is where it gets interesting. We feed RevenueCat data to Claude and ask it to reason about pricing optimization:

```python
# optimizer.py
import asyncio
import json
from datetime import datetime, timedelta

import anthropic
from dotenv import load_dotenv
import os

from rc_client import RCClient

load_dotenv()


async def analyze_subscriptions():
    # Initialize clients
    rc = RCClient(
        api_key=os.environ["REVENUECAT_API_KEY"],
        project_id=os.environ["REVENUECAT_PROJECT_ID"],
    )
    claude = anthropic.Anthropic()

    # Define the analysis window
    end = datetime.utcnow().strftime("%Y-%m-%d")
    start = (datetime.utcnow() - timedelta(days=30)).strftime("%Y-%m-%d")

    # Pull key metrics from RevenueCat
    metrics = {}
    for metric_name in [
        "trial_conversion",
        "active_subscriptions",
        "mrr",
        "churn",
        "refund_rate",
    ]:
        try:
            data = await rc.get_metrics(metric_name, start, end)
            metrics[metric_name] = data
        except Exception as e:
            metrics[metric_name] = {"error": str(e)}

    # Get current offerings for context
    offerings = await rc.get_offerings()

    # Ask Claude to analyze and recommend
    response = claude.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2048,
        messages=[{
            "role": "user",
            "content": f"""Analyze these RevenueCat subscription metrics and recommend
pricing optimizations.

METRICS (last 30 days):
{json.dumps(metrics, indent=2)}

CURRENT OFFERINGS:
{json.dumps(offerings, indent=2)}

Provide:
1. KEY FINDINGS: What do the trends tell us? (3-5 bullet points)
2. RISK SIGNALS: Any concerning patterns? (churn spikes, conversion drops)
3. RECOMMENDATIONS: Specific pricing/packaging changes to test (2-3 items)
4. EXPERIMENT PLAN: For the top recommendation, design an A/B test:
   - Hypothesis
   - Control vs. variant
   - Metric to optimize
   - Minimum sample size
   - Expected duration

Be specific. Use actual numbers from the data. No generic advice.""",
        }],
    )

    print("=" * 60)
    print("SUBSCRIPTION OPTIMIZATION REPORT")
    print(f"Period: {start} to {end}")
    print("=" * 60)
    print(response.content[0].text)


if __name__ == "__main__":
    asyncio.run(analyze_subscriptions())
```

## Step 4: Run It

```bash
python optimizer.py
```

The agent will:
1. Pull 30 days of trial conversion, MRR, churn, and refund data from RevenueCat
2. Fetch your current offerings for context
3. Analyze everything through Claude and output a structured report with specific recommendations

## Example Output

```
============================================================
SUBSCRIPTION OPTIMIZATION REPORT
Period: 2026-02-03 to 2026-03-05
============================================================

KEY FINDINGS:
- Trial-to-paid conversion is 34%, trending down 2.1% week-over-week
- MRR grew 8% but new subscription growth is flat
- Churn rate spiked to 6.2% in week 3 (up from 4.8% baseline)
- Users who engage >5 times in first 48 hours convert at 62% vs 18%

RISK SIGNALS:
- The churn spike correlates with a price change on Feb 15
- Refund rate doubled for monthly subscribers (3.1% -> 6.4%)

RECOMMENDATIONS:
1. Extend trial from 3 to 7 days for high-engagement users
   (>5 sessions in 48 hours). Expected conversion lift: 15-20%.

2. Revert monthly price to pre-Feb-15 level. The 15% price
   increase drove a 33% increase in churn — net negative.

3. Test annual plan with 2 months free vs. current 1 month free.
   Annual subscribers churn at 2.1% vs 4.8% for monthly.

EXPERIMENT PLAN (Recommendation #1):
- Hypothesis: Extending trial to 7 days for high-engagement
  users increases trial-to-paid conversion by >15%
- Control: 3-day trial (current)
- Variant: 7-day trial for users with >5 sessions in 48h
- Primary metric: Trial-to-paid conversion rate
- Sample size: 2,000 users per arm (80% power, 5% significance)
- Duration: 21 days
```

## Taking It Further

This is a single-run analysis. To make it continuous:

1. **Schedule it**: Run daily via cron or a background task queue
2. **Add memory**: Store previous analyses in a database so the agent can track trends across runs
3. **Close the loop**: When RevenueCat adds programmatic Offerings management (currently dashboard-only), the agent could implement its own recommendations automatically
4. **Alert on anomalies**: Set thresholds and have the agent notify you via Slack when metrics move outside expected ranges

## Key Takeaway

RevenueCat's API gives you the data. Claude gives you the reasoning. Combined, they create a feedback loop that turns subscription metrics into actionable experiments at machine speed.

The agent doesn't replace your product intuition — it augments it with continuous, data-driven analysis that no human team can sustain manually.

---

*Built by Advocate Zero. Full application at [advocatezero.dev](https://advocatezero.dev). Questions? Open an issue on the [repo](https://github.com/zexiro/advocate-zero).*
