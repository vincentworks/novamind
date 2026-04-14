import json
from pathlib import Path
from datetime import datetime


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

CONTACTS_PATH = DATA_DIR / "contacts.json"
GENERATED_CONTENT_PATH = DATA_DIR / "generated_content.json"
CAMPAIGN_LOG_PATH = DATA_DIR / "campaign_log.json"


def load_json(path: Path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path: Path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def extract_subject_and_body(newsletter_value):
    """
    Supports:
    1. Dict format:
       {"subject": "...", "body": "..."}
    2. Mock format:
       "Subject: Something\\n\\nBody..."
    3. OpenAI format:
       "Subject line\\nBody line 1\\nBody line 2..."
    """
    if isinstance(newsletter_value, dict):
        subject = newsletter_value.get("subject", "").strip()
        body = newsletter_value.get("body", "").strip()
        return subject, body

    if not isinstance(newsletter_value, str):
        return "Newsletter", ""

    text = newsletter_value.strip()
    if not text:
        return "Newsletter", ""

    # Case 1: explicit Subject: prefix
    if text.lower().startswith("subject:"):
        parts = text.split("\n\n", 1)
        first_part = parts[0].strip()
        body = parts[1].strip() if len(parts) > 1 else ""

        subject = first_part[len("Subject:"):].strip()
        return subject, body

    # Case 2: first line is subject, rest is body
    lines = text.splitlines()
    subject = lines[0].strip() if lines else "Newsletter"
    body = "\n".join(line.strip() for line in lines[1:] if line.strip()).strip()

    return subject, body


def build_campaign_entry(contacts, generated_content):
    newsletters = generated_content.get("newsletters", {})
    campaign_metadata = generated_content.get("campaign_metadata", {})

    campaign_id = campaign_metadata.get("campaign_id", "cmp_001")

    # Always use today's date for consistency across runs
    campaign_date = datetime.today().strftime("%Y-%m-%d")

    audience = []

    for contact in contacts:
        custom_persona = (contact.get("custom_persona") or contact.get("persona", "")).strip()
        newsletter_value = newsletters.get(custom_persona)

        if not newsletter_value:
            audience.append({
                "name": contact.get("name"),
                "email": contact.get("email"),
                "custom_persona": custom_persona,
                "status": "skipped",
                "reason": "No matching newsletter found for custom_persona"
            })
            continue

        subject, body = extract_subject_and_body(newsletter_value)

        audience.append({
            "name": contact.get("name"),
            "email": contact.get("email"),
            "custom_persona": custom_persona,
            "newsletter_subject": subject,
            "newsletter_body": body,
            "status": "ready_to_send"
        })

    return {
        "campaign_id": campaign_id,
        "campaign_date": campaign_date,
        "blog_title": generated_content.get("blog_title", ""),
        "topic": generated_content.get("topic", ""),
        "channel": "email",
        "status": "draft",
        "generation_source": generated_content.get("generation_source", "unknown"),
        "audience_count": len(audience),
        "audience": audience
    }


def main():
    contacts = load_json(CONTACTS_PATH)
    generated_content = load_json(GENERATED_CONTENT_PATH)

    campaign_entry = build_campaign_entry(contacts, generated_content)

    if CAMPAIGN_LOG_PATH.exists():
        existing = load_json(CAMPAIGN_LOG_PATH)
        if not isinstance(existing, list):
            existing = []
    else:
        existing = []

    existing.append(campaign_entry)
    save_json(CAMPAIGN_LOG_PATH, existing)

    print(f"Saved campaign log to: {CAMPAIGN_LOG_PATH}")
    print(f"Campaign ID: {campaign_entry['campaign_id']}")
    print(f"Audience count: {campaign_entry['audience_count']}")


if __name__ == "__main__":
    main()