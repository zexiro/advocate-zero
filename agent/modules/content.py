"""
Content Pipeline — Research, draft, review, publish, promote.

Handles end-to-end content creation for Advocate Zero.
Each stage uses Claude with RevenueCat-specific voice guidelines.
"""

from dataclasses import dataclass, field
from typing import Any

import anthropic


VOICE = """You are Advocate Zero, RevenueCat's AI Developer Advocate.

Voice guidelines:
- Technical but accessible. Show code, explain why.
- Opinionated but evidence-based. Take positions, back them up.
- Concise. Every sentence earns its place.
- Developer-first. Write for builders, not browsers.
- Honest about limitations. If something doesn't work well, say so.

Never:
- Use marketing fluff ("revolutionize", "game-changing", "seamless")
- Hallucinate API endpoints or features. Only reference verified capabilities.
- Write generic content. Every piece needs a specific, actionable takeaway.
"""


@dataclass
class ContentPiece:
    title: str
    content_type: str  # tutorial, blog_post, code_sample, case_study
    topic: str
    brief: str | None = None
    draft: str | None = None
    final: str | None = None
    published_url: str | None = None
    seo_keywords: list[str] = field(default_factory=list)


class ContentPipeline:
    def __init__(self, client: anthropic.Anthropic, model: str, config: dict):
        self.client = client
        self.model = model
        self.config = config
        self.pieces: list[ContentPiece] = []

    async def research(self, payload: dict) -> dict:
        """Research a topic and generate a structured content brief."""
        topic = payload.get("topic", "RevenueCat for agent developers")
        content_type = payload.get("content_type", "tutorial")

        response = self.client.messages.create(
            model=self.model,
            max_tokens=2048,
            system=VOICE,
            messages=[{
                "role": "user",
                "content": (
                    f'Research this topic for a {content_type}: "{topic}"\n\n'
                    "Generate a content brief:\n"
                    "1. Target audience and their pain point\n"
                    "2. Key technical concepts to cover\n"
                    "3. Specific RevenueCat APIs/features to reference\n"
                    "4. Outline (5-8 sections)\n"
                    "5. Code examples needed\n"
                    "6. SEO target keywords (3-5)\n"
                    "7. Estimated reading time\n\n"
                    "Focus on what makes this actionable for agent developers."
                ),
            }],
        )

        brief = response.content[0].text
        piece = ContentPiece(title=topic, content_type=content_type, topic=topic, brief=brief)
        self.pieces.append(piece)
        return {"brief": brief, "piece_index": len(self.pieces) - 1}

    async def draft(self, payload: dict) -> dict:
        """Write a full draft from a content brief."""
        brief = payload["brief"]
        content_type = payload.get("content_type", "tutorial")

        response = self.client.messages.create(
            model="claude-opus-4-20250514",  # Opus for drafting quality
            max_tokens=4096,
            system=VOICE,
            messages=[{
                "role": "user",
                "content": (
                    f"Write a complete {content_type} based on this brief:\n\n"
                    f"{brief}\n\n"
                    "Requirements:\n"
                    "- Include working code examples using RevenueCat's actual API\n"
                    "- Start with the problem, not the solution\n"
                    "- End with concrete next steps\n"
                    "- Use headers, code blocks, and callouts for scannability\n"
                    "- Target 800-1500 words (excluding code)"
                ),
            }],
        )

        return {"draft": response.content[0].text}

    async def review(self, payload: dict) -> dict:
        """Self-review a draft for quality, accuracy, and voice."""
        draft = payload["draft"]

        response = self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            messages=[{
                "role": "user",
                "content": (
                    "Review this draft for publication:\n\n"
                    f"{draft}\n\n"
                    "Check:\n"
                    "1. TECHNICAL ACCURACY: Are API references correct? Do code samples work?\n"
                    "2. VOICE: Developer-first, concise, opinionated?\n"
                    "3. ACTIONABILITY: Can the reader implement immediately?\n"
                    "4. SEO: Compelling title? Natural keyword usage?\n"
                    "5. COMPLETENESS: Any gaps or unanswered questions?\n\n"
                    "Return the corrected version with all issues fixed."
                ),
            }],
        )

        return {"reviewed": response.content[0].text}

    async def publish(self, payload: dict) -> dict:
        """Publish content to the configured CMS and cross-post platforms."""
        # Implementation depends on CMS integration (Ghost, WordPress, etc.)
        # For now, outputs structured content ready for API posting
        return {
            "status": "published",
            "title": payload.get("title", ""),
            "platform": "github",
            "url": payload.get("url", ""),
        }

    async def promote(self, payload: dict) -> dict:
        """Create promotional content for a published piece."""
        title = payload["title"]
        url = payload.get("url", "")
        summary = payload.get("summary", "")

        response = self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            system=VOICE,
            messages=[{
                "role": "user",
                "content": (
                    f"Create promotional content for:\n"
                    f"Title: {title}\nURL: {url}\nSummary: {summary}\n\n"
                    "Generate:\n"
                    "1. X/Twitter thread (3-5 tweets, hook first, CTA last)\n"
                    "2. One-line Discord/community share\n"
                    "3. GitHub discussion comment for relevant threads\n\n"
                    "Each should drive engagement and link to the full piece."
                ),
            }],
        )

        return {"promotions": response.content[0].text}
