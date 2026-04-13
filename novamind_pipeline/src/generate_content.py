from __future__ import annotations

import argparse
import json
import os
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


def generate_mock_content(topic: str, personas: list[str]) -> dict[str, Any]:
    blog_title = f"How {topic.title()} Is Reshaping Creative Agency Workflows"
    blog_outline = [
        "The growing pressure on agency teams to do more with less",
        f"How {topic.lower()} helps reduce repetitive coordination work",
        "Three practical agency use cases for AI-powered automation",
        "Common implementation mistakes and how to avoid them",
        "What teams should measure after adoption",
    ]

    blog_draft = (
        f"Creative agencies are under constant pressure to move faster without sacrificing quality. "
        f"That is exactly why {topic.lower()} is becoming more relevant. Rather than replacing creative work, "
        f"AI tools are helping teams reduce the manual tasks that slow down execution, such as project updates, "
        f"asset routing, meeting notes, and repetitive client communication. This gives strategists, designers, "
        f"and account teams more time to focus on higher-value work.\n\n"
        "One of the clearest benefits is workflow visibility. When teams use AI to summarize tasks, extract next steps, "
        "and connect tools across the stack, fewer things fall through the cracks. For a growing agency, this matters "
        "because operational drag often increases before headcount does. Automation can help preserve speed without "
        "forcing managers to micromanage every project.\n\n"
        "There are also strong marketing benefits. Agencies can use AI to repurpose one piece of thought leadership into "
        "multiple formats, including blog posts, newsletters, social copy, and client-facing summaries. That means a "
        "single insight can reach different audiences with less manual rewriting. In practice, this improves consistency "
        "while reducing production time.\n\n"
        "Still, teams should be realistic. AI content and workflow automation perform best when paired with clear review "
        "steps, well-defined brand guidance, and a strong understanding of audience needs. The goal is not to automate "
        "everything, but to automate the repeatable parts of work so people can focus on judgment, relationships, and "
        "creative direction.\n\n"
        "For agencies considering adoption, the most important next step is to start small and measure outcomes. Teams "
        "should track cycle time, content engagement, and internal efficiency to see where automation is actually helping. "
        "Done well, AI can become less of a novelty and more of a practical growth lever."
    )

    newsletters = {
        "Creative Agency Founder": (
            f"Subject: A smarter way to scale {topic.lower()}\n\n"
            "As agency leaders look for ways to grow without adding unnecessary overhead, AI-powered automation is becoming "
            "a practical advantage. This week’s blog breaks down how agencies can reduce repetitive work, move faster, and "
            "free up teams for higher-value creative decisions."
        ),
        "Operations Manager": (
            f"Subject: How to streamline operations with {topic.lower()}\n\n"
            "If your team is juggling deadlines, approvals, and scattered tools, this week’s blog is for you. We look at "
            "how AI can support routing, coordination, and workflow visibility so projects move with fewer bottlenecks."
        ),
        "Marketing Lead": (
            f"Subject: Turn one idea into more campaign output\n\n"
            "This week’s post explores how AI can help marketing teams repurpose one idea across blog, email, and other "
            "channels. It is a useful look at how to increase output while keeping messaging focused and relevant."
        ),
    }

    filtered_newsletters = {persona: newsletters.get(persona, "") for persona in personas}

    return {
        "topic": topic,
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
        "You are a growth marketing assistant for NovaMind, an AI startup serving small creative agencies. "
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
- campaign_id should be 'cmp_001'
- status should be 'draft'
- campaign_date should be today's date
"""

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )

    text = response.output_text
    data = json.loads(text)
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
