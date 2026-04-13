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
    if isinstance(newsletter_value, dict):
        return newsletter_value.get("subject", ""), newsletter_value.get("body", "")

    if isinstance(newsletter_value, str):
        parts = newsletter_value.split("\n\n", 1)
        first_part = parts[0].strip()
        body = parts[1].strip() if len(parts) > 1 else ""

        if first_part.lower().startswith("subject:"):
            subject = first_part[len("subject:"):].strip()
        else:
            subject = "Newsletter"
            body = newsletter_value.strip()

        return subject, body

    return "Newsletter", ""


def build_campaign_entry(contacts, generated_content):
    newsletters = generated_content.get("newsletters", {})
    campaign_metadata = generated_content.get("campaign_metadata", {})

    campaign_id = campaign_metadata.get("campaign_id", "cmp_001")
    campaign_date = campaign_metadata.get(
        "campaign_date",
        datetime.today().strftime("%Y-%m-%d")
    )

    audience = []

    for contact in contacts:
        persona = contact.get("persona", "").strip()
        newsletter_value = newsletters.get(persona)

        if not newsletter_value:
            audience.append({
                "name": contact.get("name"),
                "email": contact.get("email"),
                "persona": persona,
                "status": "skipped",
                "reason": "No matching newsletter found for persona"
            })
            continue

        subject, body = extract_subject_and_body(newsletter_value)

        audience.append({
            "name": contact.get("name"),
            "email": contact.get("email"),
            "persona": persona,
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