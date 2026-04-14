from __future__ import annotations

import argparse
import json
import os
import re
from datetime import date
from pathlib import Path
from typing import Any

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

DEFAULT_PERSONAS = [
    "Creative Agency Founder",
    "Operations Manager",
    "Marketing Lead",
]

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
OUTPUT_PATH = DATA_DIR / "generated_content.json"


def load_environment() -> None:
    if load_dotenv:
        load_dotenv()


def normalize_ai_capitalization(value: str) -> str:
    return re.sub(r"\bai\b", "AI", value, flags=re.IGNORECASE)


def format_topic_for_title(topic: str) -> str:
    return topic.replace("AI", "Ai").title().replace("Ai", "AI")


def generate_mock_content(topic: str, personas: list[str]) -> dict[str, Any]:
    formatted_topic = format_topic_for_title(topic)
    normalized_topic = normalize_ai_capitalization(topic)

    blog_title = f"How {formatted_topic} Is Transforming Modern Workflows"

    blog_outline = [
        "The growing pressure on teams to do more with less",
        f"How {normalized_topic.lower()} helps reduce repetitive coordination work",
        "Three practical use cases for AI-powered automation",
        "Common implementation mistakes and how to avoid them",
        "What teams should measure after adoption",
    ]

    blog_draft = (
        f"Teams across industries are under constant pressure to move faster without sacrificing quality. "
        f"That is exactly why {normalized_topic} is becoming more relevant. Rather than replacing high-value work, "
        f"AI tools are helping teams reduce the manual tasks that slow down execution, such as project updates, "
        f"task routing, meeting notes, and repetitive communication. This gives employees more time to focus on "
        f"judgment, collaboration, and strategic work.\n\n"
        "One of the clearest benefits is workflow visibility. When teams use AI to summarize tasks, extract next steps, "
        "and connect tools across the stack, fewer things fall through the cracks. For growing organizations, this matters "
        "because operational drag often increases before headcount does. Automation can help preserve speed without "
        "forcing managers to micromanage every process.\n\n"
        "There are also strong content and communication benefits. Organizations can use AI to repurpose one insight into "
        "multiple formats, including blog posts, newsletters, internal updates, and external summaries. That means a "
        "single idea can reach different audiences with less manual rewriting. In practice, this improves consistency "
        "while reducing production time.\n\n"
        "Still, teams should be realistic. AI content and workflow automation perform best when paired with clear review "
        "steps, well-defined brand or communication guidance, and a strong understanding of audience needs. The goal is "
        "not to automate everything, but to automate the repeatable parts of work so people can focus on what requires "
        "context and judgment.\n\n"
        "For teams considering adoption, the most important next step is to start small and measure outcomes. Teams should "
        "track cycle time, engagement, and internal efficiency to see where automation is actually helping. Done well, AI "
        "can become less of a novelty and more of a practical growth lever."
    )

    newsletters = {
        "Creative Agency Founder": (
            f"Subject: A smarter way to scale {normalized_topic}\n\n"
            "As agency leaders look for ways to grow without adding unnecessary overhead, AI-powered automation is becoming "
            "a practical advantage. This week’s blog breaks down how teams can reduce repetitive work, move faster, and "
            "free up time for higher-value creative decisions."
        ),
        "Operations Manager": (
            f"Subject: How to streamline operations with {normalized_topic}\n\n"
            "If your team is juggling deadlines, approvals, and scattered tools, this week’s blog is for you. We look at "
            "how AI can support routing, coordination, and workflow visibility so projects move with fewer bottlenecks."
        ),
        "Marketing Lead": (
            "Subject: Turn one idea into more campaign output\n\n"
            "This week’s post explores how AI can help marketing teams repurpose one idea across blog, email, and other "
            "channels. It is a useful look at how to increase output while keeping messaging focused and relevant."
        ),
    }

    filtered_newsletters = {
        persona: normalize_ai_capitalization(newsletters.get(persona, ""))
        for persona in personas
    }

    blog_title = normalize_ai_capitalization(blog_title)
    blog_outline = [normalize_ai_capitalization(item) for item in blog_outline]
    blog_draft = normalize_ai_capitalization(blog_draft)

    return {
        "topic": normalized_topic,
        "personas": personas,
        "blog_title": blog_title,
        "blog_outline": blog_outline,
        "blog_draft": blog_draft,
        "newsletters": filtered_newsletters,
        "campaign_metadata": {
            "campaign_id": "cmp_001",
            "campaign_date": str(date.today()),
            "status": "draft",
        },
    }


def generate_with_openai(topic: str, personas: list[str]) -> dict[str, Any]:
    from openai import OpenAI

    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

    system_prompt = (
        "You are a growth marketing assistant for NovaMind, an AI startup. "
        "Return only valid JSON."
    )

    user_prompt = f"""
Generate a JSON object with the following keys:
- topic
- personas
- blog_title
- blog_outline (5 bullets)
- blog_draft (400-600 words)
- newsletters (object with one short newsletter for each persona)
- campaign_metadata (campaign_id, campaign_date, status)

Topic: {topic}
Personas: {personas}

Requirements:
- Blog should be clear, practical, and written for a startup marketing audience.
- Each newsletter should reflect the persona's priorities.
- campaign_id should be "cmp_001"
- status should be "draft"
- campaign_date should be today's date
- Return ONLY valid JSON with no markdown fences
"""

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )

    text = response.output_text
    print("DEBUG output_text:", repr(text))

    if not text or not text.strip():
        raise ValueError("OpenAI returned empty output_text")

    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        raise ValueError(f"Invalid JSON from OpenAI: {text}")

    # Normalize a few fields for consistency
    if "topic" in data and isinstance(data["topic"], str):
        data["topic"] = normalize_ai_capitalization(data["topic"])

    if "blog_title" in data and isinstance(data["blog_title"], str):
        data["blog_title"] = normalize_ai_capitalization(data["blog_title"])

    if "blog_outline" in data and isinstance(data["blog_outline"], list):
        data["blog_outline"] = [
            normalize_ai_capitalization(item) if isinstance(item, str) else item
            for item in data["blog_outline"]
        ]

    if "blog_draft" in data and isinstance(data["blog_draft"], str):
        data["blog_draft"] = normalize_ai_capitalization(data["blog_draft"])

    if "newsletters" in data and isinstance(data["newsletters"], dict):
        data["newsletters"] = {
            key: normalize_ai_capitalization(value) if isinstance(value, str) else value
            for key, value in data["newsletters"].items()
        }

    return data


def save_output(payload: dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate blog and newsletter content for NovaMind.")
    parser.add_argument("--topic", required=True, help="Main content topic.")
    parser.add_argument(
        "--personas",
        nargs="*",
        default=DEFAULT_PERSONAS,
        help="Optional list of target personas.",
    )
    return parser.parse_args()


def main() -> None:
    load_environment()
    args = parse_args()

    api_key = os.environ.get("OPENAI_API_KEY")
    if api_key:
        try:
            payload = generate_with_openai(args.topic, args.personas)
            source = "openai"
        except Exception as exc:
            print(f"OpenAI generation failed, falling back to mock content: {exc}")
            payload = generate_mock_content(args.topic, args.personas)
            source = "mock_fallback"
    else:
        payload = generate_mock_content(args.topic, args.personas)
        source = "mock"

    payload["generation_source"] = source
    save_output(payload, OUTPUT_PATH)

    print(f"Saved generated content to: {OUTPUT_PATH}")
    print(f"Generation source: {source}")
    print(f"Blog title: {payload['blog_title']}")


if __name__ == "__main__":
    main()