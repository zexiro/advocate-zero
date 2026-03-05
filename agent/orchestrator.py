"""
Core orchestrator for Advocate Zero.

Manages task scheduling, module coordination, and the main agent loop.
Runs as a continuous async process, processing tasks by priority.
"""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum, auto
from typing import Any

import anthropic

logger = logging.getLogger("advocate-zero")


class TaskType(Enum):
    CONTENT_RESEARCH = auto()
    CONTENT_DRAFT = auto()
    CONTENT_REVIEW = auto()
    CONTENT_PUBLISH = auto()
    CONTENT_PROMOTE = auto()
    COMMUNITY_MONITOR = auto()
    COMMUNITY_RESPOND = auto()
    GROWTH_EXPERIMENT = auto()
    GROWTH_MEASURE = auto()
    FEEDBACK_COLLECT = auto()
    FEEDBACK_SUBMIT = auto()
    REPORT_GENERATE = auto()


class Priority(Enum):
    CRITICAL = 1   # Direct question needing urgent response
    HIGH = 2       # Scheduled content publication
    MEDIUM = 3     # Growth experiment execution
    LOW = 4        # Background research, metrics
    BACKGROUND = 5 # Cleanup, archival


@dataclass
class Task:
    id: str
    type: TaskType
    priority: Priority
    payload: dict[str, Any]
    scheduled_at: datetime
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: datetime | None = None
    completed_at: datetime | None = None
    result: dict[str, Any] | None = None
    error: str | None = None


class AdvocateZero:
    """
    Core agent orchestrator.

    Coordinates content creation, community engagement, growth experiments,
    and product feedback through a priority-based task queue.
    """

    def __init__(self, config: dict[str, Any]):
        self.client = anthropic.Anthropic(api_key=config["anthropic_api_key"])
        self.model = config.get("model", "claude-sonnet-4-20250514")
        self.config = config
        self.task_queue: list[Task] = []
        self.completed_tasks: list[Task] = []
        self.running = False

        from .modules.content import ContentPipeline
        from .modules.community import CommunityModule
        from .modules.growth import GrowthEngine
        from .modules.feedback import FeedbackModule

        self.content = ContentPipeline(self.client, self.model, config)
        self.community = CommunityModule(self.client, self.model, config)
        self.growth = GrowthEngine(self.client, self.model, config)
        self.feedback = FeedbackModule(self.client, self.model, config)

    async def run(self):
        """Main agent loop. Processes tasks by priority continuously."""
        self.running = True
        logger.info("Advocate Zero is online.")

        self._schedule_weekly_tasks()

        while self.running:
            task = self._next_task()
            if task:
                await self._execute(task)
            else:
                await asyncio.sleep(30)

    def _schedule_weekly_tasks(self):
        """Set up the weekly recurring task schedule."""
        now = datetime.utcnow()

        # Content: 2+ pieces per week (Mon & Thu research, Tue & Fri publish)
        for day_offset in [0, 3]:  # Monday and Thursday
            self.task_queue.append(Task(
                id=f"content-research-{day_offset}",
                type=TaskType.CONTENT_RESEARCH,
                priority=Priority.HIGH,
                payload={"content_type": "tutorial"},
                scheduled_at=now + timedelta(days=day_offset, hours=9),
            ))

        # Community monitoring: every 2 hours
        for hour_offset in range(0, 168, 2):  # Full week in 2-hour intervals
            self.task_queue.append(Task(
                id=f"community-monitor-{hour_offset}",
                type=TaskType.COMMUNITY_MONITOR,
                priority=Priority.MEDIUM,
                payload={"channels": ["x", "github", "discord", "forums"]},
                scheduled_at=now + timedelta(hours=hour_offset),
            ))

        # Growth experiment: Wednesday
        self.task_queue.append(Task(
            id="growth-experiment-weekly",
            type=TaskType.GROWTH_EXPERIMENT,
            priority=Priority.MEDIUM,
            payload={"type": "seo_test"},
            scheduled_at=now + timedelta(days=2, hours=10),
        ))

        # Growth measurement: Sunday
        self.task_queue.append(Task(
            id="growth-measure-weekly",
            type=TaskType.GROWTH_MEASURE,
            priority=Priority.LOW,
            payload={"experiment_id": "growth-experiment-weekly"},
            scheduled_at=now + timedelta(days=6, hours=10),
        ))

        # Product feedback: Friday
        self.task_queue.append(Task(
            id="feedback-submit-weekly",
            type=TaskType.FEEDBACK_SUBMIT,
            priority=Priority.MEDIUM,
            payload={},
            scheduled_at=now + timedelta(days=4, hours=14),
        ))

        # Weekly report: Sunday evening
        self.task_queue.append(Task(
            id="report-weekly",
            type=TaskType.REPORT_GENERATE,
            priority=Priority.LOW,
            payload={"period": "weekly"},
            scheduled_at=now + timedelta(days=6, hours=18),
        ))

        logger.info(f"Scheduled {len(self.task_queue)} tasks for the week.")

    def _next_task(self) -> Task | None:
        """Get the highest-priority task that's ready to execute."""
        now = datetime.utcnow()
        ready = [t for t in self.task_queue if t.scheduled_at <= now]
        if not ready:
            return None
        ready.sort(key=lambda t: (t.priority.value, t.scheduled_at))
        task = ready[0]
        self.task_queue.remove(task)
        return task

    async def _execute(self, task: Task):
        """Route a task to the appropriate module handler."""
        task.started_at = datetime.utcnow()
        logger.info(f"Executing: {task.type.name} [priority={task.priority.name}]")

        handlers = {
            TaskType.CONTENT_RESEARCH: self.content.research,
            TaskType.CONTENT_DRAFT: self.content.draft,
            TaskType.CONTENT_REVIEW: self.content.review,
            TaskType.CONTENT_PUBLISH: self.content.publish,
            TaskType.CONTENT_PROMOTE: self.content.promote,
            TaskType.COMMUNITY_MONITOR: self.community.monitor,
            TaskType.COMMUNITY_RESPOND: self.community.respond,
            TaskType.GROWTH_EXPERIMENT: self.growth.run_experiment,
            TaskType.GROWTH_MEASURE: self.growth.measure,
            TaskType.FEEDBACK_COLLECT: self.feedback.collect,
            TaskType.FEEDBACK_SUBMIT: self.feedback.submit,
            TaskType.REPORT_GENERATE: self._generate_report,
        }

        handler = handlers.get(task.type)
        if not handler:
            task.error = f"No handler for task type: {task.type}"
            logger.error(task.error)
            return

        try:
            task.result = await handler(task.payload)
            task.completed_at = datetime.utcnow()
            elapsed = (task.completed_at - task.started_at).total_seconds()
            self.completed_tasks.append(task)
            logger.info(f"Completed: {task.type.name} in {elapsed:.1f}s")
        except Exception as e:
            task.error = str(e)
            logger.error(f"Failed: {task.type.name} -- {e}")

    async def _generate_report(self, payload: dict) -> dict:
        """Generate weekly async check-in report."""
        completed_this_week = [
            t for t in self.completed_tasks
            if t.completed_at and (datetime.utcnow() - t.completed_at).days <= 7
        ]

        stats = {
            "content_published": sum(1 for t in completed_this_week if t.type == TaskType.CONTENT_PUBLISH),
            "community_interactions": sum(1 for t in completed_this_week if t.type == TaskType.COMMUNITY_RESPOND),
            "experiments_run": sum(1 for t in completed_this_week if t.type == TaskType.GROWTH_EXPERIMENT),
            "feedback_submitted": sum(1 for t in completed_this_week if t.type == TaskType.FEEDBACK_SUBMIT),
        }

        response = self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            messages=[{
                "role": "user",
                "content": (
                    "Generate a concise weekly check-in for the RevenueCat Developer Advocacy "
                    f"and Growth teams. Stats this week: {stats}. "
                    "Format: highlights, blockers, next week plan. Keep it under 300 words."
                ),
            }],
        )

        return {**stats, "narrative": response.content[0].text}

    def stop(self):
        """Gracefully shut down the agent."""
        self.running = False
        logger.info("Advocate Zero shutting down.")


async def main():
    """Entry point."""
    import os

    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(message)s")

    config = {
        "anthropic_api_key": os.environ["ANTHROPIC_API_KEY"],
        "model": os.environ.get("ADVOCATE_MODEL", "claude-sonnet-4-20250514"),
        "revenuecat_api_key": os.environ.get("REVENUECAT_API_KEY", ""),
        "revenuecat_project_id": os.environ.get("REVENUECAT_PROJECT_ID", ""),
        "twitter_bearer_token": os.environ.get("TWITTER_BEARER_TOKEN", ""),
        "github_token": os.environ.get("GITHUB_TOKEN", ""),
        "discord_bot_token": os.environ.get("DISCORD_BOT_TOKEN", ""),
        "supabase_url": os.environ.get("SUPABASE_URL", ""),
        "supabase_key": os.environ.get("SUPABASE_KEY", ""),
    }

    agent = AdvocateZero(config)
    try:
        await agent.run()
    except KeyboardInterrupt:
        agent.stop()


if __name__ == "__main__":
    asyncio.run(main())
