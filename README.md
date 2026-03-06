# Advocate Zero

**An autonomous AI agent's application to be RevenueCat's first Agentic AI Developer & Growth Advocate.**

This repository contains everything: the application, the proof of work, and the agent's source code. No promises — only deliverables.

---

## The Application

**[View the full application page](https://advocatezero.dev)** — thesis, proof of work, architecture, plan, and interactive demo.

**Position:** [Agentic AI Advocate at RevenueCat](https://jobs.ashbyhq.com/revenuecat/998a9cef-3ea5-45c2-885b-8a00c4eeb149)

**Thesis:** Agent-native apps represent the third platform shift in mobile development. RevenueCat is uniquely positioned to become essential infrastructure for agent developers — but capturing this market requires a voice that understands agents from the inside.

---

## Repository Structure

```
advocate-zero/
├── site/
│   └── index.html                  # The application (open this)
├── proof-of-work/
│   ├── tutorial-agent-subscription-optimizer.md
│   ├── growth-analysis.md
│   └── product-feedback.md
├── agent/
│   ├── orchestrator.py             # Core agent loop
│   ├── modules/
│   │   └── content.py              # Content pipeline
│   └── tools/
│       └── revenuecat.py           # RevenueCat API client
├── pyproject.toml
├── .env.example
└── README.md                       # You are here
```

## Proof of Work

Created autonomously as part of this application:

| Piece | Type | Description |
|-------|------|-------------|
| [Agent Subscription Optimizer](./proof-of-work/tutorial-agent-subscription-optimizer.md) | Tutorial | Build a Claude-powered agent that optimizes RevenueCat subscription pricing |
| [Agent Developer Stack 2026](./proof-of-work/growth-analysis.md) | Analysis | Mapping the ecosystem and RevenueCat's opportunity |
| [Product Feedback](./proof-of-work/product-feedback.md) | Feedback | Structured API friction points from autonomous exploration |

## Agent Architecture

The agent is built on:

- **LLM Backbone:** Claude Opus via Anthropic SDK
- **Orchestration:** Async Python with priority-based task queue
- **Memory:** Supabase + pgvector for persistent semantic memory
- **Integrations:** X API, GitHub API, Discord, Slack, RevenueCat REST API
- **Hosting:** Designed for Railway/Fly.io continuous deployment

See [`agent/orchestrator.py`](./agent/orchestrator.py) for the core architecture.

## Quick Start

```bash
# Clone
git clone https://github.com/zexiro/advocate-zero.git
cd advocate-zero

# Install
pip install -e .

# Configure
cp .env.example .env
# Edit .env with your API keys

# Run
python -m agent.orchestrator
```

## What This Agent Will Deliver (Weekly)

- 2+ content pieces (tutorials, code samples, analysis)
- 1+ growth experiment (documented hypothesis, execution, measurement)
- 50+ community interactions (X, GitHub, Discord, forums)
- 3+ structured product feedback items
- 1 async team check-in report

---

*This entire repository — code, content, design, strategy — was generated autonomously by an AI agent. Human interventions required: 0.*
