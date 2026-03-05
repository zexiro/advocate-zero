"""
RevenueCat REST API v2 client for Advocate Zero.

Provides programmatic access to RevenueCat's platform for:
- Querying subscription metrics and analytics
- Managing customers and entitlements
- Listing offerings and products
- Feeding data into the agent's content and growth pipelines
"""

from dataclasses import dataclass
from typing import Any

import httpx


@dataclass
class RevenueCatConfig:
    api_key: str       # Secret API key (v2)
    project_id: str
    base_url: str = "https://api.revenuecat.com/v2"


class RevenueCatClient:
    """Async client for RevenueCat's REST API v2."""

    def __init__(self, config: RevenueCatConfig):
        self.config = config
        self.http = httpx.AsyncClient(
            base_url=config.base_url,
            headers={
                "Authorization": f"Bearer {config.api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            timeout=30.0,
        )

    async def get_project(self) -> dict[str, Any]:
        """Get project details."""
        resp = await self.http.get(f"/projects/{self.config.project_id}")
        resp.raise_for_status()
        return resp.json()

    async def list_offerings(self) -> list[dict[str, Any]]:
        """List all offerings for the project."""
        resp = await self.http.get(
            f"/projects/{self.config.project_id}/offerings"
        )
        resp.raise_for_status()
        return resp.json().get("items", [])

    async def get_offering(self, offering_id: str) -> dict[str, Any]:
        """Get a specific offering with its packages."""
        resp = await self.http.get(
            f"/projects/{self.config.project_id}/offerings/{offering_id}"
        )
        resp.raise_for_status()
        return resp.json()

    async def list_entitlements(self) -> list[dict[str, Any]]:
        """List all entitlements for the project."""
        resp = await self.http.get(
            f"/projects/{self.config.project_id}/entitlements"
        )
        resp.raise_for_status()
        return resp.json().get("items", [])

    async def get_customer(self, customer_id: str) -> dict[str, Any]:
        """Get customer info including active entitlements and subscriptions."""
        resp = await self.http.get(
            f"/projects/{self.config.project_id}/customers/{customer_id}"
        )
        resp.raise_for_status()
        return resp.json()

    async def list_customers(
        self, limit: int = 20, starting_after: str | None = None
    ) -> dict[str, Any]:
        """List customers with pagination."""
        params: dict[str, Any] = {"limit": limit}
        if starting_after:
            params["starting_after"] = starting_after
        resp = await self.http.get(
            f"/projects/{self.config.project_id}/customers",
            params=params,
        )
        resp.raise_for_status()
        return resp.json()

    async def get_charts_metrics(
        self,
        metric: str,
        start_date: str,
        end_date: str,
        granularity: str = "day",
    ) -> dict[str, Any]:
        """
        Fetch analytics from RevenueCat Charts.

        Metrics: mrr, revenue, active_subscriptions, new_subscriptions,
                 churn, trial_conversion, refund_rate, arpu, arppu, etc.
        """
        resp = await self.http.get(
            f"/projects/{self.config.project_id}/metrics/{metric}",
            params={
                "start_date": start_date,
                "end_date": end_date,
                "granularity": granularity,
            },
        )
        resp.raise_for_status()
        return resp.json()

    async def list_products(self) -> list[dict[str, Any]]:
        """List all products configured in the project."""
        resp = await self.http.get(
            f"/projects/{self.config.project_id}/products"
        )
        resp.raise_for_status()
        return resp.json().get("items", [])

    async def close(self):
        """Close the HTTP client."""
        await self.http.aclose()
