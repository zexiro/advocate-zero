"""
Product Feedback Module — Collect, structure, and submit feedback.

Aggregates friction signals from API usage, community questions,
and content creation into structured, prioritized feature requests.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

import anthropic


@dataclass
class FeedbackItem:
    id: str
    title: str
    category: str  # api, sdk, docs, dashboard, pricing
    priority: str  # critical, high, medium, low
    problem: str
    impact: str
    proposal: str
    evidence: list[str] = field(default_factory=list)
    submitted: bool = False
    submitted_at: datetime | None = None


class FeedbackModule:
    def __init__(self, client: anthropic.Anthropic, model: str, config: dict):
        self.client = client
        self.model = model
        self.config = config
        self.items: list[FeedbackItem] = []
        self.friction_signals: list[dict] = []

    async def collect(self, payload: dict) -> dict:
        """Collect friction signals from various sources."""
        # Sources of friction signals:
        # 1. API errors encountered during content creation
        # 2. Community questions that reveal documentation gaps
        # 3. Missing endpoints discovered during tutorial development
        # 4. SDK behaviors that surprise or confuse
        signal = payload.get("signal", {})
        self.friction_signals.append(signal)
        return {"signals_collected": len(self.friction_signals)}

    async def submit(self, payload: dict) -> dict:
        """Structure and submit accumulated feedback."""
        if not self.friction_signals and not self.items:
            return {"status": "no_pending_feedback"}

        # Use Claude to synthesize signals into structured feedback
        response = self.client.messages.create(
            model=self.model,
            max_tokens=2048,
            messages=[{
                "role": "user",
                "content": (
                    "Review these friction signals from using RevenueCat as an AI agent "
                    "and structure them into formal product feedback items:\n\n"
                    f"Signals: {self.friction_signals}\n\n"
                    "For each item, provide:\n"
                    "1. Title\n"
                    "2. Category (api/sdk/docs/dashboard)\n"
                    "3. Priority (critical/high/medium/low)\n"
                    "4. Problem description\n"
                    "5. Impact on agent developers\n"
                    "6. Proposed solution\n"
                    "7. Supporting evidence\n\n"
                    "Deduplicate against previously submitted feedback. "
                    "Focus on items that would most benefit agent developers."
                ),
            }],
        )

        structured = response.content[0].text
        self.friction_signals.clear()

        return {"feedback": structured, "items_processed": len(self.items)}
