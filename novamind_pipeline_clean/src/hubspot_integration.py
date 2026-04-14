import json
import os
from pathlib import Path

import requests
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

CONTACTS_PATH = DATA_DIR / "contacts.json"
GENERATED_CONTENT_PATH = DATA_DIR / "generated_content.json"
HUBSPOT_PAYLOADS_PATH = DATA_DIR / "hubspot_payloads.json"

load_dotenv()

HUBSPOT_TOKEN = os.getenv("HUBSPOT_PRIVATE_APP_TOKEN")
HUBSPOT_BASE_URL = "https://api.hubapi.com"


def load_json(path: Path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path: Path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def get_headers():
    if not HUBSPOT_TOKEN:
        raise ValueError("Missing HUBSPOT_PRIVATE_APP_TOKEN in .env")
    return {
        "Authorization": f"Bearer {HUBSPOT_TOKEN}",
        "Content-Type": "application/json"
    }


def split_name(full_name: str):
    parts = full_name.strip().split()
    if len(parts) == 0:
        return "", ""
    if len(parts) == 1:
        return parts[0], ""
    return parts[0], " ".join(parts[1:])


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

    if text.lower().startswith("subject:"):
        parts = text.split("\n\n", 1)
        first_part = parts[0].strip()
        body = parts[1].strip() if len(parts) > 1 else ""
        subject = first_part[len("Subject:"):].strip()
        return subject, body

    lines = text.splitlines()
    subject = lines[0].strip() if lines else "Newsletter"
    body = "\n".join(line.strip() for line in lines[1:] if line.strip()).strip()
    return subject, body


def build_contact_upsert_payload(contacts):
    inputs = []

    for contact in contacts:
        first, last = split_name(contact.get("name", ""))
        custom_persona = (contact.get("custom_persona") or contact.get("persona", "")).strip()

        inputs.append({
            "id": contact["email"],
            "idProperty": "email",
            "properties": {
                "email": contact["email"],
                "firstname": first,
                "lastname": last,
                "custom_persona": custom_persona
            }
        })

    return {"inputs": inputs}


def upsert_contacts_to_hubspot(payload):
    url = f"{HUBSPOT_BASE_URL}/crm/v3/objects/contacts/batch/upsert"
    response = requests.post(url, headers=get_headers(), json=payload, timeout=30)
    return response


def build_mock_send_payloads(contacts, generated_content):
    newsletters = generated_content.get("newsletters", {})
    campaign = generated_content.get("campaign_metadata", {})
    blog_title = generated_content.get("blog_title", "")
    campaign_id = campaign.get("campaign_id", "cmp_001")
    campaign_date = campaign.get("campaign_date", "")

    send_payloads = []

    for contact in contacts:
        custom_persona = (contact.get("custom_persona") or contact.get("persona", "")).strip()
        newsletter = newsletters.get(custom_persona, "")

        subject, body = extract_subject_and_body(newsletter)

        send_payloads.append({
            "recipient_email": contact["email"],
            "custom_persona": custom_persona,
            "hubspot_single_send_payload": {
                "emailId": 123456789,
                "message": {
                    "to": contact["email"]
                },
                "contactProperties": {
                    "custom_persona": custom_persona
                },
                "customProperties": {
                    "blog_title": blog_title,
                    "campaign_id": campaign_id,
                    "campaign_date": campaign_date,
                    "newsletter_subject": subject,
                    "newsletter_body": body
                }
            }
        })

    return send_payloads


def main():
    contacts = load_json(CONTACTS_PATH)
    generated_content = load_json(GENERATED_CONTENT_PATH)

    print("Building HubSpot contact upsert payload...")
    contact_payload = build_contact_upsert_payload(contacts)

    print("Sending contacts to HubSpot...")
    response = upsert_contacts_to_hubspot(contact_payload)

    print(f"HubSpot status code: {response.status_code}")
    try:
        response_json = response.json()
    except Exception:
        response_json = {"raw_text": response.text}

    print("HubSpot response:")
    print(json.dumps(response_json, indent=2))

    print("Writing mocked newsletter-send payloads...")
    send_payloads = build_mock_send_payloads(contacts, generated_content)

    output = {
        "contact_upsert_request": contact_payload,
        "contact_upsert_response": response_json,
        "mock_single_send_requests": send_payloads
    }

    save_json(HUBSPOT_PAYLOADS_PATH, output)
    print(f"Saved mocked HubSpot payloads to: {HUBSPOT_PAYLOADS_PATH}")


if __name__ == "__main__":
    main()